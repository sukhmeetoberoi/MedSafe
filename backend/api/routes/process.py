"""
Processing API endpoints
Orchestrates the complete medical report processing pipeline
"""

import asyncio
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any

from core.config import settings
from core.logging import logger
from database.database import get_db
from models.report import Report, ProcessingStatus
from services.ocr_service import ocr_service
from services.nlp_service import nlp_service
from services.phi_redaction_service import phi_redaction_service
from services.llm_service import llm_service
from services.processing_service import processing_service

router = APIRouter()

@router.post("/report/{report_id}")
async def process_medical_report(
    report_id: int,
    background_tasks: BackgroundTasks,
    include_summaries: bool = True,
    summary_types: Optional[str] = "clinician,patient",
    llm_provider: str = "auto",
    db: Session = Depends(get_db)
):
    """
    Start processing a medical report

    Args:
        report_id: Report ID to process
        background_tasks: FastAPI background tasks
        include_summaries: Whether to generate AI summaries
        summary_types: Comma-separated list of summary types
        llm_provider: LLM provider to use
        db: Database session

    Returns:
        Processing initiation response
    """
    try:
        # Get report from database
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")

        # Check if report is already being processed
        if report.status in [ProcessingStatus.OCR_PROCESSING, ProcessingStatus.PHI_REDACTING,
                           ProcessingStatus.NLP_PROCESSING, ProcessingStatus.SUMMARIZING]:
            raise HTTPException(status_code=400, detail="Report is already being processed")

        # Reset report status if failed
        if report.status == ProcessingStatus.FAILED:
            report.status = ProcessingStatus.UPLOADED
            report.processing_progress = 0.0
            report.error_message = None
            db.commit()

        # Parse summary types
        summary_type_list = []
        if include_summaries and summary_types:
            summary_type_list = [s.strip().lower() for s in summary_types.split(',') if s.strip()]

        # Add processing job to background tasks
        background_tasks.add_task(
            process_report_background,
            report_id,
            include_summaries,
            summary_type_list,
            llm_provider
        )

        logger.info(f"Started processing for report {report_id}")

        return {
            "success": True,
            "message": "Processing started successfully",
            "report_id": report_id,
            "processing_steps": [
                "1. OCR text extraction",
                "2. PHI redaction",
                "3. NLP processing",
                "4. AI summarization" if include_summaries else None
            ],
            "estimated_time": "2-5 minutes"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting processing for report {report_id}: {e}")
        raise HTTPException(status_code=500, detail="Error starting report processing")

@router.get("/status/{report_id}")
async def get_processing_status(report_id: int, db: Session = Depends(get_db)):
    """
    Get detailed processing status for a report

    Args:
        report_id: Report ID to check
        db: Database session

    Returns:
        Detailed processing status
    """
    try:
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")

        # Get detailed status information
        status_info = {
            "report_id": report_id,
            "current_status": report.status,
            "progress_percentage": round(report.processing_progress * 100, 2),
            "created_at": report.created_at.isoformat(),
            "updated_at": report.updated_at.isoformat(),
            "error_message": report.error_message
        }

        # Add step-specific details
        if report.status == ProcessingStatus.UPLOADED:
            status_info["current_step"] = "Ready to process"
            status_info["next_step"] = "OCR text extraction"

        elif report.status == ProcessingStatus.OCR_PROCESSING:
            status_info["current_step"] = "Extracting text from document"
            status_info["description"] = "Using OCR technology to read text from medical report"

        elif report.status == ProcessingStatus.OCR_COMPLETE:
            status_info["current_step"] = "OCR completed"
            status_info["description"] = f"Extracted {len(report.extracted_text or '')} characters"
            status_info["next_step"] = "PHI redaction"
            if report.ocr_metadata:
                status_info["ocr_metadata"] = report.ocr_metadata

        elif report.status == ProcessingStatus.PHI_REDACTING:
            status_info["current_step"] = "Redacting protected health information"
            status_info["description"] = "Identifying and removing PHI for HIPAA compliance"

        elif report.status == ProcessingStatus.PHI_COMPLETE:
            status_info["current_step"] = "PHI redaction completed"
            status_info["description"] = f"Found and redacted {len(report.phi_entities or [])} PHI entities"
            status_info["next_step"] = "NLP processing"
            if report.phi_entities:
                status_info["phi_summary"] = phi_redaction_service._generate_phi_summary(report.phi_entities)

        elif report.status == ProcessingStatus.NLP_PROCESSING:
            status_info["current_step"] = "Processing with Natural Language Processing"
            status_info["description"] = "Extracting medical entities and analyzing content"

        elif report.status == ProcessingStatus.NLP_COMPLETE:
            status_info["current_step"] = "NLP processing completed"
            status_info["description"] = f"Extracted {len(report.nlp_entities or [])} medical entities"
            status_info["next_step"] = "AI summarization"
            if report.nlp_summary:
                status_info["nlp_summary"] = report.nlp_summary.get("summary", "NLP processing complete")

        elif report.status == ProcessingStatus.SUMMARIZING:
            status_info["current_step"] = "Generating AI summaries"
            status_info["description"] = "Creating clinician and patient-friendly summaries"

        elif report.status == ProcessingStatus.SUMMARIES_COMPLETE:
            status_info["current_step"] = "Summaries generated"
            status_info["description"] = "AI summaries completed successfully"
            status_info["next_step"] = "Finalizing"

        elif report.status == ProcessingStatus.COMPLETED:
            status_info["current_step"] = "Processing complete"
            status_info["description"] = "All processing steps completed successfully"
            status_info["completed_at"] = report.completed_at.isoformat() if report.completed_at else None

        elif report.status == ProcessingStatus.FAILED:
            status_info["current_step"] = "Processing failed"
            status_info["description"] = "An error occurred during processing"
            status_info["error_details"] = report.error_message

        return status_info

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting processing status for report {report_id}: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving processing status")

@router.post("/report/{report_id}/summarize")
async def generate_summaries_only(
    report_id: int,
    summary_types: str = "clinician,patient",
    llm_provider: str = "auto",
    db: Session = Depends(get_db)
):
    """
    Generate AI summaries for an already processed report

    Args:
        report_id: Report ID to summarize
        summary_types: Comma-separated list of summary types
        llm_provider: LLM provider to use
        db: Database session

    Returns:
        Summary generation response
    """
    try:
        # Check if report exists and is ready for summarization
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")

        if report.status not in [ProcessingStatus.NLP_COMPLETE, ProcessingStatus.SUMMARIES_COMPLETE, ProcessingStatus.COMPLETED]:
            raise HTTPException(
                status_code=400,
                detail="Report must complete NLP processing before summarization"
            )

        if not report.phi_redacted_text:
            raise HTTPException(status_code=400, detail="PHI redaction must be completed before summarization")

        # Parse summary types
        summary_type_list = [s.strip().lower() for s in summary_types.split(',') if s.strip()]

        # Generate summaries
        summary_results = await processing_service.generate_summaries(
            report,
            summary_type_list,
            llm_provider
        )

        return {
            "success": True,
            "report_id": report_id,
            "summaries": summary_results,
            "message": "Summaries generated successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating summaries for report {report_id}: {e}")
        raise HTTPException(status_code=500, detail="Error generating summaries")

@router.post("/report/{report_id}/qa")
async def answer_question_about_report(
    report_id: int,
    question: str,
    llm_provider: str = "auto",
    db: Session = Depends(get_db)
):
    """
    Answer a question about a processed medical report

    Args:
        report_id: Report ID
        question: User's question about the report
        llm_provider: LLM provider to use
        db: Database session

    Returns:
        Answer to the question
    """
    try:
        # Check if report exists and is processed
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")

        if report.status != ProcessingStatus.COMPLETED:
            raise HTTPException(status_code=400, detail="Report processing must be completed before Q&A")

        if not report.phi_redacted_text:
            raise HTTPException(status_code=400, detail="PHI redaction must be completed before Q&A")

        # Generate answer using LLM service
        qa_result = await llm_service.generate_qa_response(
            report.phi_redacted_text,
            question,
            llm_provider
        )

        return {
            "success": True,
            "report_id": report_id,
            "question": question,
            "answer": qa_result.get("summary", ""),
            "provider_used": qa_result.get("provider_used", "unknown"),
            "confidence": qa_result.get("confidence", 0.0),
            "disclaimer": "This is AI-generated information and should not replace professional medical advice. Please consult your healthcare provider."
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error answering question for report {report_id}: {e}")
        raise HTTPException(status_code=500, detail="Error generating answer")

async def process_report_background(
    report_id: int,
    include_summaries: bool,
    summary_types: list,
    llm_provider: str
):
    """
    Background task for processing medical report
    """
    try:
        await processing_service.process_report_pipeline(
            report_id,
            include_summaries,
            summary_types,
            llm_provider
        )
    except Exception as e:
        logger.error(f"Background processing failed for report {report_id}: {e}")
        # Update database with error status
        from database.database import SessionLocal
        db = SessionLocal()
        try:
            report = db.query(Report).filter(Report.id == report_id).first()
            if report:
                report.status = ProcessingStatus.FAILED
                report.error_message = str(e)
                db.commit()
        finally:
            db.close()