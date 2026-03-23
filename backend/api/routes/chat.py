"""
Chat and Q&A API endpoints
Allows asking questions across multiple processed medical reports
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from core.logging import logger
from database.database import get_db
from models.report import Report, ProcessingStatus
from services.llm_service import llm_service

router = APIRouter()

@router.get("/qa")
async def chat_with_reports(
    question: str,
    report_ids: List[int] = Query(...),
    llm_provider: str = "auto",
    db: Session = Depends(get_db)
):
    """
    Ask a question based on one or more processed medical reports.
    
    Args:
        question: The user's question
        report_ids: List of report IDs to use as context
        llm_provider: LLM provider to use
        db: Database session
    """
    try:
        context_chunks = []
        
        for rid in report_ids:
            report = db.query(Report).filter(Report.id == rid).first()
            if not report:
                continue
                
            if report.status != ProcessingStatus.COMPLETED and report.status != ProcessingStatus.SUMMARIES_COMPLETE:
                # We can still chat if summaries are being generated or completed
                pass
            
            if not report.phi_redacted_pages:
                # Fallback to full redacted text if pages are missing
                if report.phi_redacted_text:
                    context_chunks.append({
                        "filename": report.original_filename,
                        "page_number": 1,
                        "text": report.phi_redacted_text
                    })
                continue
            
            # Add each redacted page to the context
            for page in report.phi_redacted_pages:
                context_chunks.append({
                    "filename": report.original_filename,
                    "page_number": page.get("page_number", 1),
                    "text": page.get("redacted_text", "")
                })

        if not context_chunks:
            raise HTTPException(
                status_code=400, 
                detail="No processed reports found for the given IDs. Please wait for processing to complete."
            )

        # Generate response
        qa_result = await llm_service.generate_qa_response(
            context_chunks=context_chunks,
            question=question,
            llm_provider=llm_provider
        )

        return {
            "success": True,
            "question": question,
            "answer": qa_result.get("summary", ""),
            "report_ids": report_ids,
            "provider_used": qa_result.get("provider_used", "unknown"),
            "disclaimer": "This is AI-generated information based on your reports and WHO guidelines. Consult a doctor for medical advice."
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in multi-report chat: {e}")
        raise HTTPException(status_code=500, detail="Error generating answer from reports")
