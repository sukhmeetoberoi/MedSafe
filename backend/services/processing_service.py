"""
Processing Service - Main orchestrator for medical report processing
Coordinates OCR, NLP, PHI redaction, and LLM summarization
"""

import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from core.config import settings
from core.logging import logger
from database.database import SessionLocal
from models.report import Report, ProcessingStatus
from models.summary import Summary, SummaryType, SummaryProvider
from services.ocr_service import ocr_service
from services.nlp_service import nlp_service
from services.phi_redaction_service import phi_redaction_service
from services.llm_service import llm_service

class ProcessingService:
    """Main service for orchestrating medical report processing"""

    def __init__(self):
        self.processing_steps = [
            "OCR Extraction",
            "PHI Redaction",
            "NLP Processing",
            "AI Summarization"
        ]

    async def process_report_pipeline(
        self,
        report_id: int,
        include_summaries: bool = True,
        summary_types: List[str] = None,
        llm_provider: str = "auto"
    ) -> Dict[str, Any]:
        """
        Complete processing pipeline for medical report

        Args:
            report_id: Report ID to process
            include_summaries: Whether to generate summaries
            summary_types: List of summary types to generate
            llm_provider: LLM provider to use

        Returns:
            Processing results
        """
        db = SessionLocal()
        processing_start_time = datetime.utcnow()

        try:
            # Get report
            report = db.query(Report).filter(Report.id == report_id).first()
            if not report:
                raise ValueError(f"Report {report_id} not found")

            logger.info(f"Starting processing pipeline for report {report_id}")

            # Step 1: OCR Processing
            report.status = ProcessingStatus.OCR_PROCESSING
            report.processing_progress = 0.1
            db.commit()

            ocr_result = await ocr_service.extract_text_from_file(report.file_path)
            report.extracted_text = ocr_result["text"]
            report.ocr_metadata = ocr_result

            if not report.extracted_text.strip():
                raise ValueError("No text extracted from document")

            report.status = ProcessingStatus.OCR_COMPLETE
            report.processing_progress = 0.25
            db.commit()
            logger.info(f"OCR processing completed for report {report_id}")

            # Step 2: PHI Redaction
            report.status = ProcessingStatus.PHI_REDACTING
            report.processing_progress = 0.4
            db.commit()

            phi_result = await phi_redaction_service.redact_phi(report.extracted_text)
            report.phi_entities = phi_result["phi_entities"]
            report.phi_redacted_text = phi_result["redacted_text"]

            # Generate PHI report
            phi_report = await phi_redaction_service.create_phi_report(
                report.extracted_text,
                report.phi_redacted_text
            )
            report.phi_report = phi_report["phi_redaction_report"]

            report.status = ProcessingStatus.PHI_COMPLETE
            report.processing_progress = 0.5
            db.commit()
            logger.info(f"PHI redaction completed for report {report_id}")

            # Step 3: NLP Processing
            report.status = ProcessingStatus.NLP_PROCESSING
            report.processing_progress = 0.6
            db.commit()

            nlp_result = await nlp_service.process_medical_text(report.phi_redacted_text)
            report.nlp_entities = nlp_result["entities"]
            report.nlp_summary = nlp_result

            report.status = ProcessingStatus.NLP_COMPLETE
            report.processing_progress = 0.75
            db.commit()
            logger.info(f"NLP processing completed for report {report_id}")

            # Step 4: AI Summarization (optional)
            summaries_created = []
            if include_summaries and summary_types:
                report.status = ProcessingStatus.SUMMARIZING
                report.processing_progress = 0.8
                db.commit()

                summaries_created = await self.generate_summaries(
                    report, summary_types, llm_provider
                )

                report.status = ProcessingStatus.SUMMARIES_COMPLETE
                report.processing_progress = 0.9
                db.commit()
                logger.info(f"Summaries created for report {report_id}")

            # Complete processing
            report.status = ProcessingStatus.COMPLETED
            report.processing_progress = 1.0
            report.completed_at = datetime.utcnow()
            db.commit()

            processing_time = (datetime.utcnow() - processing_start_time).total_seconds()

            logger.info(f"Processing pipeline completed for report {report_id} in {processing_time:.2f} seconds")

            return {
                "report_id": report_id,
                "status": report.status,
                "processing_time": processing_time,
                "ocr_pages": ocr_result.get("pages_count", 0),
                "phi_entities_found": len(report.phi_entities) if report.phi_entities else 0,
                "nlp_entities_found": len(report.nlp_entities) if report.nlp_entities else 0,
                "summaries_created": len(summaries_created),
                "success": True
            }

        except Exception as e:
            # Update with error status
            report.status = ProcessingStatus.FAILED
            report.error_message = str(e)
            report.processing_progress = 0.0
            db.commit()

            logger.error(f"Processing pipeline failed for report {report_id}: {e}")
            raise

        finally:
            db.close()

    async def generate_summaries(
        self,
        report: Report,
        summary_types: List[str],
        llm_provider: str = "auto"
    ) -> List[Summary]:
        """
        Generate AI summaries for a processed report

        Args:
            report: Report model instance
            summary_types: List of summary types to generate
            llm_provider: LLM provider to use

        Returns:
            List of created summaries
        """
        db = SessionLocal()
        summaries_created = []

        try:
            for summary_type in summary_types:
                if summary_type not in [s.value for s in SummaryType]:
                    logger.warning(f"Unknown summary type: {summary_type}")
                    continue

                logger.info(f"Generating {summary_type} summary for report {report.id}")

                # Generate summary using LLM service with fallback
                try:
                    summary_result = await llm_service.generate_summary(
                        report.phi_redacted_text,
                        summary_type,
                        llm_provider
                    )
                except Exception as llm_error:
                    logger.warning(f"LLM service failed for report {report.id}, using fallback: {llm_error}")
                    # Fallback: Create basic summary from extracted text
                    summary_result = self._create_fallback_summary(report.phi_redacted_text, summary_type)

                # Create summary record
                summary = Summary(
                    report_id=report.id,
                    summary_type=SummaryType(summary_type),
                    provider=SummaryProvider(summary_result.get("provider", "fallback")),
                    model_name=summary_result.get("model", "unknown"),
                    content=summary_result.get("summary", ""),
                    confidence_score=summary_result.get("confidence", 0.0),
                    processing_time=summary_result.get("processing_time", 0.0),
                    tokens_used=summary_result.get("usage", {}),
                    title=f"{summary_type.title()} Summary"
                )

                db.add(summary)
                summaries_created.append(summary)

            db.commit()

            # Update report status
            if summaries_created:
                report.status = ProcessingStatus.SUMMARIES_COMPLETE
                db.commit()

            return summaries_created

        except Exception as e:
            logger.error(f"Error generating summaries for report {report.id}: {e}")
            db.rollback()
            raise

        finally:
            db.close()

    async def get_processing_progress(self, report_id: int) -> Dict[str, Any]:
        """
        Get current processing progress for a report

        Args:
            report_id: Report ID

        Returns:
            Progress information
        """
        db = SessionLocal()
        try:
            report = db.query(Report).filter(Report.id == report_id).first()
            if not report:
                return {"error": "Report not found"}

            progress_info = {
                "report_id": report_id,
                "status": report.status,
                "progress": report.processing_progress,
                "current_step": self._get_current_step(report.status),
                "error_message": report.error_message,
                "created_at": report.created_at.isoformat(),
                "updated_at": report.updated_at.isoformat()
            }

            # Add step-specific information
            if report.ocr_metadata:
                progress_info["ocr_info"] = report.ocr_metadata

            if report.phi_entities:
                progress_info["phi_count"] = len(report.phi_entities)

            if report.nlp_entities:
                progress_info["nlp_count"] = len(report.nlp_entities)

            # Get summary count
            summary_count = db.query(Summary).filter(Summary.report_id == report_id).count()
            progress_info["summary_count"] = summary_count

            return progress_info

        finally:
            db.close()

    def _get_current_step(self, status: str) -> str:
        """Get current processing step based on status"""
        step_map = {
            ProcessingStatus.UPLOADED: "Ready to process",
            ProcessingStatus.OCR_PROCESSING: "Extracting text (OCR)",
            ProcessingStatus.OCR_COMPLETE: "Text extraction complete",
            ProcessingStatus.PHI_REDACTING: "Redacting PHI",
            ProcessingStatus.PHI_COMPLETE: "PHI redaction complete",
            ProcessingStatus.NLP_PROCESSING: "NLP processing",
            ProcessingStatus.NLP_COMPLETE: "NLP processing complete",
            ProcessingStatus.SUMMARIZING: "Generating AI summaries",
            ProcessingStatus.SUMMARIES_COMPLETE: "Summaries complete",
            ProcessingStatus.COMPLETED: "Processing complete",
            ProcessingStatus.FAILED: "Processing failed"
        }
        return step_map.get(status, "Unknown status")

    async def retry_processing(
        self,
        report_id: int,
        from_step: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retry processing from a specific step or from the beginning

        Args:
            report_id: Report ID to retry
            from_step: Step to retry from (None for beginning)

        Returns:
            Retry processing results
        """
        db = SessionLocal()
        try:
            report = db.query(Report).filter(Report.id == report_id).first()
            if not report:
                raise ValueError(f"Report {report_id} not found")

            # Reset status based on retry step
            step_reset_map = {
                "ocr": ProcessingStatus.UPLOADED,
                "phi": ProcessingStatus.OCR_COMPLETE,
                "nlp": ProcessingStatus.PHI_COMPLETE,
                "summaries": ProcessingStatus.NLP_COMPLETE
            }

            if from_step and from_step.lower() in step_reset_map:
                report.status = step_reset_map[from_step.lower()]
                report.processing_progress = self._get_progress_for_step(from_step.lower())
            else:
                report.status = ProcessingStatus.UPLOADED
                report.processing_progress = 0.0

            report.error_message = None
            db.commit()

            logger.info(f"Retrying processing for report {report_id} from step: {from_step or 'beginning'}")

            # Start processing pipeline
            result = await self.process_report_pipeline(
                report_id,
                include_summaries=True,
                summary_types=["clinician", "patient"],
                llm_provider="auto"
            )

            return {
                "success": True,
                "report_id": report_id,
                "retried_from": from_step or "beginning",
                "result": result
            }

        except Exception as e:
            logger.error(f"Error retrying processing for report {report_id}: {e}")
            raise

        finally:
            db.close()

    def _get_progress_for_step(self, step: str) -> float:
        """Get progress percentage for a given step"""
        progress_map = {
            "ocr": 0.25,
            "phi": 0.5,
            "nlp": 0.75,
            "summaries": 0.9
        }
        return progress_map.get(step.lower(), 0.0)

    async def get_processing_statistics(self) -> Dict[str, Any]:
        """
        Get overall processing statistics

        Returns:
            Processing statistics
        """
        db = SessionLocal()
        try:
            # Count reports by status
            status_counts = {}
            for status in ProcessingStatus:
                count = db.query(Report).filter(Report.status == status).count()
                status_counts[status.value] = count

            # Get total reports
            total_reports = db.query(Report).count()

            # Get completed reports with processing time
            completed_reports = db.query(Report).filter(
                Report.status == ProcessingStatus.COMPLETED
            ).all()

            processing_times = []
            for report in completed_reports:
                if report.completed_at and report.created_at:
                    processing_time = (report.completed_at - report.created_at).total_seconds()
                    processing_times.append(processing_time)

            avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0

            # Get summary statistics
            total_summaries = db.query(Summary).count()
            summaries_by_type = {}
            for summary_type in SummaryType:
                count = db.query(Summary).filter(Summary.summary_type == summary_type).count()
                summaries_by_type[summary_type.value] = count

            return {
                "total_reports": total_reports,
                "status_distribution": status_counts,
                "completed_reports": len(completed_reports),
                "average_processing_time": round(avg_processing_time, 2),
                "total_summaries": total_summaries,
                "summaries_by_type": summaries_by_type,
                "success_rate": round((len(completed_reports) / max(1, total_reports)) * 100, 2)
            }

        finally:
            db.close()

    def _create_fallback_summary(self, text: str, summary_type: str) -> Dict[str, Any]:
        """
        Create a basic fallback summary without using external LLM services

        Args:
            text: The redacted medical text
            summary_type: Type of summary (clinician/patient)

        Returns:
            Basic summary result
        """
        if not text or not text.strip():
            return {
                "summary": "No text content available for summarization.",
                "provider": "fallback",
                "model": "basic",
                "confidence": 0.5,
                "processing_time": 0.1,
                "usage": {}
            }

        # Limit text length for processing
        text_sample = text[:2000] if len(text) > 2000 else text

        if summary_type == "clinician":
            summary = self._create_clinician_fallback(text_sample)
        elif summary_type == "patient":
            summary = self._create_patient_fallback(text_sample)
        else:
            summary = f"Summary for {summary_type}: {text_sample[:300]}..."

        return {
            "summary": summary,
            "provider": "fallback",
            "model": "basic_extractor",
            "confidence": 0.7,
            "processing_time": 0.2,
            "usage": {}
        }

    def _create_clinician_fallback(self, text: str) -> str:
        """Create a basic clinician-focused summary"""
        # Extract key medical information patterns
        sentences = text.split('.')[:10]  # First 10 sentences
        key_findings = []

        # Look for medical keywords
        medical_keywords = ['diagnosis', 'treatment', 'medication', 'blood pressure', 'heart rate',
                          'temperature', 'lab results', 'x-ray', 'mri', 'ct scan', 'ultrasound']

        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and any(keyword.lower() in sentence.lower() for keyword in medical_keywords):
                key_findings.append(sentence)

        if key_findings:
            return f"""CLINICAL SUMMARY

Key Findings:
{chr(10).join(f"• {finding}" for finding in key_findings[:5])}

Text Length: {len(text)} characters
Extraction Method: Basic Pattern Recognition
Note: This is a basic summary. For comprehensive analysis, configure AI service API keys.
"""
        else:
            return f"""CLINICAL SUMMARY

Document contains {len(text)} characters of medical text.
No specific medical patterns detected in automatic analysis.

Recommendation: Review full document manually for complete clinical assessment.
Extraction Method: Basic Text Analysis
"""

    def _create_patient_fallback(self, text: str) -> str:
        """Create a basic patient-friendly summary"""
        # Simplify medical content for patient understanding
        sentences = [s.strip() for s in text.split('.') if s.strip()]

        summary = f"""PATIENT SUMMARY

Your medical report has been processed and contains approximately {len(text)} characters of medical information.

What was found:
• Document has been automatically analyzed for your safety
• Personal health information has been protected
• Key medical information has been identified

Important Notes:
• This is a basic summary of your medical report
• Please discuss the complete report with your healthcare provider
• Ask your doctor to explain any medical terms you don't understand
• Keep this report for your personal health records

For personalized explanation of your results, please consult with your healthcare provider.

Processing completed successfully with privacy protection.
"""
        return summary

# Singleton instance
processing_service = ProcessingService()