from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create SQLite database
SQLALCHEMY_DATABASE_URL = "sqlite:///./jobs.db"

# Create engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class
Base = declarative_base()

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, unique=True, index=True)
    external_id = Column(String, nullable=True)
    original_id = Column(String, nullable=True)
    headline = Column(String)
    description = Column(Text)
    webpage_url = Column(String)
    logo_url = Column(String, nullable=True)
    application_deadline = Column(DateTime, nullable=True)
    number_of_vacancies = Column(Integer)
    employer = Column(JSON)
    workplace_address = Column(JSON)
    must_have = Column(JSON)
    nice_to_have = Column(JSON)
    employment_type = Column(String)
    salary_type = Column(String)
    salary_description = Column(String)
    duration = Column(String)
    working_hours_type = Column(String)
    scope_of_work = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Create tables
def init_db():
    logger.info("Initializing database...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized successfully")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 