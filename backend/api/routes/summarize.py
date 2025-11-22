"""
Summarization API endpoints
Handles AI-powered medical report summarization
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from core.logging import logger
from database.database import get_db
from models.report import Report, ProcessingStatus
from models.summary import Summary, SummaryType
from services.llm_service import llm_service

router = APIRouter()


@router.get("/report/{report_id}")
def get_latest_report_summary(
    report_id: int,
    summary_type: str = Query("clinician"),  # "clinician" or "patient"
    db: Session = Depends(get_db),
):
    """
    Get the latest summary for a report, optionally filtered by type.

    Returns (when summary exists):
        {
          "success": true,
          "report_id": ...,
          "summary": { ...Summary.to_dict()... }
        }

    Returns (when summary not ready yet):
        {
          "success": false,
          "report_id": ...,
          "summary": null,
          "status": "...",
          "message": "Summary not generated yet"
        }
    """
    # 1) Check report exists
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    # 2) Validate summary_type
    if summary_type not in [s.value for s in SummaryType]:
        raise HTTPException(status_code=400, detail="Invalid summary_type")

    # 3) Get latest summary of that type
    summary = (
        db.query(Summary)
        .filter(
            Summary.report_id == report_id,
            Summary.summary_type == summary_type,
        )
        .order_by(Summary.created_at.desc())
        .first()
    )

    if not summary:
        # 🔹 IMPORTANT: return 200 (success: false) instead of 404
        # so frontend doesn't treat it as a hard error.
        return {
            "success": False,
            "report_id": report_id,
            "summary": None,
            "status": report.status,
            "message": "Summary not generated yet",
        }

    return {
        "success": True,
        "report_id": report_id,
        "summary": summary.to_dict(),
    }


@router.get("/report/{report_id}/all")
def get_all_summaries_for_report(
    report_id: int,
    summary_type: Optional[str] = Query(None),  # optional filter
    db: Session = Depends(get_db),
):
    """
    Get all summaries for a report.

    Returns:
        {
          "success": true,
          "report_id": ...,
          "total_summaries": N,
          "summaries": [ {..}, {..}, ... ]
        }
    """
    try:
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")

        query = db.query(Summary).filter(Summary.report_id == report_id)

        if summary_type:
            if summary_type not in [s.value for s in SummaryType]:
                raise HTTPException(status_code=400, detail="Invalid summary_type")
            query = query.filter(Summary.summary_type == summary_type)

        summaries = query.order_by(Summary.created_at.desc()).all()

        return {
            "success": True,
            "report_id": report_id,
            "total_summaries": len(summaries),
            "summaries": [s.to_dict() for s in summaries],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting summaries for report {report_id}: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving summaries")


@router.get("/{summary_id}")
async def get_summary(summary_id: int, db: Session = Depends(get_db)):
    """Get a specific summary by ID."""
    try:
        summary = db.query(Summary).filter(Summary.id == summary_id).first()
        if not summary:
            raise HTTPException(status_code=404, detail="Summary not found")

        return {
            "success": True,
            "summary": summary.to_dict(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting summary {summary_id}: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving summary")


@router.get("/report/{report_id}/compare")
async def compare_summaries(report_id: int, db: Session = Depends(get_db)):
    """
    Compare clinician vs patient summaries for a report.
    Used by the Demo tab.
    """
    try:
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")

        if report.status != ProcessingStatus.COMPLETED:
            raise HTTPException(
                status_code=400, detail="Report processing must be completed"
            )

        summaries = db.query(Summary).filter(Summary.report_id == report_id).all()

        clinician_summary = None
        patient_summary = None

        for summary in summaries:
            if summary.summary_type == SummaryType.CLINICIAN.value:
                clinician_summary = summary
            elif summary.summary_type == SummaryType.PATIENT.value:
                patient_summary = summary

        if not clinician_summary or not patient_summary:
            raise HTTPException(
                status_code=400,
                detail="Need clinician and patient summaries for comparison",
            )

        comparison = await llm_service.compare_summaries(
            report.phi_redacted_text or report.extracted_text or "",
            clinician_summary.content,
            patient_summary.content,
        )

        return {
            "success": True,
            "report_id": report_id,
            "clinician_summary": clinician_summary.to_dict(),
            "patient_summary": patient_summary.to_dict(),
            "comparison_analysis": comparison.get("comparison_analysis", {}),
            "recommendations": comparison.get("recommendations", []),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing summaries for report {report_id}: {e}")
        raise HTTPException(status_code=500, detail="Error comparing summaries")
