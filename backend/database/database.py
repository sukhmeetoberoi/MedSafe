"""
Database configuration and connection management
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from core.config import settings
from core.logging import logger

# SQLAlchemy setup
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ✅ Single shared Base for all models
Base = declarative_base()


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables and run basic migrations"""
    try:
        # Import models so SQLAlchemy registers them
        import models.user
        import models.report
        import models.summary

        Base.metadata.create_all(bind=engine)
        logger.info("Database tables verified/created successfully")

        # --- MANUAL SCHEMA UPDATES (for existing SQLite files) ---
        from sqlalchemy import inspect, text
        inspector = inspect(engine)
        columns = [c["name"] for c in inspector.get_columns("reports")]
        
        needed_columns = [
            ("phi_redacted_text", "TEXT"),
            ("phi_redacted_pages", "TEXT"),
            ("phi_report", "TEXT")
        ]
        
        with engine.connect() as conn:
            for col_name, col_type in needed_columns:
                if col_name not in columns:
                    logger.info(f"Adding missing column '{col_name}' to 'reports' table...")
                    conn.execute(text(f"ALTER TABLE reports ADD COLUMN {col_name} {col_type}"))
                    conn.commit()
            
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


def drop_db():
    """Drop all database tables (for testing)"""
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("Database tables dropped successfully")
    except Exception as e:
        logger.error(f"Error dropping database tables: {e}")
        raise
