"""
Medical Report database models
"""

from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Float,
    Boolean,
    JSON,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from database.database import Base  # ✅ use the shared Base


class ProcessingStatus(str, Enum):
    """Processing status for medical reports"""

    UPLOADED = "uploaded"
    OCR_PROCESSING = "ocr_processing"
    OCR_COMPLETE = "ocr_complete"
    PHI_REDACTING = "phi_redacting"
    PHI_COMPLETE = "phi_complete"
    NLP_PROCESSING = "nlp_processing"
    NLP_COMPLETE = "nlp_complete"
    SUMMARIZING = "summarizing"
    SUMMARIES_COMPLETE = "summaries_complete"
    COMPLETED = "completed"
    FAILED = "failed"


class Report(Base):
    """Medical Report model"""
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    # File information
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(50), nullable=False)  # pdf, jpg, png, etc.

    # Processing information
    status = Column(
        String(50),
        default=ProcessingStatus.UPLOADED.value,  # ✅ store enum value (string)
        nullable=False,
    )
    processing_progress = Column(Float, default=0.0)  # 0.0 to 1.0
    error_message = Column(Text, nullable=True)

    # OCR results
    extracted_text = Column(Text, nullable=True)
    ocr_metadata = Column(JSON, nullable=True)

    # NLP processing results
    nlp_entities = Column(JSON, nullable=True)
    nlp_summary = Column(JSON, nullable=True)

    # PHI redaction
    phi_entities = Column(JSON, nullable=True)
    phi_redacted_text = Column(Text, nullable=True)
    phi_report = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="reports")
    summaries = relationship(
        "Summary",
        back_populates="report",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Report(id={self.id}, filename={self.filename}, status={self.status})>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "filename": self.filename,
            "original_filename": self.original_filename,
            "file_size": self.file_size,
            "file_type": self.file_type,
            "status": self.status,
            "processing_progress": self.processing_progress,
            "error_message": self.error_message,
            "ocr_metadata": self.ocr_metadata,
            "nlp_entities": self.nlp_entities,
            "nlp_summary": self.nlp_summary,
            "phi_entities": self.phi_entities,
            "phi_redacted_text_length": len(self.phi_redacted_text)
            if self.phi_redacted_text
            else 0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
