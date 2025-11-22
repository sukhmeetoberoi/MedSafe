"""
LLM Service (Final Fixed Version)
Gemini primary, fallback summarizer secondary.
"""

import asyncio
import json
from typing import Dict, Any, Optional

from core.config import settings
from core.logging import logger
from models.summary import SummaryProvider

# Try loading Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    genai = None
    GEMINI_AVAILABLE = False


class LLMService:
    def __init__(self):
        self.gemini_api_key = settings.GEMINI_API_KEY or settings.GOOGLE_API_KEY
        self.model_name = settings.GEMINI_MODEL
        self.model = None

        self.active_provider = SummaryProvider.BASIC
        self._setup_gemini()

    def _setup_gemini(self):
        """Initialize Gemini model correctly"""
        if not self.gemini_api_key:
            logger.warning("Gemini API Key missing -> Using fallback summaries.")
            return

        if not GEMINI_AVAILABLE:
            logger.warning("google-generativeai not installed.")
            return

        try:
            genai.configure(api_key=self.gemini_api_key)
            self.model = genai.GenerativeModel(self.model_name)
            self.active_provider = SummaryProvider.GEMINI
            logger.info(f"Gemini model loaded: {self.model_name}")
        except Exception as e:
            logger.error(f"Gemini init failed: {e}")
            self.model = None
            self.active_provider = SummaryProvider.BASIC

    # ----------------------------------------------------
    # BASIC FALLBACK SUMMARIZER
    # ----------------------------------------------------
    def _basic_summaries(self, text: str) -> Dict[str, Any]:
        chunk = (text or "")[:700] + ("..." if len(text) > 700 else "")
        return {
            "clinician": {
                "title": "Clinician Summary (Basic Fallback)",
                "content": f"Excerpt:\n\n{chunk}"
            },
            "patient": {
                "title": "Patient Summary (Basic Fallback)",
                "content": f"This is a simplified summary:\n\n{chunk[:500]}"
            }
        }

    # ----------------------------------------------------
    # GEMINI RAW CALL (NO MIME TYPE)
    # ----------------------------------------------------
    async def _call_gemini(self, prompt: str) -> str:
        """Safely call Gemini and return text."""
        if not self.model:
            raise RuntimeError("Gemini model not initialized")

        def _sync():
            resp = self.model.generate_content(prompt)
            return resp.text

        return await asyncio.to_thread(_sync)

    # ----------------------------------------------------
    # PARSE GEMINI JSON SAFELY
    # ----------------------------------------------------
    def _parse_json(self, raw: str) -> Dict[str, Any]:
        cleaned = raw.strip()

        # remove markdown fences if present
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            if cleaned.lower().startswith("json"):
                cleaned = cleaned[4:].strip()

        try:
            data = json.loads(cleaned)
        except Exception:
            logger.warning("Gemini did not return proper JSON.")
            return {
                "clinician": {
                    "title": "Clinician Summary",
                    "content": raw
                },
                "patient": {
                    "title": "Patient Summary",
                    "content": raw[:600]
                },
            }

        return {
            "clinician": {
                "title": data.get("clinician", {}).get("title", "Clinician Summary"),
                "content": data.get("clinician", {}).get("content", "")
            },
            "patient": {
                "title": data.get("patient", {}).get("title", "Patient Summary"),
                "content": data.get("patient", {}).get("content", "")
            }
        }

    # ----------------------------------------------------
    # PUBLIC: GENERATE SUMMARIES
    # ----------------------------------------------------
    # ----------------------------------------------------
    # PUBLIC: GENERATE SUMMARIES
    # ----------------------------------------------------
    async def generate_summaries(self, redacted_text: str, extracted_fields=None):
        if not redacted_text:
            return self._basic_summaries("")

        # Build snippet from extracted_fields (if any)
        field_text = ""
        if extracted_fields:
            for k, v in extracted_fields.items():
                if isinstance(v, (dict, list)):
                    continue
                field_text += f"{k.replace('_', ' ').title()}: {v}\n"

        # ✨ RICH, STRUCTURED PROMPT
        prompt = f"""
You are an expert medical summarization assistant.

You will read a PHI-redacted medical report and return ONLY valid JSON
in exactly this format:

{{
  "clinician": {{"title": "", "content": ""}},
  "patient":   {{"title": "", "content": ""}}
}}

GENERAL RULES
- Use ONLY information clearly present in the report text.
- NEVER invent new diagnoses, numbers, or lab values.
- Do NOT include any names or identifiers (they have been redacted).
- Write clearly in English.
- Do not mention that you are an AI model.

CLINICIAN SUMMARY REQUIREMENTS
- Audience: doctor / specialist.
- Length: about 180–260 words.
- Tone: technical but readable.
- Structure the BODY text with headings in ALL CAPS, for example:
  PATIENT INFORMATION
  KEY FINDINGS
  IMPRESSION / DIFFERENTIAL DIAGNOSIS
  RECOMMENDATIONS / NEXT STEPS
- Under KEY FINDINGS and RECOMMENDATIONS, prefer short bullet points.
- Focus on: key imaging/lab findings, relevant history, and clear plan.

PATIENT SUMMARY REQUIREMENTS
- Audience: patient with no medical background.
- Length: about 160–230 words.
- Tone: calm, friendly, and reassuring.
- Avoid jargon, or briefly explain it in brackets if needed.
- Structure the BODY text in 3 parts:
  1) A short overview of what the test/report looked at.
  2) A section titled "What this means" with 3–6 bullet points explaining
     the main ideas in simple language.
  3) A section titled "Next steps" with 3–6 bullet points describing what
     usually happens next (follow-up tests, doctor visit, lifestyle advice),
     but ONLY if supported by the report.
- END with 2–3 sentences of warm reassurance, acknowledging that the
  situation can feel worrying, and encouraging the patient to work with
  their healthcare team (without giving absolute guarantees).

Return ONLY the JSON object described above, with no extra text.

PHI-redacted medical report:
--------------------
{redacted_text}
--------------------

Extracted structured fields (may be empty):
{field_text}
"""

        # Try Gemini first
        if self.model and self.active_provider == SummaryProvider.GEMINI:
            try:
                raw = await self._call_gemini(prompt)
                parsed = self._parse_json(raw)
                # keep provider metadata
                self.active_provider = SummaryProvider.GEMINI
                return parsed
            except Exception as e:
                logger.error(f"Gemini error => fallback. {e}")

        # Fallback if Gemini missing / error
        self.active_provider = SummaryProvider.BASIC
        return self._basic_summaries(redacted_text)
        if not redacted_text:
            return self._basic_summaries("")

        # Build prompt
        field_text = ""
        if extracted_fields:
            for k, v in extracted_fields.items():
                if isinstance(v, (dict, list)): continue
                field_text += f"{k}: {v}\n"

        prompt = f"""
You are an expert medical report summarization AI.

Return ONLY valid JSON in this format:

{{
  "clinician": {{"title": "", "content": ""}},
  "patient":   {{"title": "", "content": ""}}
}}

Clinician summary: 150-250 words, technical.
Patient summary: 100-200 words, simple, friendly.

PHI-redacted medical report:
--------------------
{redacted_text}
--------------------

Extracted fields:
{field_text}
"""

        # Try Gemini
        if self.model and self.active_provider == SummaryProvider.GEMINI:
            try:
                raw = await self._call_gemini(prompt)
                parsed = self._parse_json(raw)
                return parsed
            except Exception as e:
                logger.error(f"Gemini error => fallback. {e}")

        # Fallback
        return self._basic_summaries(redacted_text)

    # ----------------------------------------------------
    # PUBLIC: COMPARE SUMMARIES
    # ----------------------------------------------------
    async def compare_summaries(self, original, clinician, patient):
        if not self.model:
            return {
                "comparison_analysis": {
                    "text": "Gemini not available for comparison."
                },
                "recommendations": []
            }

        prompt = f"""
Compare two summaries of this medical report.

Original report:
{original}

Clinician summary:
{clinician}

Patient summary:
{patient}

Provide:
1) Differences in tone/detail
2) 3 improvements each
3) Missing clinical details
"""

        raw = await self._call_gemini(prompt)
        return {
            "comparison_analysis": {"text": raw},
            "recommendations": []
        }


# Singleton
llm_service = LLMService()
