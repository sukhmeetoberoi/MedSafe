"""
PHI Redaction Service for HIPAA compliance
Uses Presidio for detecting and redacting Protected Health Information
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import RecognizerResult, OperatorConfig

# Presidio might not be available, so we'll handle import gracefully
try:
    from presidio_analyzer import AnalyzerEngine
    from presidio_anonymizer import AnonymizerEngine
    from presidio_anonymizer.entities import OperatorConfig
    PRESIDIO_AVAILABLE = True
except ImportError:
    PRESIDIO_AVAILABLE = False

from core.logging import logger
from core.config import settings

class PHIRedactionService:
    """Service for detecting and redacting PHI from medical documents"""

    def __init__(self):
        self.analyzer = None
        self.anonymizer = None
        self.setup_presidio()
        self.setup_custom_patterns()

    def setup_presidio(self):
        """Setup Presidio analyzer and anonymizer"""
        if not PRESIDIO_AVAILABLE:
            logger.warning("Presidio not available. Using fallback PHI detection.")
            return

        try:
            self.analyzer = AnalyzerEngine()
            self.anonymizer = AnonymizerEngine()
            logger.info("Presidio PHI detection initialized successfully")
        except Exception as e:
            logger.error(f"Error setting up Presidio: {e}")
            self.analyzer = None
            self.anonymizer = None

    def setup_custom_patterns(self):
        """Setup custom medical PHI patterns"""
        self.custom_patterns = [
            # Medical Record Numbers
            {
                "name": "MEDICAL_RECORD_NUMBER",
                "regex": r"\b(MR|MED|MEDICAL\s*RECORD|#)\s*[:#]?\s*\d{6,10}\b",
                "score": 0.8
            },

            # Patient IDs
            {
                "name": "PATIENT_ID",
                "regex": r"\b(PATIENT\s*ID|PID|ID)\s*[:#]?\s*[A-Z]{2,4}-?\d{4,8}\b",
                "score": 0.9
            },

            # SSN variations
            {
                "name": "SOCIAL_SECURITY_NUMBER",
                "regex": r"\b\d{3}[-.\s]?\d{2}[-.\s]?\d{4}\b",
                "score": 0.95
            },

            # Phone numbers (extended)
            {
                "name": "PHONE_NUMBER",
                "regex": r"\b(?:\+?1[-.\s]?)?\(?([2-9][0-8]\d)\)?[-.\s]?([2-9]\d{2})[-.\s]?(\d{4})\b",
                "score": 0.9
            },

            # Email addresses
            {
                "name": "EMAIL_ADDRESS",
                "regex": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
                "score": 0.95
            },

            # Address patterns
            {
                "name": "STREET_ADDRESS",
                "regex": r"\d+\s+[A-Z][a-z]+\s+(?:St|Ave|Avenue|Blvd|Boulevard|Dr|Drive|Lane|Ln|Road|Rd|Court|Ct|Way|Pl|Place|Square|Sq|Terrace|Ter|Parkway|Pkwy|Circle|Cir|Trail|Trl)[\s,]*[A-Z]{2}\s*\d{5}",
                "score": 0.85
            },

            # ZIP codes
            {
                "name": "ZIP_CODE",
                "regex": r"\b\d{5}(?:[-\s]\d{4})?\b",
                "score": 0.7
            },

            # Medical license numbers
            {
                "name": "MEDICAL_LICENSE",
                "regex": r"\b(?:MD|DO|RN|PA|NP)\s*[:#]?\s*[A-Z]{2,3}\d{6,8}\b",
                "score": 0.8
            },

            # Account numbers
            {
                "name": "ACCOUNT_NUMBER",
                "regex": r"\b(?:ACCT|ACCOUNT)\s*[:#]?\s*\d{6,12}\b",
                "score": 0.8
            },

            # Dates (HIPAA considers dates over 90 years old as PHI)
            {
                "name": "BIRTH_DATE",
                "regex": r"\b(?:DOB|Date\s*of\s*Birth|Birth\s*Date)\s*[:#]?\s*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
                "score": 0.9
            }
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
        """Detect PHI using Presidio"""
        try:
            # Add custom patterns to Presidio
            patterns = []
            for pattern_config in self.custom_patterns:
                from presidio_analyzer import Pattern
                patterns.append(Pattern(
                    name=pattern_config["name"],
                    regex=pattern_config["regex"],
                    score=pattern_config["score"]
                ))

            # Analyze text
            results = self.analyzer.analyze(
                text=text,
                entities=[  # PHI entities to detect
                    "PERSON", "LOCATION", "DATE_TIME", "PHONE_NUMBER",
                    "EMAIL_ADDRESS", "IP_ADDRESS", "URL", "NRP",
                    "MEDICAL_RECORD_NUMBER", "PATIENT_ID"
                ],
                language="en",
                add_patterns=patterns if patterns else None
            )

            # Convert Presidio results to our format
            phi_entities = []
            for result in results:
                phi_entities.append({
                    "type": result.entity_type,
                    "text": text[result.start:result.end],
                    "start": result.start,
                    "end": result.end,
                    "score": result.score,
                    "source": "presidio"
                })

            return phi_entities

        except Exception as e:
            logger.error(f"Error with Presidio detection: {e}")
            # Fallback to regex detection
            return await self._detect_with_regex(text)

    async def _detect_with_regex(self, text: str) -> List[Dict[str, Any]]:
        """Detect PHI using regex patterns (fallback)"""
        phi_entities = []

        for pattern_config in self.custom_patterns:
            try:
                matches = re.finditer(
                    pattern_config["regex"],
                    text,
                    re.IGNORECASE
                )

                for match in matches:
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
                matches = re.finditer(pattern, text)
                for match in matches:
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

            # Sort entities by start position to avoid overlapping issues
            phi_entities.sort(key=lambda x: x["start"])

            # Create redacted text
            redacted_text = text
            offset = 0

            for entity in phi_entities:
                # Adjust for previous redactions
                adjusted_start = entity["start"] + offset
                adjusted_end = entity["end"] + offset

                # Replace PHI with redaction character
                redaction = redaction_char
                redacted_text = (
                    redacted_text[:adjusted_start] +
                    redaction +
                    redacted_text[adjusted_end:]
                )

                # Update offset
                offset += len(redaction) - (entity["end"] - entity["start"])

            # Generate redaction summary
            phi_summary = self._generate_phi_summary(phi_entities)

            return {
                "original_text": text,
                "redacted_text": redacted_text,
                "phi_entities": phi_entities,
                "phi_summary": phi_summary,
                "redaction_stats": {
                    "total_entities": len(phi_entities),
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
        type_counts = {}
        for entity in phi_entities:
            entity_type = entity["type"]
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
                if entity["score"] >= 0.7
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

            # Analyze redaction effectiveness
            redacted_words = redacted_text.count("[REDACTED]")
            total_phi = len(phi_entities)

            # Categorize PHI types
            phi_categories = {}
            for entity in phi_entities:
                entity_type = entity["type"]
                if entity_type not in phi_categories:
                    phi_categories[entity_type] = []
                phi_categories[entity_type].append({
                    "text": entity["text"][:20] + "..." if len(entity["text"]) > 20 else entity["text"],
                    "confidence": entity["score"]
                })

            return {
                "phi_redaction_report": {
                    "compliance_standard": "HIPAA",
                    "processing_timestamp": "2024-01-01T00:00:00Z",  # Use actual timestamp in production
                    "original_text_length": len(original_text),
                    "redacted_text_length": len(redacted_text),
                    "total_phi_detected": total_phi,
                    "total_phi_redacted": redacted_words,
                    "redaction_efficiency": redacted_words / max(1, total_phi),
                    "phi_categories": phi_categories,
                    "average_confidence": sum(e["score"] for e in phi_entities) / max(1, len(phi_entities)),
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