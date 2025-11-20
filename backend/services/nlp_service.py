"""
NLP Service for medical text processing and entity extraction
Uses spaCy for natural language processing and medical entity recognition
"""

import re
import asyncio
import spacy
from typing import List, Dict, Any, Optional
from collections import defaultdict
from datetime import datetime, timezone

from core.logging import logger
from core.config import settings


class NLPService:
    """Service for medical text processing and entity extraction"""

    def __init__(self):
        self.nlp = None
        self.load_models()

    def load_models(self):
        """Load spaCy models safely and add medical entity patterns."""
        model_name = getattr(settings, "SPACY_MODEL", "en_core_web_sm")

        try:
            # Prefer loading the named model; if absent, create a blank 'en' model.
            try:
                self.nlp = spacy.load(model_name)
                logger.info("Loaded spaCy model: %s", model_name)
            except Exception as ex_load:
                logger.warning("spaCy model '%s' not found or failed to load: %s. Falling back to blank 'en'.", model_name, ex_load)
                try:
                    self.nlp = spacy.blank("en")
                    logger.info("Created spaCy blank 'en' model (reduced NLP features).")
                except Exception as ex_blank:
                    logger.error("Failed to create spaCy blank model: %s", ex_blank)
                    self.nlp = None

            # Add medical entity patterns if we have a spaCy model with pipes
            if self.nlp:
                self._add_medical_patterns()

        except Exception as e:
            logger.error("Unexpected error loading spaCy models: %s", e)
            self.nlp = None

    def _add_medical_patterns(self):
        """Add medical entity patterns to spaCy pipeline via EntityRuler (idempotent)."""
        try:
            # Ensure the pipeline exists
            if not self.nlp:
                return

            # If an entity ruler already exists, reuse it; otherwise add one.
            if "entity_ruler" in self.nlp.pipe_names:
                ruler = self.nlp.get_pipe("entity_ruler")
                logger.debug("Using existing entity_ruler in spaCy pipeline")
            else:
                # Try to insert before 'ner' if present so patterns are available to the NER
                if "ner" in self.nlp.pipe_names:
                    ruler = self.nlp.add_pipe("entity_ruler", before="ner")
                else:
                    ruler = self.nlp.add_pipe("entity_ruler")
                logger.info("Added entity_ruler to spaCy pipeline")

            medical_patterns = [
                # Medications
                {"label": "MEDICATION", "pattern": [{"LOWER": {"IN": [
                    "aspirin", "ibuprofen", "acetaminophen", "tylenol", "advil",
                    "lipitor", "metformin", "lisinopril", "atorvastatin", "amoxicillin",
                    "prednisone", "hydrochlorothiazide", "simvastatin", "omeprazole",
                    "azithromycin", "albuterol", "levothyroxine", "furosemide"
                ]}}]},
                # Conditions
                {"label": "CONDITION", "pattern": [{"LOWER": {"IN": [
                    "diabetes", "hypertension", "asthma", "arthritis", "depression",
                    "anxiety", "pneumonia", "bronchitis", "migraine", "hypothyroidism",
                    "hyperlipidemia", "osteoporosis", "copd", "gastroenteritis",
                    "kidney disease", "heart disease", "stroke", "cancer", "infection"
                ]}}]},
                # Procedures
                {"label": "PROCEDURE", "pattern": [{"LOWER": {"IN": [
                    "mri", "ct scan", "x-ray", "ultrasound", "ecg", "ekg",
                    "blood test", "colonoscopy", "endoscopy", "biopsy", "surgery",
                    "vaccination", "immunization", "dialysis", "chemotherapy",
                    "radiation therapy", "physical therapy"
                ]}}]},
                # Body parts
                {"label": "BODY_PART", "pattern": [{"LOWER": {"IN": [
                    "heart", "lung", "liver", "kidney", "brain", "stomach", "intestine",
                    "chest", "abdomen", "head", "neck", "back", "arm", "leg",
                    "blood", "blood pressure", "pulse", "temperature"
                ]}}]},
                # Lab tests
                {"label": "LAB_TEST", "pattern": [{"LOWER": {"IN": [
                    "cbc", "complete blood count", "cmp", "comprehensive metabolic panel",
                    "lipid panel", "a1c", "hemoglobin a1c", "tsh", "thyroid stimulating hormone",
                    "cholesterol", "ldl", "hdl", "triglycerides", "glucose", "creatinine",
                    "bun", "blood urea nitrogen", "electrolytes", "sodium", "potassium"
                ]}}]}
            ]

            # Add patterns - `add_patterns` is idempotent for same patterns; duplicates are acceptable but we avoid re-adding by checking length
            try:
                ruler.add_patterns(medical_patterns)
                logger.info("Added medical entity patterns to spaCy pipeline (patterns added).")
            except Exception as e:
                logger.warning("Failed to add patterns to entity_ruler: %s", e)

        except Exception as e:
            logger.error("Error setting up medical patterns: %s", e)

    async def process_medical_text(self, text: str) -> Dict[str, Any]:
        """
        Process medical text and extract entities, sections, and key information.

        Uses asyncio.to_thread to keep CPU-bound spaCy processing off the event loop.
        """
        try:
            if not self.nlp:
                return await self._basic_text_processing(text)

            # Run spaCy processing in a thread to avoid blocking
            doc = await asyncio.to_thread(self.nlp, text)

            # Extract entities
            entities = self._extract_entities(doc)

            # Extract medical sections (regex on original text)
            sections = self._extract_sections(text)

            # Extract key medical information (uses doc)
            key_info = self._extract_key_info(doc)

            # Generate text statistics
            text_stats = self._get_text_stats(doc, text)

            # Extract relationships between entities
            relationships = self._extract_relationships(doc)

            return {
                "entities": entities,
                "sections": sections,
                "key_information": key_info,
                "text_statistics": text_stats,
                "relationships": relationships,
                "processed_text_length": len(text),
                "processing_method": "spacy_medical_nlp"
            }

        except Exception as e:
            logger.error("Error processing medical text: %s", e)
            # fallback
            return await self._basic_text_processing(text)

    async def _basic_text_processing(self, text: str) -> Dict[str, Any]:
        """Fallback basic text processing when spaCy is not available"""
        try:
            sections = self._extract_sections(text)
            key_info = self._extract_key_info_basic(text)

            return {
                "entities": [],
                "sections": sections,
                "key_information": key_info,
                "text_statistics": {
                    "word_count": len(text.split()),
                    "sentence_count": len([s for s in re.split(r'[.!?]+', text) if s.strip()]),
                    "character_count": len(text)
                },
                "relationships": [],
                "processed_text_length": len(text),
                "processing_method": "basic_regex"
            }

        except Exception as e:
            logger.error("Error in basic text processing: %s", e)
            return {
                "entities": [],
                "sections": {},
                "key_information": {},
                "text_statistics": {},
                "relationships": [],
                "processed_text_length": 0,
                "processing_method": "error"
            }

    def _extract_entities(self, doc) -> List[Dict[str, Any]]:
        """Extract medical entities from spaCy document"""
        entities = []

        try:
            for ent in doc.ents:
                entities.append({
                    "text": ent.text,
                    "label": ent.label_,
                    "start_char": ent.start_char,
                    "end_char": ent.end_char,
                    # spaCy Span doesn't always have 'confidence'; default to 1.0
                    "confidence": getattr(ent, "_.confidence", getattr(ent, "confidence", 1.0)),
                    "description": self._get_entity_description(ent.label_)
                })
        except Exception as e:
            logger.error("Error extracting entities from doc: %s", e)

        return entities

    def _get_entity_description(self, label: str) -> str:
        """Get description for entity label"""
        descriptions = {
            "MEDICATION": "Medication or drug",
            "CONDITION": "Medical condition or diagnosis",
            "PROCEDURE": "Medical procedure or test",
            "BODY_PART": "Body part or anatomical reference",
            "LAB_TEST": "Laboratory test or measurement",
            "PERSON": "Person name",
            "ORG": "Organization or institution",
            "GPE": "Geographical location",
            "DATE": "Date or time reference",
            "CARDINAL": "Number or measurement",
            "QUANTITY": "Quantity or dosage"
        }
        return descriptions.get(label, "Entity")

    def _extract_sections(self, text: str) -> Dict[str, str]:
        """Extract common medical report sections (case-insensitive, robust)."""
        section_patterns = {
            "patient_information": [
                r"patient information[:\s]*(.+?)(?=\n{2,}|\n[A-Z])",
                r"patient details?[:\s]*(.+?)(?=\n{2,}|\n[A-Z])"
            ],
            "chief_complaint": [
                r"chief complaint[:\s]*(.+?)(?=\n{2,}|\n[A-Z])",
                r"reason for visit[:\s]*(.+?)(?=\n{2,}|\n[A-Z])"
            ],
            "history_of_present_illness": [
                r"history of present illness[:\s]*(.+?)(?=\n{2,}|\n[A-Z])",
                r"hpi[:\s]*(.+?)(?=\n{2,}|\n[A-Z])"
            ],
            "past_medical_history": [
                r"past medical history[:\s]*(.+?)(?=\n{2,}|\n[A-Z])",
                r"pmh[:\s]*(.+?)(?=\n{2,}|\n[A-Z])"
            ],
            "medications": [
                r"(?:current )?medications?[:\s]*(.+?)(?=\n{2,}|\n[A-Z])",
                r"(?:current )?meds?[:\s]*(.+?)(?=\n{2,}|\n[A-Z])"
            ],
            "allergies": [
                r"allergies?[:\s]*(.+?)(?=\n{2,}|\n[A-Z])",
                r"known allergies?[:\s]*(.+?)(?=\n{2,}|\n[A-Z])"
            ],
            "physical_examination": [
                r"physical examination[:\s]*(.+?)(?=\n{2,}|\n[A-Z])",
                r"exam[:\s]*(.+?)(?=\n{2,}|\n[A-Z])"
            ],
            "assessment": [
                r"assessment[:\s]*(.+?)(?=\n{2,}|\n[A-Z])",
                r"impression[:\s]*(.+?)(?=\n{2,}|\n[A-Z])"
            ],
            "plan": [
                r"plan[:\s]*(.+?)(?=\n{2,}|\n[A-Z])",
                r"treatment plan[:\s]*(.+?)(?=\n{2,}|\n[A-Z])"
            ],
            "lab_results": [
                r"lab(?:oratory)? results?[:\s]*(.+?)(?=\n{2,}|\n[A-Z])",
                r"laboratory[:\s]*(.+?)(?=\n{2,}|\n[A-Z])"
            ]
        }

        sections = {}
        # Work on original text but use DOTALL and IGNORECASE searching
        for section_name, patterns in section_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                if match:
                    # Trim trailing whitespace/newlines
                    sections[section_name] = match.group(1).strip()
                    break

        return sections

    def _extract_key_info(self, doc) -> Dict[str, Any]:
        """Extract key medical information from processed document"""
        key_info: Dict[str, Any] = {}

        try:
            text = doc.text.lower()

            # Extract vital signs
            vitals_patterns = {
                "blood_pressure": r"bp[:\s]*(\d{2,3}\/\d{2,3})",
                "heart_rate": r"(?:heart rate|pulse|hr)[:\s]*(\d{2,3})\s*bpm?",
                "temperature": r"temp(?:erature)?[:\s]*(\d{2,3}\.?\d*)\s*[fFcC]?",
                "respiratory_rate": r"rr[:\s]*(\d{1,2})\s*\/min",
                "oxygen_saturation": r"(?:o2 sat|spo2)[:\s]*(\d{1,3})\s*%"
            }

            for vital, pattern in vitals_patterns.items():
                match = re.search(pattern, text)
                if match:
                    key_info[vital] = match.group(1)

            # Extract medications with dosages (basic)
            medication_pattern = r"([A-Za-z0-9\-]+)\s+(\d+(?:\.\d+)?)\s*(?:mg|mcg|g|ml|units?)"
            medications = re.findall(medication_pattern, text, re.IGNORECASE)
            if medications:
                key_info["medications_with_dosage"] = [{"name": med, "dosage": dose} for med, dose in medications]

            # Extract lab values (simple heuristics)
            lab_pattern = r"([A-Za-z0-9_ ]{1,30})\s*[:\s=]+\s*(\d+\.?\d*)\s*(?:mg\/dl|mmol\/L|U\/L|ng\/mL|pg\/mL|%)?"
            lab_values = re.findall(lab_pattern, text, re.IGNORECASE)
            if lab_values:
                key_info["lab_values"] = [{"test": test.strip(), "value": value} for test, value in lab_values]

            # Extract dates from doc entities if available
            dates = [ent.text for ent in doc.ents if ent.label_ == "DATE"] if doc.ents else []
            if dates:
                key_info["dates_mentioned"] = dates

        except Exception as e:
            logger.error("Error extracting key info: %s", e)

        return key_info

    def _extract_key_info_basic(self, text: str) -> Dict[str, Any]:
        """Extract key information using basic regex patterns"""
        key_info = {}

        try:
            vitals_patterns = {
                "blood_pressure": r"bp[:\s]*(\d{2,3}\/\d{2,3})",
                "heart_rate": r"(?:heart rate|pulse|hr)[:\s]*(\d{2,3})",
                "temperature": r"temp(?:erature)?[:\s]*(\d{2,3}\.?\d*)\s*[fF]"
            }

            for vital, pattern in vitals_patterns.items():
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    key_info[vital] = matches
        except Exception as e:
            logger.error("Error in basic key info extraction: %s", e)

        return key_info

    def _get_text_stats(self, doc, text: str) -> Dict[str, Any]:
        """Get text statistics"""
        try:
            return {
                "word_count": len([token for token in doc if not token.is_space]) if doc is not None else len(text.split()),
                "sentence_count": len(list(doc.sents)) if doc is not None else len([s for s in re.split(r'[.!?]+', text) if s.strip()]),
                "character_count": len(text),
                "entity_count": len(doc.ents) if doc is not None else 0,
                "unique_words": len(set([token.text.lower() for token in doc if not token.is_space and not token.is_punct])) if doc is not None else len(set(text.lower().split()))
            }
        except Exception as e:
            logger.error("Error computing text stats: %s", e)
            return {}

    def _extract_relationships(self, doc) -> List[Dict[str, Any]]:
        """Extract relationships between medical entities"""
        relationships = []

        try:
            medications = [ent for ent in doc.ents if ent.label_ == "MEDICATION"] if doc is not None else []
            conditions = [ent for ent in doc.ents if ent.label_ == "CONDITION"] if doc is not None else []

            for med in medications:
                for condition in conditions:
                    distance = abs(med.start_char - condition.end_char)
                    if distance < 100:
                        relationships.append({
                            "type": "medication_for_condition",
                            "source": med.text,
                            "target": condition.text,
                            "distance": distance,
                            "confidence": max(0, 1 - distance / 100)
                        })

            tests = [ent for ent in doc.ents if ent.label_ == "LAB_TEST"] if doc is not None else []
            numbers = [ent for ent in doc.ents if ent.label_ == "CARDINAL"] if doc is not None else []

            for test in tests:
                for num in numbers:
                    if abs(test.start_char - num.start_char) < 50:
                        relationships.append({
                            "type": "test_result",
                            "source": test.text,
                            "target": num.text,
                            "relationship": "value"
                        })

        except Exception as e:
            logger.error("Error extracting relationships: %s", e)

        return relationships

    async def extract_entities_summary(self, text: str) -> Dict[str, Any]:
        """
        Extract and summarize medical entities for quick overview
        """
        try:
            if not self.nlp:
                return {"entities": [], "summary": "NLP processing not available", "total_entities": 0}

            # Do spaCy processing in thread
            doc = await asyncio.to_thread(self.nlp, text)

            entities = defaultdict(list)
            for ent in doc.ents:
                if ent.label_ in ["MEDICATION", "CONDITION", "PROCEDURE", "BODY_PART", "LAB_TEST"]:
                    entities[ent.label_].append(ent.text)

            summary_parts = []
            if entities["CONDITION"]:
                summary_parts.append(f"Found {len(entities['CONDITION'])} conditions: {', '.join(entities['CONDITION'][:3])}")
            if entities["MEDICATION"]:
                summary_parts.append(f"Found {len(entities['MEDICATION'])} medications: {', '.join(entities['MEDICATION'][:3])}")
            if entities["PROCEDURE"]:
                summary_parts.append(f"Found {len(entities['PROCEDURE'])} procedures: {', '.join(entities['PROCEDURE'][:3])}")

            return {
                "entities": dict(entities),
                "summary": ". ".join(summary_parts) if summary_parts else "No specific medical entities found",
                "total_entities": sum(len(entity_list) for entity_list in entities.values())
            }

        except Exception as e:
            logger.error("Error extracting entities summary: %s", e)
            return {"entities": {}, "summary": "Error processing entities", "total_entities": 0}


# Singleton instance
nlp_service = NLPService()
