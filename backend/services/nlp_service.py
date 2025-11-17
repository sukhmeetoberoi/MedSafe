"""
NLP Service for medical text processing and entity extraction
Uses spaCy for natural language processing and medical entity recognition
"""

import spacy
import re
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict
import json
from core.logging import logger
from core.config import settings

class NLPService:
    """Service for medical text processing and entity extraction"""

    def __init__(self):
        self.nlp = None
        self.load_models()

    def load_models(self):
        """Load spaCy models and medical entities"""
        try:
            # Load spaCy model
            self.nlp = spacy.load(settings.SPACY_MODEL)
            logger.info(f"Loaded spaCy model: {settings.SPACY_MODEL}")

            # Add medical entity patterns if not already present
            self._add_medical_patterns()

        except Exception as e:
            logger.error(f"Error loading spaCy model: {e}")
            # Fallback to basic processing
            self.nlp = None

    def _add_medical_patterns(self):
        """Add medical entity patterns to spaCy pipeline"""
        if not self.nlp or "entity_ruler" not in self.nlp.pipe_names:
            return

        medical_patterns = [
            # Medications
            {"label": "MEDICATION", "pattern": [{"LOWER": {"IN": [
                "aspirin", "ibuprofen", "acetaminophen", "tylenol", "advil",
                "lipitor", "metformin", "lisinopril", "atorvastatin", "amoxicillin",
                "prednisone", "hydrochlorothiazide", "simvastatin", "omeprazole",
                "azithromycin", "albuterol", "levothyroxine", "furosemide"
            ]}}]},

            # Medical Conditions
            {"label": "CONDITION", "pattern": [{"LOWER": {"IN": [
                "diabetes", "hypertension", "asthma", "arthritis", "depression",
                "anxiety", "pneumonia", "bronchitis", "migraine", "hypothyroidism",
                "hyperlipidemia", "osteoporosis", "copd", "gastroenteritis",
                "kidney disease", "heart disease", "stroke", "cancer", "infection"
            ]}}]},

            # Medical Procedures
            {"label": "PROCEDURE", "pattern": [{"LOWER": {"IN": [
                "mri", "ct scan", "x-ray", "ultrasound", "ecg", "ekg",
                "blood test", "colonoscopy", "endoscopy", "biopsy", "surgery",
                "vaccination", "immunization", "dialysis", "chemotherapy",
                "radiation therapy", "physical therapy"
            ]}}]},

            # Body Parts
            {"label": "BODY_PART", "pattern": [{"LOWER": {"IN": [
                "heart", "lung", "liver", "kidney", "brain", "stomach", "intestine",
                "chest", "abdomen", "head", "neck", "back", "arm", "leg",
                "blood", "blood pressure", "pulse", "temperature"
            ]}}]},

            # Lab Tests
            {"label": "LAB_TEST", "pattern": [{"LOWER": {"IN": [
                "cbc", "complete blood count", "cmp", "comprehensive metabolic panel",
                "lipid panel", "a1c", "hemoglobin a1c", "tsh", "thyroid stimulating hormone",
                "cholesterol", "ldl", "hdl", "triglycerides", "glucose", "creatinine",
                "bun", "blood urea nitrogen", "electrolytes", "sodium", "potassium"
            ]}}]}
        ]

        # Add patterns to entity ruler
        ruler = self.nlp.add_pipe("entity_ruler", before="ner")
        ruler.add_patterns(medical_patterns)
        logger.info("Added medical entity patterns to spaCy pipeline")

    async def process_medical_text(self, text: str) -> Dict[str, Any]:
        """
        Process medical text and extract entities, sections, and key information

        Args:
            text: Medical text to process

        Returns:
            Dictionary with processed information
        """
        try:
            if not self.nlp:
                return await self._basic_text_processing(text)

            # Process text with spaCy
            doc = self.nlp(text)

            # Extract entities
            entities = self._extract_entities(doc)

            # Extract medical sections
            sections = self._extract_sections(text)

            # Extract key medical information
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
            logger.error(f"Error processing medical text: {e}")
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
                    "sentence_count": len(re.split(r'[.!?]+', text)),
                    "character_count": len(text)
                },
                "relationships": [],
                "processed_text_length": len(text),
                "processing_method": "basic_regex"
            }

        except Exception as e:
            logger.error(f"Error in basic text processing: {e}")
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

        for ent in doc.ents:
            entities.append({
                "text": ent.text,
                "label": ent.label_,
                "start_char": ent.start_char,
                "end_char": ent.end_char,
                "confidence": getattr(ent, 'confidence', 1.0),
                "description": self._get_entity_description(ent.label_)
            })

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
        """Extract common medical report sections"""
        section_patterns = {
            "patient_information": [
                r"patient information[:\s]*(.+?)(?=\n\n|\n[A-Z])",
                r"patient details?[:\s]*(.+?)(?=\n\n|\n[A-Z])"
            ],
            "chief_complaint": [
                r"chief complaint[:\s]*(.+?)(?=\n\n|\n[A-Z])",
                r"reason for visit[:\s]*(.+?)(?=\n\n|\n[A-Z])"
            ],
            "history_of_present_illness": [
                r"history of present illness[:\s]*(.+?)(?=\n\n|\n[A-Z])",
                r"hpi[:\s]*(.+?)(?=\n\n|\n[A-Z])"
            ],
            "past_medical_history": [
                r"past medical history[:\s]*(.+?)(?=\n\n|\n[A-Z])",
                r"pmh[:\s]*(.+?)(?=\n\n|\n[A-Z])"
            ],
            "medications": [
                r"(?:current )?medications?[:\s]*(.+?)(?=\n\n|\n[A-Z])",
                r"(?:current )?meds?[:\s]*(.+?)(?=\n\n|\n[A-Z])"
            ],
            "allergies": [
                r"allergies?[:\s]*(.+?)(?=\n\n|\n[A-Z])",
                r"known allergies?[:\s]*(.+?)(?=\n\n|\n[A-Z])"
            ],
            "physical_examination": [
                r"physical examination[:\s]*(.+?)(?=\n\n|\n[A-Z])",
                r"exam[:\s]*(.+?)(?=\n\n|\n[A-Z])"
            ],
            "assessment": [
                r"assessment[:\s]*(.+?)(?=\n\n|\n[A-Z])",
                r"impression[:\s]*(.+?)(?=\n\n|\n[A-Z])"
            ],
            "plan": [
                r"plan[:\s]*(.+?)(?=\n\n|\n[A-Z])",
                r"treatment plan[:\s]*(.+?)(?=\n\n|\n[A-Z])"
            ],
            "lab_results": [
                r"lab(?:oratory)? results?[:\s]*(.+?)(?=\n\n|\n[A-Z])",
                r"laboratory[:\s]*(.+?)(?=\n\n|\n[A-Z])"
            ]
        }

        sections = {}
        text_lower = text.lower()

        for section_name, patterns in section_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text_lower, re.IGNORECASE | re.DOTALL)
                if match:
                    sections[section_name] = match.group(1).strip()
                    break

        return sections

    def _extract_key_info(self, doc) -> Dict[str, Any]:
        """Extract key medical information from processed document"""
        key_info = {}

        # Extract vital signs
        vitals_patterns = {
            "blood_pressure": r"bp[:\s]*(\d{2,3}\/\d{2,3})",
            "heart_rate": r"(?:heart rate|pulse|hr)[:\s]*(\d{2,3})\s*bpm",
            "temperature": r"temp(?:erature)?[:\s]*(\d{2,3}\.?\d*)\s*[fF]",
            "respiratory_rate": r"rr[:\s]*(\d{1,2})\s*\/min",
            "oxygen_saturation": r"o2 sat|spo2[:\s]*(\d{1,3})\s*%"
        }

        text = doc.text.lower()
        for vital, pattern in vitals_patterns.items():
            match = re.search(pattern, text)
            if match:
                key_info[vital] = match.group(1)

        # Extract medications with dosages
        medication_pattern = r"(\b(?:[A-Z][a-z]+|\d+)\b)\s*(\d+)\s*(?:mg|mcg|g|ml|units?)"
        medications = re.findall(medication_pattern, text, re.IGNORECASE)
        if medications:
            key_info["medications_with_dosage"] = [{"name": med, "dosage": dose} for med, dose in medications]

        # Extract lab values
        lab_pattern = r"(\w+)\s*[:\s=]*\s*(\d+\.?\d*)\s*(?:mg\/dl|mmol\/L|U\/L|ng\/mL|pg\/mL)?"
        lab_values = re.findall(lab_pattern, text, re.IGNORECASE)
        if lab_values:
            key_info["lab_values"] = [{"test": test, "value": value} for test, value in lab_values]

        # Extract dates
        dates = [ent.text for ent in doc.ents if ent.label_ == "DATE"]
        if dates:
            key_info["dates_mentioned"] = dates

        return key_info

    def _extract_key_info_basic(self, text: str) -> Dict[str, Any]:
        """Extract key information using basic regex patterns"""
        key_info = {}

        # Basic vital signs extraction
        vitals_patterns = {
            "blood_pressure": r"bp[:\s]*(\d{2,3}\/\d{2,3})",
            "heart_rate": r"(?:heart rate|pulse|hr)[:\s]*(\d{2,3})",
            "temperature": r"temp(?:erature)?[:\s]*(\d{2,3}\.?\d*)\s*[fF]"
        }

        for vital, pattern in vitals_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                key_info[vital] = matches

        return key_info

    def _get_text_stats(self, doc, text: str) -> Dict[str, Any]:
        """Get text statistics"""
        return {
            "word_count": len([token for token in doc if not token.is_space]),
            "sentence_count": len(list(doc.sents)),
            "character_count": len(text),
            "entity_count": len(doc.ents),
            "unique_words": len(set([token.text.lower() for token in doc if not token.is_space and not token.is_punct]))
        }

    def _extract_relationships(self, doc) -> List[Dict[str, Any]]:
        """Extract relationships between medical entities"""
        relationships = []

        try:
            # Find medication-condition relationships
            medications = [ent for ent in doc.ents if ent.label_ == "MEDICATION"]
            conditions = [ent for ent in doc.ents if ent.label_ == "CONDITION"]

            for med in medications:
                for condition in conditions:
                    distance = abs(med.start_char - condition.end_char)
                    if distance < 100:  # Within reasonable proximity
                        relationships.append({
                            "type": "medication_for_condition",
                            "source": med.text,
                            "target": condition.text,
                            "distance": distance,
                            "confidence": max(0, 1 - distance / 100)
                        })

            # Find test-result relationships
            tests = [ent for ent in doc.ents if ent.label_ == "LAB_TEST"]
            numbers = [ent for ent in doc.ents if ent.label_ == "CARDINAL"]

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
            logger.error(f"Error extracting relationships: {e}")

        return relationships

    async def extract_entities_summary(self, text: str) -> Dict[str, Any]:
        """
        Extract and summarize medical entities for quick overview
        """
        try:
            if not self.nlp:
                return {"entities": [], "summary": "NLP processing not available"}

            doc = self.nlp(text)
            entities = defaultdict(list)

            for ent in doc.ents:
                if ent.label_ in ["MEDICATION", "CONDITION", "PROCEDURE", "BODY_PART", "LAB_TEST"]:
                    entities[ent.label_].append(ent.text)

            # Create summary
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
            logger.error(f"Error extracting entities summary: {e}")
            return {"entities": {}, "summary": "Error processing entities", "total_entities": 0}

# Singleton instance
nlp_service = NLPService()