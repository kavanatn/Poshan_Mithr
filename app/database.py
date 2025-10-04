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
    from app.models import Base, User, UserRole
    from app.auth import get_password_hash
    
    print("🔧 Initializing database...")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created")
    
    db = SessionLocal()
    try:
        # Check if admin user already exists
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if existing_admin:
            print("✅ Database already initialized")
            return
        
        print("🌱 Seeding database with initial data...")
        
        # Create admin user
        admin = User(
            username="admin",
            password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
        )
        db.add(admin)
        
        # Create headmaster user
        headmaster = User(
            username="head1",
            password=get_password_hash("pass123"),
            role=UserRole.AUTHORITY,
        )
        db.add(headmaster)
        
        # Create parent user
        parent = User(
            username="parent1",
            password=get_password_hash("pass123"),
            role=UserRole.PARENT,
        )
        db.add(parent)
        
        db.commit()
        print("✅ Database seeded successfully with 3 users")
        
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        db.rollback()
        raise
    finally:
        db.close()
# Auto-initialize database on import
import atexit

def ensure_db_initialized():
    """Ensure database is initialized - called on every cold start"""
    try:
        # Check if tables exist
        from app.models import User
        db = SessionLocal()
        try:
            db.query(User).first()
            db.close()
        except:
            # Tables don't exist, initialize
            db.close()
            init_db()
    except Exception as e:
        print(f"Database check error: {e}")

# Run on module import (every serverless function cold start)
ensure_db_initialized()
