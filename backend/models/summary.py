"""
Summary database models
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

from database.database import Base  # ✅ use the shared Base (do NOT call declarative_base())


class SummaryType(str, Enum):
    """Summary type enumeration"""
    CLINICIAN = "clinician"
    PATIENT = "patient"
    GENERAL = "general"


class SummaryProvider(str, Enum):
    """LLM provider enumeration"""
    OPENAI = "openai"
    GEMINI = "gemini"
    FALLBACK = "fallback"
    BASIC = "basic"


class Summary(Base):
    """Medical Report Summary model"""
    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=False, index=True)

    # Summary metadata
    summary_type = Column(
        String(20),
        default=SummaryType.CLINICIAN.value,  # ✅ store enum value
        nullable=False,
    )
    provider = Column(
        String(20),
        default=SummaryProvider.OPENAI.value,  # ✅ store enum value
        nullable=False,
    )
    model_name = Column(String(100), nullable=True)

    # Summary content
    title = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    structured_content = Column(JSON, nullable=True)  # For formatted/sectioned summaries

    # Quality metrics
    confidence_score = Column(Float, nullable=True)
    completeness_score = Column(Float, nullable=True)
    readability_score = Column(Float, nullable=True)

    # Processing metadata
    processing_time = Column(Float, nullable=True)  # in seconds
    tokens_used = Column(JSON, nullable=True)       # Usage statistics from LLM

    # User feedback
    user_rating = Column(Integer, nullable=True)  # 1-5 rating
    user_feedback = Column(Text, nullable=True)
    is_bookmarked = Column(Boolean, default=False)

    # Versioning
    version = Column(Integer, default=1)
    parent_summary_id = Column(Integer, ForeignKey("summaries.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    report = relationship("Report", back_populates="summaries")
    parent_summary = relationship("Summary", remote_side=[id])

    def __repr__(self):
        return f"<Summary(id={self.id}, type={self.summary_type}, provider={self.provider})>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "report_id": self.report_id,
            "summary_type": self.summary_type,
            "provider": self.provider,
            "model_name": self.model_name,
            "title": self.title,
            "content": self.content,
            "structured_content": self.structured_content,
            "confidence_score": self.confidence_score,
            "completeness_score": self.completeness_score,
            "readability_score": self.readability_score,
            "processing_time": self.processing_time,
            "tokens_used": self.tokens_used,
            "user_rating": self.user_rating,
            "user_feedback": self.user_feedback,
            "is_bookmarked": self.is_bookmarked,
            "version": self.version,
            "parent_summary_id": self.parent_summary_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
