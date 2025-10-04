from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Get database URL from Vercel environment (Postgres) or use SQLite locally
DATABASE_URL = os.environ.get(
    "POSTGRES_URL",
    "sqlite:///./nutrition_app.db"
)

# Fix for SQLAlchemy (Vercel uses postgres:// but SQLAlchemy needs postgresql://)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Create engine
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

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
