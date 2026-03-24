"""
File upload API endpoints
Handles medical report uploads with validation and processing initiation
"""

import os
from typing import Optional

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
    Depends,
    Form,
    BackgroundTasks,
)
from typing import List
from sqlalchemy.orm import Session

from core.config import settings
from core.logging import logger
from database.database import get_db
from models.report import Report, ProcessingStatus
from models.summary import Summary, SummaryType, SummaryProvider
from services.file_service import file_service
from services.processing_service import processing_service  # 👈 your pipeline service
from fastapi.background import BackgroundTasks
from services.processing_service import processing_service

router = APIRouter()


@router.post("/report")
async def upload_medical_report(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_id: Optional[int] = Form(None),
    db: Session = Depends(get_db)
):


    """
    Upload a medical report for processing
    """
    try:
        # Validate file
        await _validate_upload_file(file)

        # Save file to disk
        file_info = await file_service.save_uploaded_file(file)

        # Create database record
        report = Report(
            user_id=user_id,
            filename=file_info["filename"],
            original_filename=file.filename,
            file_path=file_info["file_path"],
            file_size=file_info["file_size"],
            file_type=file_info["file_type"],
            status=ProcessingStatus.UPLOADED.value
            if isinstance(ProcessingStatus.UPLOADED, str)
            else ProcessingStatus.UPLOADED,
        )

        db.add(report)
        db.commit()
        db.refresh(report)

        # TEMP: create a simple demo summary so frontend has something to show
        demo_summary = Summary(
            report_id=report.id,
            summary_type=SummaryType.PATIENT.value,
            provider=SummaryProvider.BASIC.value,
            title="Quick Overview",
            content=(
                f"This is a demo summary for '{report.original_filename}'. "
                "Later, your real AI pipeline will generate this summary."
            ),
        )
        db.add(demo_summary)
        db.commit()

        # ✅ Initiate processing pipeline as a background task
        background_tasks.add_task(
            processing_service.process_report_pipeline,  # async function
            report.id,
        )

        logger.info(f"Successfully uploaded report: {report.id} ({file.filename})")

        return {
            "success": True,
            "report_id": report.id,
            "filename": file.filename,
            "file_size": file_info["file_size"],
            "status": report.status,
            "message": "File uploaded successfully. Processing will begin shortly.",
            "processing_steps": [
                "OCR text extraction",
                "PHI redaction",
                "NLP processing",
                "AI summarization",
            ],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file {file.filename}: {e}")
        raise HTTPException(
            status_code=500, detail="Internal server error during file upload"
        )


@router.post("/reports")
async def upload_multiple_reports(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    user_id: Optional[int] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Upload multiple medical reports for processing
    """
    try:
        report_ids = []
        for file in files:
            # Validate file
            await _validate_upload_file(file)

            # Save file to disk
            file_info = await file_service.save_uploaded_file(file)

            # Create database record
            report = Report(
                user_id=user_id,
                filename=file_info["filename"],
                original_filename=file.filename,
                file_path=file_info["file_path"],
                file_size=file_info["file_size"],
                file_type=file_info["file_type"],
                status=ProcessingStatus.UPLOADED.value
                if isinstance(ProcessingStatus.UPLOADED, str)
                else ProcessingStatus.UPLOADED,
            )

            db.add(report)
            db.commit()
            db.refresh(report)

            # Initiate processing pipeline as a background task
            background_tasks.add_task(
                processing_service.process_report_pipeline,
                report.id,
            )
            
            report_ids.append(report.id)
            logger.info(f"Successfully uploaded batch report: {report.id} ({file.filename})")

        return {
            "success": True,
            "report_ids": report_ids,
            "message": f"{len(files)} files uploaded successfully. Processing will begin shortly.",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading multiple files: {e}")
        raise HTTPException(
            status_code=500, detail="Internal server error during batch file upload"
        )



@router.get("/status/{report_id}")
async def get_upload_status(report_id: int, db: Session = Depends(get_db)):
    """
    Get processing status for an uploaded report
    """
    try:
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")

        status_info = {
            "report_id": report.id,
            "status": report.status,
            "processing_progress": report.processing_progress,
            "error_message": report.error_message,
            "created_at": report.created_at.isoformat(),
            "updated_at": report.updated_at.isoformat(),
        }

        if report.status == ProcessingStatus.OCR_COMPLETE:
            status_info.update(
                {
                    "step": "OCR Complete",
                    "next_step": "PHI Redaction",
                    "extracted_text_length": len(report.extracted_text)
                    if report.extracted_text
                    else 0,
                }
            )
        elif report.status == ProcessingStatus.PHI_COMPLETE:
            status_info.update(
                {
                    "step": "PHI Redaction Complete",
                    "next_step": "NLP Processing",
                    "phi_entities_found": len(report.phi_entities)
                    if report.phi_entities
                    else 0,
                }
            )
        elif report.status == ProcessingStatus.NLP_COMPLETE:
            status_info.update(
                {
                    "step": "NLP Processing Complete",
                    "next_step": "AI Summarization",
                    "entities_extracted": len(report.nlp_entities)
                    if report.nlp_entities
                    else 0,
                }
            )
        elif report.status == ProcessingStatus.COMPLETED:
            status_info.update(
                {
                    "step": "Processing Complete",
                    "completed_at": report.completed_at.isoformat()
                    if report.completed_at
                    else None,
                }
            )

        return status_info

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting upload status for report {report_id}: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving upload status")


@router.delete("/{report_id}")
async def delete_report(report_id: int, db: Session = Depends(get_db)):
    """
    Delete a report and its associated files
    """
    try:
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")

        await file_service.delete_report_files(report)

        db.delete(report)
        db.commit()

        logger.info(f"Successfully deleted report: {report_id}")

        return {
            "success": True,
            "message": "Report deleted successfully",
            "report_id": report_id,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting report {report_id}: {e}")
        raise HTTPException(status_code=500, detail="Error deleting report")


@router.get("/list")
async def list_user_reports(
    user_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """
    List reports with optional filtering
    """
    try:
        query = db.query(Report)

        if user_id:
            query = query.filter(Report.user_id == user_id)
        if status_filter:
            query = query.filter(Report.status == status_filter)

        reports = (
            query.order_by(Report.created_at.desc()).offset(offset).limit(limit).all()
        )
        total = query.count()

        return {
            "reports": [report.to_dict() for report in reports],
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    except Exception as e:
        logger.error(f"Error listing reports: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving reports")


async def _validate_upload_file(file: UploadFile):
    """Validate uploaded file for medical report processing"""

    # Check filename
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    # Compute file size from underlying file object
    size = None
    try:
        file.file.seek(0, os.SEEK_END)
        size = file.file.tell()
        file.file.seek(0)
    except Exception as e:
        logger.warning(f"Could not determine file size for {file.filename}: {e}")

    if size is not None and size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {settings.MAX_FILE_SIZE // (1024*1024)}MB",
        )

    # Check file type
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in settings.ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"File type not supported. Allowed types: {', '.join(settings.ALLOWED_FILE_TYPES)}",
        )

    # Check MIME type (non-blocking)
    content_type = file.content_type
    allowed_mime_types = {
        ".pdf": ["application/pdf"],
        ".jpg": ["image/jpeg"],
        ".jpeg": ["image/jpeg"],
        ".png": ["image/png"],
        ".tiff": ["image/tiff"],
        ".tif": ["image/tiff"],
    }

    if file_ext in allowed_mime_types and content_type not in allowed_mime_types[file_ext]:
        logger.warning(f"Content type mismatch for {file.filename}: {content_type}")

    return True
