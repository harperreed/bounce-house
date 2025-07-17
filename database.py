# ABOUTME: SQLAlchemy database models and repository for domain submissions
# ABOUTME: Handles database operations including storing submissions and duplicate checking

from sqlalchemy import Column, String, Integer, Float, DateTime, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import datetime
import uuid
import os
from typing import Dict, Any, Optional
from models import FormInput

Base = declarative_base()


class Submission(Base):
    __tablename__ = "submissions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    budget_cents = Column(Integer)
    domain_name = Column(String, nullable=False)
    note = Column(String)
    ip = Column(String, nullable=False)
    user_agent = Column(String)
    recaptcha_score = Column(Float)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.UTC))
    updated_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.UTC), onupdate=lambda: datetime.datetime.now(datetime.UTC))


class Repository:
    def __init__(self, db_url: Optional[str] = None):
        self.db_url = db_url or os.environ.get("DATABASE_URL", "sqlite:///domainer_capture.db")
        self.engine = create_engine(self.db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    def insert_if_new(self, form_data: FormInput, meta: Dict[str, Any]) -> Dict[str, Any]:
        """Insert a new submission if the email doesn't already exist."""
        with self.Session() as session:
            # Check for existing email
            existing = session.query(Submission).filter_by(email=form_data.email).first()
            if existing:
                return {"type": "duplicate", "submission": existing}
            
            # Create new submission
            submission = Submission(
                email=form_data.email,
                name=form_data.name,
                budget_cents=form_data.budget,
                domain_name=form_data.domain_name,
                note=form_data.note,
                ip=meta.get("ip"),
                user_agent=meta.get("user_agent"),
                recaptcha_score=meta.get("recaptcha_score")
            )
            session.add(submission)
            session.commit()
            session.refresh(submission)  # Refresh to get the latest data
            return {"type": "inserted", "submission": submission}
    
    def get_submission_by_email(self, email: str) -> Optional[Submission]:
        """Get a submission by email address."""
        with self.Session() as session:
            return session.query(Submission).filter_by(email=email).first()
    
    def get_all_submissions(self) -> list[Submission]:
        """Get all submissions."""
        with self.Session() as session:
            return session.query(Submission).all()