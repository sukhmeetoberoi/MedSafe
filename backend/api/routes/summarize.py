"""
Summarization API endpoints
Handles AI-powered medical report summarization
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from core.config import settings
from core.logging import logger
from database.database import get_db
from models.report import Report, ProcessingStatus
from models.summary import Summary
from services.llm_service import llm_service

router = APIRouter()

@router.get("/report/{report_id}")
async def get_report_summaries(
    report_id: int,
    summary_type: Optional[str] = Query(None, description="Filter by summary type"),
    db: Session = Depends(get_db)
):
    """
    Get all summaries for a report

    Args:
        report_id: Report ID
        summary_type: Optional filter for summary type
        db: Database session

    Returns:
        List of summaries
    """
    try:
        # Check if report exists
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")

        # Query summaries
        query = db.query(Summary).filter(Summary.report_id == report_id)

        if summary_type:
            query = query.filter(Summary.summary_type == summary_type)

        summaries = query.order_by(Summary.created_at.desc()).all()

        return {
            "success": True,
            "report_id": report_id,
            "total_summaries": len(summaries),
            "summaries": [summary.to_dict() for summary in summaries]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting summaries for report {report_id}: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving summaries")

@router.get("/{summary_id}")
async def get_summary(summary_id: int, db: Session = Depends(get_db)):
    """
    Get a specific summary by ID

    Args:
        summary_id: Summary ID
        db: Database session

    Returns:
        Summary details
    """
    try:
        summary = db.query(Summary).filter(Summary.id == summary_id).first()
        if not summary:
            raise HTTPException(status_code=404, detail="Summary not found")

        return {
            "success": True,
            "summary": summary.to_dict()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting summary {summary_id}: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving summary")

@router.post("/{summary_id}/feedback")
async def submit_summary_feedback(
    summary_id: int,
    rating: int,
    feedback: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Submit feedback for a summary

    Args:
        summary_id: Summary ID
        rating: User rating (1-5)
        feedback: Optional feedback text
        db: Database session

    Returns:
        Feedback submission response
    """
    try:
        # Validate rating
        if not 1 <= rating <= 5:
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")

        summary = db.query(Summary).filter(Summary.id == summary_id).first()
        if not summary:
            raise HTTPException(status_code=404, detail="Summary not found")

        # Update summary with feedback
        summary.user_rating = rating
        summary.user_feedback = feedback
        db.commit()

        logger.info(f"Feedback submitted for summary {summary_id}: rating={rating}")

        return {
            "success": True,
            "message": "Feedback submitted successfully",
            "summary_id": summary_id,
            "rating": rating
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting feedback for summary {summary_id}: {e}")
        raise HTTPException(status_code=500, detail="Error submitting feedback")

@router.post("/{summary_id}/bookmark")
async def toggle_bookmark(summary_id: int, db: Session = Depends(get_db)):
    """
    Toggle bookmark status for a summary

    Args:
        summary_id: Summary ID
        db: Database session

    Returns:
        Updated bookmark status
    """
    try:
        summary = db.query(Summary).filter(Summary.id == summary_id).first()
        if not summary:
            raise HTTPException(status_code=404, detail="Summary not found")

        # Toggle bookmark status
        summary.is_bookmarked = not summary.is_bookmarked
        db.commit()

        logger.info(f"Bookmark toggled for summary {summary_id}: {summary.is_bookmarked}")

        return {
            "success": True,
            "summary_id": summary_id,
            "is_bookmarked": summary.is_bookmarked,
            "message": f"Summary {'bookmarked' if summary.is_bookmarked else 'unbookmarked'} successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling bookmark for summary {summary_id}: {e}")
        raise HTTPException(status_code=500, detail="Error toggling bookmark")

@router.get("/report/{report_id}/compare")
async def compare_summaries(report_id: int, db: Session = Depends(get_db)):
    """
    Compare different summary types for a report

    Args:
        report_id: Report ID
        db: Database session

    Returns:
        Summary comparison
    """
    try:
        # Check if report exists and is processed
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")

        if report.status != ProcessingStatus.COMPLETED:
            raise HTTPException(status_code=400, detail="Report processing must be completed")

        # Get summaries for comparison
        summaries = db.query(Summary).filter(Summary.report_id == report_id).all()

        if len(summaries) < 2:
            raise HTTPException(status_code=400, detail="Need at least 2 summaries for comparison")

        # Separate summaries by type
        clinician_summary = None
        patient_summary = None

        for summary in summaries:
            if summary.summary_type == "clinician":
                clinician_summary = summary
            elif summary.summary_type == "patient":
                patient_summary = summary

        if not clinician_summary or not patient_summary:
            raise HTTPException(status_code=400, detail="Both clinician and patient summaries required for comparison")

        # Generate comparison analysis
        comparison = await llm_service.compare_summaries(
            report.phi_redacted_text,
            clinician_summary.content,
            patient_summary.content
        )

        return {
            "success": True,
            "report_id": report_id,
            "clinician_summary": {
                "id": clinician_summary.id,
                "content": clinician_summary.content,
                "confidence": clinician_summary.confidence_score,
                "provider": clinician_summary.provider
            },
            "patient_summary": {
                "id": patient_summary.id,
                "content": patient_summary.content,
                "confidence": patient_summary.confidence_score,
                "provider": patient_summary.provider
            },
            "comparison_analysis": comparison.get("comparison_analysis", {}),
            "recommendations": comparison.get("recommendations", [])
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing summaries for report {report_id}: {e}")
        raise HTTPException(status_code=500, detail="Error comparing summaries")