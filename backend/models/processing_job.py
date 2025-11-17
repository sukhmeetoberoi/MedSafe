"""
Processing Job database models for tracking background tasks
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum

Base = declarative_base()

class JobStatus(str, Enum):
    """Job status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class JobType(str, Enum):
    """Job type enumeration"""
    OCR = "ocr"
    PHI_REDACTION = "phi_redaction"
    NLP_PROCESSING = "nlp_processing"
    SUMMARY_GENERATION = "summary_generation"
    FULL_PROCESSING = "full_processing"

class ProcessingJob(Base):
    """Background processing job model"""
    __tablename__ = "processing_jobs"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=False, index=True)

    # Job identification
    job_type = Column(String(50), nullable=False)
    job_id = Column(String(100), unique=True, index=True, nullable=False)  # Unique job identifier

    # Status and progress
    status = Column(String(20), default=JobStatus.PENDING)
    progress = Column(Float, default=0.0)  # 0.0 to 1.0
    current_step = Column(String(100), nullable=True)

    # Configuration and parameters
    parameters = Column(JSON, nullable=True)

    # Results and outputs
    result = Column(JSON, nullable=True)
    output_files = Column(JSON, nullable=True)  # List of generated files
    error_message = Column(Text, nullable=True)
    error_details = Column(JSON, nullable=True)

    # Performance metrics
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    processing_time = Column(Float, nullable=True)  # Total time in seconds

    # Retry information
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)

    # Metadata
    metadata = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    report = relationship("Report")

    def __repr__(self):
        return f"<ProcessingJob(id={self.id}, type={self.job_type}, status={self.status})>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "report_id": self.report_id,
            "job_type": self.job_type,
            "job_id": self.job_id,
            "status": self.status,
            "progress": self.progress,
            "current_step": self.current_step,
            "parameters": self.parameters,
            "result": self.result,
            "output_files": self.output_files,
            "error_message": self.error_message,
            "error_details": self.error_details,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "processing_time": self.processing_time,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }