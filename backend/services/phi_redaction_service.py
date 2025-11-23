"""
PHI Redaction Service for HIPAA compliance
Uses Presidio for detecting and redacting Protected Health Information
"""

import re
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

# Try to import Presidio components; set a flag if unavailable
PRESIDIO_AVAILABLE = True
try:
    from presidio_analyzer import AnalyzerEngine, Pattern
    from presidio_anonymizer import AnonymizerEngine
    from presidio_anonymizer.entities import OperatorConfig
    # SpacyNlpEngine is imported lazily in setup_presidio to avoid import errors if presidio isn't installed
except Exception:
    PRESIDIO_AVAILABLE = False

from core.logging import logger
from core.config import settings


class PHIRedactionService:
    """Service for detecting and redacting PHI from medical documents"""

    def __init__(self):
        self.analyzer = None
        self.anonymizer = None
        self.custom_patterns: List[Dict[str, Any]] = []
        # Setup patterns first (used by Presidio and regex fallback)
        self.setup_custom_patterns()
        # Then setup Presidio (depends on patterns optionally)
        self.setup_presidio()

    def setup_presidio(self):
        """Setup Presidio analyzer and anonymizer safely.

        Force SpacyNlpEngine to use en_core_web_sm if present; otherwise use a blank 'en'.
        This prevents Presidio from auto-loading en_core_web_lg and failing startup.
        """
        if not PRESIDIO_AVAILABLE:
            logger.warning("Presidio not available. Using regex fallback.")
            return

        try:
            # Build models mapping for SpacyNlpEngine.
            models = {}
            try:
                import spacy
                # prefer en_core_web_sm if installed
                try:
                    spacy.load("en_core_web_sm")
                    models["en"] = "en_core_web_sm"
                except Exception:
                    # not installed — instruct SpacyNlpEngine to use a blank model by passing None
                    models["en"] = None
            except Exception:
                models["en"] = None

            # Create SpacyNlpEngine with explicit models mapping to avoid auto-loading a large model.
            from presidio_analyzer.nlp_engine import SpacyNlpEngine  # lazy import
            nlp_engine = SpacyNlpEngine(models=models)
            self.analyzer = AnalyzerEngine(nlp_engine=nlp_engine)
            self.anonymizer = AnonymizerEngine()
            logger.info("Presidio initialized with SpacyNlpEngine(models=%s)", models)
        except Exception as e:
            logger.error("Error setting up Presidio: %s", e)
            self.analyzer = None
            self.anonymizer = None

    def setup_custom_patterns(self):
        """Setup custom medical PHI patterns"""
        self.custom_patterns = [
            # Medical Record Numbers
            {
                "name": "MEDICAL_RECORD_NUMBER",
                "regex": r"\b(?:MR|MED|MEDICAL\s*RECORD|#)\s*[:#]?\s*\d{6,10}\b",
                "score": 0.8,
            },
# Patient IDs like "ID: SATPRIET 128", "PATIENT ID: AB1234"
{
    "name": "PATIENT_ID",
    "regex": r"\b(?:PATIENT\s*ID|PID|ID)\s*[:#]?\s*[A-Z0-9]{2,12}[-\s]?\d{1,6}\b",
    "score": 0.9,
},

# Case / MRN style IDs: "Case No: R-55220", "UHID: XYS123 77"
{
    "name": "PATIENT_CASE_ID",
    "regex": r"\b(?:CASE\s*NO\.?|CASE|UHID|MRN)\s*[:#]?\s*[A-Z0-9]{2,12}[-\s]?\d{1,6}\b",
    "score": 0.9,
},

            # SSN variations
            {
                "name": "SOCIAL_SECURITY_NUMBER",
                "regex": r"\b\d{3}[-.\s]?\d{2}[-.\s]?\d{4}\b",
                "score": 0.95,
            },
            # Phone numbers (extended)
            {
                "name": "PHONE_NUMBER",
                "regex": r"\b(?:\+?1[-.\s]?)?\(?[2-9][0-8]\d\)?[-.\s]?[2-9]\d{2}[-.\s]?\d{4}\b",
                "score": 0.9,
            },
            # Email addresses
            {
                "name": "EMAIL_ADDRESS",
                "regex": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
                "score": 0.95,
            },
            # Address patterns (US-centric)
            {
                "name": "STREET_ADDRESS",
                "regex": r"\d+\s+[A-Z][a-zA-Z]+\s+(?:St|Ave|Avenue|Blvd|Boulevard|Dr|Drive|Lane|Ln|Road|Rd|Court|Ct|Way|Pl|Place|Square|Sq|Terrace|Ter|Parkway|Pkwy|Circle|Cir|Trail|Trl)[\s,]*[A-Z]{2}\s*\d{5}",
                "score": 0.85,
            },
            # ZIP codes
            {
                "name": "ZIP_CODE",
                "regex": r"\b\d{5}(?:[-\s]\d{4})?\b",
                "score": 0.7,
            },
            # Medical license numbers
            {
                "name": "MEDICAL_LICENSE",
                "regex": r"\b(?:MD|DO|RN|PA|NP)\s*[:#]?\s*[A-Z]{2,3}\d{6,8}\b",
                "score": 0.8,
            },
            # Account numbers
            {
                "name": "ACCOUNT_NUMBER",
                "regex": r"\b(?:ACCT|ACCOUNT)\s*[:#]?\s*\d{6,12}\b",
                "score": 0.8,
            },
            # Dates (DOB)
            {
                "name": "BIRTH_DATE",
                "regex": r"\b(?:DOB|Date\s*of\s*Birth|Birth\s*Date)\s*[:#]?\s*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
                "score": 0.9,
            },
        ]

    async def detect_phi(self, text: str) -> List[Dict[str, Any]]:
        """
        Detect PHI in text

        Args:
            text: Text to analyze for PHI

        Returns:
            List of detected PHI entities
        """
        try:
            if self.analyzer:
                return await self._detect_with_presidio(text)
            else:
                return await self._detect_with_regex(text)
        except Exception as e:
            logger.error(f"Error detecting PHI: {e}")
            return []

    async def _detect_with_presidio(self, text: str) -> List[Dict[str, Any]]:
        """Detect PHI using Presidio (runs blocking analyze in a thread)"""
        try:
            # Add custom patterns to Presidio
            patterns = []
            for pattern_config in self.custom_patterns:
                try:
                    patterns.append(Pattern(
                        name=pattern_config["name"],
                        regex=pattern_config["regex"],
                        score=pattern_config["score"]
                    ))
                except Exception:
                    # If Pattern class can't be used, skip adding
                    logger.debug("Unable to add custom pattern to Presidio: %s", pattern_config.get("name"))

            # AnalyzerEngine.analyze is synchronous — run in a thread to avoid blocking
            def analyze_sync():
                return self.analyzer.analyze(
                    text=text,
                    entities=[
                        "PERSON", "LOCATION", "DATE_TIME", "PHONE_NUMBER",
                        "EMAIL_ADDRESS", "IP_ADDRESS", "URL", "NRP",
                        "MEDICAL_RECORD_NUMBER", "PATIENT_ID",
                        "PATIENT_CASE_ID",  # 👈 add this
],

                    language="en",
                    add_patterns=patterns if patterns else None
                )

            results = await asyncio.to_thread(analyze_sync)

            # Convert Presidio results to our format
            phi_entities: List[Dict[str, Any]] = []
            for result in results:
                try:
                    phi_entities.append({
                        "type": result.entity_type,
                        "text": text[result.start:result.end],
                        "start": result.start,
                        "end": result.end,
                        "score": result.score,
                        "source": "presidio"
                    })
                except Exception as e:
                    logger.debug("Error converting presidio result: %s", e)

            return phi_entities

        except Exception as e:
            logger.error(f"Error with Presidio detection: {e}")
            # Fallback to regex detection
            return await self._detect_with_regex(text)

    async def _detect_with_regex(self, text: str) -> List[Dict[str, Any]]:
        """Detect PHI using regex patterns (fallback)"""
        phi_entities: List[Dict[str, Any]] = []

        for pattern_config in self.custom_patterns:
            try:
                for match in re.finditer(pattern_config["regex"], text, re.IGNORECASE):
                    phi_entities.append({
                        "type": pattern_config["name"],
                        "text": match.group(0),
                        "start": match.start(),
                        "end": match.end(),
                        "score": pattern_config["score"],
                        "source": "regex"
                    })
            except Exception as e:
                logger.error(f"Error in regex pattern {pattern_config['name']}: {e}")
                continue

        # Basic name detection (simple heuristic)
        name_patterns = [
            r"\b(?:Mr|Mrs|Ms|Dr)\.\s+[A-Z][a-z]+\s+[A-Z][a-z]+\b",
            r"\b[A-Z][a-z]+\s+[A-Z][a-z]+\b(?=\s(?:MD|DO|RN|PA|NP))"
        ]

        for pattern in name_patterns:
            try:
                for match in re.finditer(pattern, text):
                    phi_entities.append({
                        "type": "PERSON",
                        "text": match.group(0),
                        "start": match.start(),
                        "end": match.end(),
                        "score": 0.6,
                        "source": "regex"
                    })
            except Exception as e:
                logger.error(f"Error in name pattern: {e}")

        return phi_entities

    async def redact_phi(self, text: str, redaction_char: str = "[REDACTED]") -> Dict[str, Any]:
        """
        Redact PHI from text

        Args:
            text: Text to redact
            redaction_char: Character/string to use for redaction

        Returns:
            Dictionary with redacted text and PHI entities
        """
        try:
            # Detect PHI
            phi_entities = await self.detect_phi(text)

            # Normalize and dedupe overlapping entities: sort by start, then merge overlaps
            if not phi_entities:
                return {
                    "original_text": text,
                    "redacted_text": text,
                    "phi_entities": [],
                    "phi_summary": "No PHI detected",
                    "redaction_stats": {
                        "total_entities": 0,
                        "redaction_char_used": redaction_char,
                        "text_length_original": len(text),
                        "text_length_redacted": len(text)
                    }
                }

            # Sort by start index
            phi_entities.sort(key=lambda x: (x["start"], -x["end"]))

            # Merge overlapping entries (keep the widest span)
            merged = []
            current = phi_entities[0].copy()
            for ent in phi_entities[1:]:
                if ent["start"] <= current["end"]:
                    # overlap or contiguous -> extend if needed
                    if ent["end"] > current["end"]:
                        current["end"] = ent["end"]
                        current["text"] = text[current["start"]:current["end"]]
                        # keep max score
                        current["score"] = max(current.get("score", 0), ent.get("score", 0))
                else:
                    merged.append(current)
                    current = ent.copy()
            merged.append(current)

            # Redact by replacing spans from the end to avoid offset math
            redacted_text = text
            for ent in sorted(merged, key=lambda e: e["start"], reverse=True):
                start, end = ent["start"], ent["end"]
                redacted_text = redacted_text[:start] + redaction_char + redacted_text[end:]

            # Generate summary
            phi_summary = self._generate_phi_summary(merged)

            return {
                "original_text": text,
                "redacted_text": redacted_text,
                "phi_entities": merged,
                "phi_summary": phi_summary,
                "redaction_stats": {
                    "total_entities": len(merged),
                    "redaction_char_used": redaction_char,
                    "text_length_original": len(text),
                    "text_length_redacted": len(redacted_text)
                }
            }

        except Exception as e:
            logger.error(f"Error redacting PHI: {e}")
            return {
                "original_text": text,
                "redacted_text": text,
                "phi_entities": [],
                "phi_summary": "Error during redaction",
                "redaction_stats": {"error": str(e)}
            }

    def _generate_phi_summary(self, phi_entities: List[Dict[str, Any]]) -> str:
        """Generate summary of detected PHI"""
        if not phi_entities:
            return "No PHI detected"

        # Count by type
        type_counts: Dict[str, int] = {}
        for entity in phi_entities:
            entity_type = entity.get("type", "UNKNOWN")
            type_counts[entity_type] = type_counts.get(entity_type, 0) + 1

        # Create summary
        summary_parts = []
        for entity_type, count in sorted(type_counts.items()):
            summary_parts.append(f"{count} {entity_type.replace('_', ' ').lower()}")

        return f"Detected and redacted: {', '.join(summary_parts)}"

    async def is_phi_free(self, text: str) -> Dict[str, Any]:
        """
        Check if text is PHI-free

        Args:
            text: Text to check

        Returns:
            Dictionary with PHI-free status
        """
        try:
            phi_entities = await self.detect_phi(text)

            # Check for high-confidence PHI
            high_confidence_phi = [
                entity for entity in phi_entities
                if entity.get("score", 0) >= 0.7
            ]

            return {
                "is_phi_free": len(high_confidence_phi) == 0,
                "phi_count": len(phi_entities),
                "high_confidence_phi_count": len(high_confidence_phi),
                "phi_entities": phi_entities,
                "confidence_score": min(1.0, len(high_confidence_phi) * 0.1)
            }

        except Exception as e:
            logger.error(f"Error checking PHI-free status: {e}")
            return {
                "is_phi_free": False,
                "phi_count": 0,
                "high_confidence_phi_count": 0,
                "phi_entities": [],
                "confidence_score": 0.0,
                "error": str(e)
            }

    async def create_phi_report(self, original_text: str, redacted_text: str) -> Dict[str, Any]:
        """
        Create detailed PHI redaction report for compliance
        """
        try:
            phi_entities = await self.detect_phi(original_text)

            # Count how many redactions were inserted
            redaction_token = "[REDACTED]"
            total_redacted = redacted_text.count(redaction_token)
            total_phi = len(phi_entities)

            # Categorize PHI types
            phi_categories: Dict[str, List[Dict[str, Any]]] = {}
            for entity in phi_entities:
                entity_type = entity.get("type", "UNKNOWN")
                if entity_type not in phi_categories:
                    phi_categories[entity_type] = []
                text_snip = entity.get("text", "")
                phi_categories[entity_type].append({
                    "text": (text_snip[:20] + "...") if len(text_snip) > 20 else text_snip,
                    "confidence": entity.get("score", 0)
                })

            avg_confidence = sum(e.get("score", 0) for e in phi_entities) / max(1, len(phi_entities))

            return {
                "phi_redaction_report": {
                    "compliance_standard": "HIPAA",
                    "processing_timestamp": datetime.now(timezone.utc).isoformat(),
                    "original_text_length": len(original_text),
                    "redacted_text_length": len(redacted_text),
                    "total_phi_detected": total_phi,
                    "total_phi_redacted": total_redacted,
                    "redaction_efficiency": total_redacted / max(1, total_phi),
                    "phi_categories": phi_categories,
                    "average_confidence": avg_confidence,
                    "redaction_method": "presidio" if self.analyzer else "regex_fallback"
                }
            }

        except Exception as e:
            logger.error(f"Error creating PHI report: {e}")
            return {
                "phi_redaction_report": {
                    "error": str(e),
                    "compliance_standard": "HIPAA"
                }
            }


# Singleton instance
phi_redaction_service = PHIRedactionService()
