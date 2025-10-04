from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import sys

# Detect if running on Vercel
IS_VERCEL = os.environ.get("VERCEL", False)

if IS_VERCEL:
    # Use /tmp on Vercel (serverless)
    SQLALCHEMY_DATABASE_URL = "sqlite:////tmp/nutrition_app.db"
else:
    # Use current directory for local development
    SQLALCHEMY_DATABASE_URL = "sqlite:///./nutrition_app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database with tables and seed data"""
    from app.models import Base

    Base.metadata.create_all(bind=engine)

    # Only run seed data if database is empty
    try:
        db = SessionLocal()
        from app.models import User

        if db.query(User).count() == 0:
            db.close()
            from app.seed_data import create_seed_data

            create_seed_data()
        else:
            db.close()
    except Exception as e:
        print(f"Seed data error: {e}")
