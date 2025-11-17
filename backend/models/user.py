"""
User database models
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    """User model for authentication and user management"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # Basic information
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=True)
    full_name = Column(String(255), nullable=True)

    # Authentication
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # Professional information (optional)
    professional_title = Column(String(100), nullable=True)
    organization = Column(String(255), nullable=True)
    license_number = Column(String(100), nullable=True)
    specialization = Column(String(100), nullable=True)

    # Preferences and metadata
    preferences = Column(JSON, nullable=True)
    metadata = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # Relationships
    reports = relationship("Report", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, is_active={self.is_active})>"

    def to_dict(self):
        """Convert to dictionary (excluding sensitive information)"""
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "full_name": self.full_name,
            "professional_title": self.professional_title,
            "organization": self.organization,
            "specialization": self.specialization,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "preferences": self.preferences,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None
        }