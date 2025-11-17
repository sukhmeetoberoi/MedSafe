"""
LLM Service for AI-powered medical report summarization
Integrates with OpenAI GPT and Google Gemini for intelligent summarization
"""

import json
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import openai
import google.generativeai as genai

# Handle import errors gracefully
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from core.logging import logger
from core.config import settings

class LLMService:
    """Service for LLM-powered medical text summarization"""

    def __init__(self):
        self.openai_client = None
        self.gemini_model = None
        self.setup_clients()

    def setup_clients(self):
        """Setup LLM API clients"""
        # Setup OpenAI
        if OPENAI_AVAILABLE and settings.OPENAI_API_KEY:
            try:
                openai.api_key = settings.OPENAI_API_KEY
                self.openai_client = openai
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"Error setting up OpenAI client: {e}")
                self.openai_client = None

        # Setup Google Gemini
        if GEMINI_AVAILABLE and settings.GEMINI_API_KEY:
            try:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.gemini_model = genai.GenerativeModel('gemini-pro')
                logger.info("Google Gemini client initialized successfully")
            except Exception as e:
                logger.error(f"Error setting up Gemini client: {e}")
                self.gemini_model = None

    async def generate_summary(
        self,
        text: str,
        summary_type: str = "clinician",
        provider: str = "auto",
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """
        Generate medical report summary using LLM

        Args:
            text: Medical text to summarize
            summary_type: "clinician" or "patient"
            provider: "openai", "gemini", or "auto"
            max_tokens: Maximum tokens for summary

        Returns:
            Dictionary with summary and metadata
        """
        try:
            # Determine which provider to use
            selected_provider = self._select_provider(provider)

            # Create prompt based on summary type
            prompt = self._create_prompt(text, summary_type)

            # Generate summary
            if selected_provider == "openai":
                summary_result = await self._generate_with_openai(prompt, max_tokens)
            elif selected_provider == "gemini":
                summary_result = await self._generate_with_gemini(prompt, max_tokens)
            else:
                # Fallback to basic summarization
                summary_result = await self._basic_summary(text, summary_type)

            # Add metadata
            summary_result.update({
                "summary_type": summary_type,
                "provider_used": selected_provider,
                "input_text_length": len(text),
                "summary_length": len(summary_result.get("summary", "")),
                "timestamp": datetime.utcnow().isoformat(),
                "model_info": self._get_model_info(selected_provider)
            })

            return summary_result

        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return await self._basic_summary(text, summary_type)

    def _select_provider(self, provider: str) -> str:
        """Select which LLM provider to use"""
        if provider == "auto":
            # Prefer OpenAI, fallback to Gemini
            if self.openai_client:
                return "openai"
            elif self.gemini_model:
                return "gemini"
            else:
                return "fallback"
        elif provider == "openai" and self.openai_client:
            return "openai"
        elif provider == "gemini" and self.gemini_model:
            return "gemini"
        else:
            return "fallback"

    def _create_prompt(self, text: str, summary_type: str) -> str:
        """Create prompt based on summary type"""
        if summary_type == "clinician":
            return f"""
You are a medical AI assistant tasked with creating a clinician-oriented summary of a medical report.
Please analyze the following medical text and provide a comprehensive summary for healthcare professionals.

Requirements:
- Use precise medical terminology
- Include ICD codes if identifiable
- Highlight critical findings and abnormal values
- Note medication interactions
- Provide clinical recommendations
- Maintain medical accuracy above all else
- Be concise but thorough

Medical Report:
{text}

Please structure your summary with these sections:
1. PATIENT INFORMATION
2. KEY FINDINGS
3. LABORATORY RESULTS
4. ASSESSMENT/DIAGNOSIS
5. TREATMENT PLAN
6. RECOMMENDATIONS

Focus on information that would be most valuable for clinical decision-making.
"""

        elif summary_type == "patient":
            return f"""
You are a medical AI assistant tasked with creating a patient-friendly summary of a medical report.
Please analyze the following medical text and provide an easy-to-understand summary for patients.

Requirements:
- Use simple, clear language (avoid medical jargon)
- Explain medical terms in plain English
- Focus on what the patient needs to know
- Include actionable steps for the patient
- Use encouraging and supportive tone
- Highlight when to seek medical attention

Medical Report:
{text}

Please structure your summary with these sections:
1. What We Found
2. What This Means for You
3. Next Steps
4. When to Call Your Doctor
5. Lifestyle Recommendations

Make sure the information is accurate but easily understandable for someone without medical training.
"""

        else:
            return f"""
Please provide a balanced summary of the following medical report that would be suitable for both healthcare professionals and patients.

Medical Report:
{text}

Please include:
- Key findings
- Important medical information
- Action items
- Any concerns that need attention
"""

    async def _generate_with_openai(self, prompt: str, max_tokens: int) -> Dict[str, Any]:
        """Generate summary using OpenAI GPT"""
        try:
            response = await self.openai_client.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional medical AI assistant specializing in medical report analysis and summarization."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.3,  # Lower temperature for more consistent medical responses
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )

            summary = response.choices[0].message.content.strip()

            # Extract usage information
            usage = response.usage

            return {
                "summary": summary,
                "provider": "openai",
                "model": response.model,
                "usage": {
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens
                },
                "finish_reason": response.choices[0].finish_reason,
                "confidence": 0.9  # High confidence for OpenAI GPT-4
            }

        except Exception as e:
            logger.error(f"Error generating summary with OpenAI: {e}")
            raise

    async def _generate_with_gemini(self, prompt: str, max_tokens: int) -> Dict[str, Any]:
        """Generate summary using Google Gemini"""
        try:
            response = self.gemini_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=0.3,
                    top_p=0.8,
                    top_k=40,
                )
            )

            summary = response.text.strip()

            return {
                "summary": summary,
                "provider": "gemini",
                "model": "gemini-pro",
                "usage": {
                    "prompt_tokens": None,  # Gemini doesn't provide detailed token usage
                    "completion_tokens": None,
                    "total_tokens": None
                },
                "finish_reason": getattr(response, 'finish_reason', 'stop'),
                "confidence": 0.85  # Good confidence for Gemini
            }

        except Exception as e:
            logger.error(f"Error generating summary with Gemini: {e}")
            raise

    async def _basic_summary(self, text: str, summary_type: str) -> Dict[str, Any]:
        """Fallback basic summarization when LLM services are unavailable"""
        try:
            # Simple extractive summarization
            sentences = text.split('.')

            # Score sentences based on length and key medical terms
            medical_keywords = [
                'diagnosis', 'treatment', 'medication', 'patient', 'result',
                'normal', 'abnormal', 'high', 'low', 'condition', 'therapy'
            ]

            scored_sentences = []
            for i, sentence in enumerate(sentences):
                if sentence.strip():
                    score = len(sentence.split())
                    for keyword in medical_keywords:
                        if keyword.lower() in sentence.lower():
                            score += 5
                    scored_sentences.append((score, i, sentence.strip()))

            # Select top sentences
            scored_sentences.sort(reverse=True)
            top_sentences = [s[2] for s in scored_sentences[:5]]

            summary = '. '.join(top_sentences) + '.'

            if summary_type == "patient":
                summary = f"Here's a summary of your medical information:\n\n{summary}\n\nPlease discuss these findings with your healthcare provider for proper interpretation and guidance."
            elif summary_type == "clinician":
                summary = f"CLINICAL SUMMARY:\n\n{summary}\n\nNote: This is a basic summary. Please review the full report for complete clinical details."

            return {
                "summary": summary,
                "provider": "fallback_basic",
                "model": "extractive_summarization",
                "usage": {},
                "finish_reason": "basic_processing",
                "confidence": 0.5,  # Lower confidence for basic summarization
                "note": "Basic summarization used due to LLM service unavailability"
            }

        except Exception as e:
            logger.error(f"Error in basic summarization: {e}")
            return {
                "summary": "Unable to generate summary. Please review the original medical report.",
                "provider": "error",
                "model": None,
                "usage": {},
                "finish_reason": "error",
                "confidence": 0.0,
                "error": str(e)
            }

    def _get_model_info(self, provider: str) -> Dict[str, Any]:
        """Get information about the model being used"""
        model_info = {
            "openai": {
                "name": "GPT-4",
                "capabilities": ["medical_text_understanding", "structured_summaries", "medical_reasoning"],
                "training_cutoff": "2021-09"
            },
            "gemini": {
                "name": "Gemini Pro",
                "capabilities": ["multimodal_understanding", "medical_knowledge", "reasoning"],
                "training_cutoff": "2023-02"
            },
            "fallback": {
                "name": "Basic Extractive Summarizer",
                "capabilities": ["keyword_extraction", "sentence_scoring"],
                "training_cutoff": "N/A"
            }
        }
        return model_info.get(provider, model_info["fallback"])

    async def generate_qa_response(
        self,
        report_text: str,
        question: str,
        provider: str = "auto"
    ) -> Dict[str, Any]:
        """
        Generate answer to a question about a medical report

        Args:
            report_text: Original medical report text
            question: User's question about the report
            provider: LLM provider to use

        Returns:
            Dictionary with answer and metadata
        """
        try:
            selected_provider = self._select_provider(provider)

            prompt = f"""
You are a medical AI assistant helping users understand their medical reports.
Based on the following medical report, please answer the user's question accurately and responsibly.

Medical Report:
{report_text}

User Question: {question}

Please provide:
1. A clear, accurate answer based on the report
2. Relevant context from the report
3. If the information is not available in the report, clearly state that
4. For medical questions, include a disclaimer that this is not medical advice

Be helpful but responsible - never provide definitive medical advice and always encourage users to consult healthcare professionals.
"""

            if selected_provider == "openai":
                answer_result = await self._generate_with_openai(prompt, 500)
            elif selected_provider == "gemini":
                answer_result = await self._generate_with_gemini(prompt, 500)
            else:
                answer_result = await self._basic_qa_response(report_text, question)

            answer_result.update({
                "question": question,
                "response_type": "qa",
                "provider_used": selected_provider
            })

            return answer_result

        except Exception as e:
            logger.error(f"Error generating QA response: {e}")
            return await self._basic_qa_response(report_text, question)

    async def _basic_qa_response(self, report_text: str, question: str) -> Dict[str, Any]:
        """Basic QA response when LLM is unavailable"""
        # Simple keyword-based answer
        question_lower = question.lower()
        report_lower = report_text.lower()

        # Extract relevant sentences
        sentences = report_text.split('.')
        relevant_sentences = [
            sent.strip() for sent in sentences
            if any(word in sent.lower() for word in question_lower.split() if len(word) > 3)
        ]

        if relevant_sentences:
            answer = f"Based on the report, here's what I found:\n\n" + "\n".join(relevant_sentences[:3])
        else:
            answer = "I couldn't find specific information about your question in the report. Please review the full document or consult your healthcare provider."

        answer += "\n\nNote: This is a basic response and should not replace professional medical advice."

        return {
            "summary": answer,
            "provider": "fallback_basic",
            "model": "keyword_matching",
            "usage": {},
            "finish_reason": "basic_processing",
            "confidence": 0.3
        }

    async def compare_summaries(
        self,
        original_text: str,
        clinician_summary: str,
        patient_summary: str
    ) -> Dict[str, Any]:
        """
        Compare and analyze the quality of both summaries
        """
        try:
            comparison = {
                "text_length": {
                    "original": len(original_text),
                    "clinician": len(clinician_summary),
                    "patient": len(patient_summary),
                    "compression_ratio_clinician": len(clinician_summary) / max(1, len(original_text)),
                    "compression_ratio_patient": len(patient_summary) / max(1, len(original_text))
                },
                "readability_scores": self._calculate_readability(clinician_summary, patient_summary),
                "medical_terminology": self._analyze_medical_terminology(clinician_summary, patient_summary),
                "completeness_score": self._assess_completeness(original_text, clinician_summary, patient_summary)
            }

            return {
                "comparison_analysis": comparison,
                "recommendations": self._generate_summary_recommendations(comparison),
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error comparing summaries: {e}")
            return {"error": str(e), "timestamp": datetime.utcnow().isoformat()}

    def _calculate_readability(self, clinician_text: str, patient_text: str) -> Dict[str, Any]:
        """Calculate basic readability metrics"""
        def basic_metrics(text):
            sentences = text.split('.')
            words = text.split()
            avg_sentence_length = sum(len(sent.split()) for sent in sentences if sent.strip()) / max(1, len(sentences))
            return {
                "word_count": len(words),
                "sentence_count": len(sentences),
                "avg_sentence_length": avg_sentence_length,
                "avg_word_length": sum(len(word) for word in words) / max(1, len(words))
            }

        return {
            "clinician": basic_metrics(clinician_text),
            "patient": basic_metrics(patient_text)
        }

    def _analyze_medical_terminology(self, clinician_text: str, patient_text: str) -> Dict[str, Any]:
        """Analyze medical terminology usage"""
        medical_terms = [
            'diagnosis', 'prognosis', 'treatment', 'therapy', 'medication',
            'symptom', 'syndrome', 'pathology', 'malignant', 'benign',
            'acute', 'chronic', 'prophylaxis', 'contraindication'
        ]

        clinician_terms = sum(1 for term in medical_terms if term in clinician_text.lower())
        patient_terms = sum(1 for term in medical_terms if term in patient_text.lower())

        return {
            "clinician_medical_terms": clinician_terms,
            "patient_medical_terms": patient_terms,
            "terminology_complexity_diff": clinician_terms - patient_terms
        }

    def _assess_completeness(self, original: str, clinician: str, patient: str) -> Dict[str, Any]:
        """Assess completeness of summaries"""
        # Simple heuristic based on content overlap
        original_words = set(original.lower().split())
        clinician_words = set(clinician.lower().split())
        patient_words = set(patient.lower().split())

        clinician_overlap = len(original_words & clinician_words) / max(1, len(original_words))
        patient_overlap = len(original_words & patient_words) / max(1, len(original_words))

        return {
            "clinician_completeness": min(1.0, clinician_overlap),
            "patient_completeness": min(1.0, patient_overlap),
            "average_completeness": (clinician_overlap + patient_overlap) / 2
        }

    def _generate_summary_recommendations(self, comparison: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on comparison analysis"""
        recommendations = []

        completeness = comparison.get("completeness_score", {}).get("average_completeness", 0)
        med_terms = comparison.get("medical_terminology", {}).get("terminology_complexity_diff", 0)

        if completeness < 0.5:
            recommendations.append("Consider expanding summaries to include more key information from the original report")
        if med_terms > 5:
            recommendations.append("Patient summary uses significantly fewer medical terms - good for patient understanding")
        if med_terms < 2:
            recommendations.append("Consider if the patient summary has sufficient differentiation from clinician summary")

        return recommendations

# Singleton instance
llm_service = LLMService()