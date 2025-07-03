# manages DB connection
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# DB engine for SQLAlchemy to connect
engine = create_engine(SQLALCHEMY_DATABASE_URL)
# DB session class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base class for ORM models
Base = declarative_base()

# Dependency to inject DB session into FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
