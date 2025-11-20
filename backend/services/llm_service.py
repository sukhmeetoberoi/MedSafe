"""
LLM Service for generating medical report summaries
"""

import asyncio
from typing import Dict, Any, Optional

from core.config import settings
from core.logging import logger

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class LLMService:
    def __init__(self):
        self.client = None
        self.model = "gpt-4o-mini"  # change to whatever you have access to
        self._setup_clients()

    def _setup_clients(self):
        """Initialize OpenAI or fallback."""
        if not settings.OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY not set. Falling back to basic summaries.")
            return

        if not OPENAI_AVAILABLE:
            logger.warning("openai package not installed. Falling back to basic summaries.")
            return

        try:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            logger.info("OpenAI client initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing OpenAI client: {e}")
            self.client = None

    async def generate_summaries(
        self,
        redacted_text: str,
        extracted_fields: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate clinician and patient-friendly summaries.

        Returns a dict:
        {
          "clinician": {"title": ..., "content": ...},
          "patient": {"title": ..., "content": ...}
        }
        """
        # Fallback basic summaries if no client
        if not self.client:
            logger.warning("LLM client not available, using basic fallback summaries")
            base = redacted_text[:600] + ("..." if len(redacted_text) > 600 else "")
            return {
                "clinician": {
                    "title": "Clinician Summary (Fallback)",
                    "content": f"Raw excerpt (first 600 chars):\n\n{base}",
                },
                "patient": {
                    "title": "Patient Summary (Fallback)",
                    "content": "This is a basic fallback summary because the AI "
                               "client is not configured properly.",
                },
            }

        # Build a little context string from extracted_fields if available
        fields_snippet = ""
        if extracted_fields:
            parts = []
            for key, val in extracted_fields.items():
                if isinstance(val, (dict, list)):
                    continue
                parts.append(f"{key.replace('_', ' ').title()}: {val}")
            if parts:
                fields_snippet = "\n\nKey extracted fields:\n" + "\n".join(parts)

        prompt_common = (
            "You are a medical assistant helping summarize a medical report.\n\n"
            "Here is the PHI-redacted text of the report:\n"
            "--------------------\n"
            f"{redacted_text}\n"
            "--------------------\n"
            f"{fields_snippet}\n\n"
        )

        # Run two prompts in sequence (clinician + patient).
        async def _call_openai(system_msg: str, user_msg: str) -> str:
            """Call OpenAI in a thread (client is sync)."""
            def _sync_call():
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": user_msg},
                    ],
                    temperature=0.3,
                )
                return completion.choices[0].message.content.strip()

            return await asyncio.to_thread(_sync_call)

        try:
            clinician_system = "You are an expert clinician writing concise, technical summaries."
            clinician_user = (
                prompt_common
                + "Write a concise summary (150-250 words) for clinicians. "
                  "Focus on diagnoses, key findings, and recommended next steps. "
                  "Use bullet points where appropriate."
            )

            patient_system = "You explain medical information to patients in simple, reassuring language."
            patient_user = (
                prompt_common
                + "Write a friendly, easy-to-understand summary (120-200 words) for a patient. "
                  "Avoid medical jargon or explain it in simple terms. "
                  "Focus on what the results mean and what they should do next."
            )

            clinician_summary, patient_summary = await asyncio.gather(
                _call_openai(clinician_system, clinician_user),
                _call_openai(patient_system, patient_user),
            )

            return {
                "clinician": {
                    "title": "Clinician Summary",
                    "content": clinician_summary,
                },
                "patient": {
                    "title": "Patient-Friendly Summary",
                    "content": patient_summary,
                },
            }
        except Exception as e:
            logger.error(f"Error generating summaries with LLM: {e}")
            # Fallback if LLM call fails
            base = redacted_text[:600] + ("..." if len(redacted_text) > 600 else "")
            return {
                "clinician": {
                    "title": "Clinician Summary (LLM Error Fallback)",
                    "content": f"Raw excerpt (first 600 chars):\n\n{base}",
                },
                "patient": {
                    "title": "Patient Summary (LLM Error Fallback)",
                    "content": "We could not generate an AI summary due to an error. "
                               "Please try again later.",
                },
            }

    async def compare_summaries(
        self,
        original_text: str,
        clinician_summary: str,
        patient_summary: str,
    ) -> Dict[str, Any]:
        """
        Used by /api/summarize/report/{id}/compare to compare clinician vs patient summaries.
        """
        if not self.client:
            return {
                "comparison_analysis": {
                    "note": "LLM not configured. Comparison not available."
                },
                "recommendations": [],
            }

        system_msg = (
            "You are a medical communication expert comparing two summaries "
            "of the same medical report."
        )
        user_msg = (
            "Original redacted report text:\n"
            "-----------------\n"
            f"{original_text}\n"
            "-----------------\n\n"
            "Clinician-oriented summary:\n"
            "-----------------\n"
            f"{clinician_summary}\n"
            "-----------------\n\n"
            "Patient-oriented summary:\n"
            "-----------------\n"
            f"{patient_summary}\n"
            "-----------------\n\n"
            "1. Briefly compare the focus, tone, and level of detail of both summaries.\n"
            "2. Suggest 3 improvements to each.\n"
            "3. Highlight any important clinical detail that is missing from either."
        )

        def _sync_call():
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg},
                ],
                temperature=0.4,
            )
            return completion.choices[0].message.content.strip()

        try:
            text = await asyncio.to_thread(_sync_call)
            return {"comparison_analysis": {"text": text}, "recommendations": []}
        except Exception as e:
            logger.error(f"Error comparing summaries: {e}")
            return {
                "comparison_analysis": {
                    "text": "Error while comparing summaries."
                },
                "recommendations": [],
            }


# Singleton instance
llm_service = LLMService()
