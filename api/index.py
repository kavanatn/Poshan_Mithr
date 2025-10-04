import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("=" * 60)
print("🚀 API/INDEX.PY LOADING")
print("=" * 60)

# Find Postgres URL
DATABASE_URL = None
postgres_vars = [k for k in os.environ.keys() if 'POSTGRES' in k and 'URL' in k]
print(f"\n🔍 Found {len(postgres_vars)} Postgres variables")

for key in postgres_vars:
    if 'NON_POOLING' not in key and 'PRISMA' not in key:
        DATABASE_URL = os.environ[key]
        print(f"✅ Using: {key}")
        print(f"   Value: {DATABASE_URL[:60]}...")
        break

if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./nutrition_app.db"
    print("⚠️  Using SQLite fallback")

# Fix URL
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    print("✅ Fixed postgres:// to postgresql://")

# Set environment variable
os.environ['DATABASE_URL_OVERRIDE'] = DATABASE_URL

print("\n🔧 Initializing database...")

try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.models import Base, User, UserRole
    from app.auth import get_password_hash
    
    # Create engine
    if DATABASE_URL.startswith("sqlite"):
        engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    else:
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    
    print("✅ Engine created")
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created")
    
    # Seed users
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        existing = db.query(User).filter(User.username == "admin").first()
        if not existing:
            admin = User(username="admin", password=get_password_hash("admin123"), role=UserRole.ADMIN)
            head = User(username="head1", password=get_password_hash("pass123"), role=UserRole.AUTHORITY)
            parent = User(username="parent1", password=get_password_hash("pass123"), role=UserRole.PARENT)
            
            db.add_all([admin, head, parent])
            db.commit()
            print("✅ Seeded 3 users: admin, head1, parent1")
        else:
            print("✅ Users already exist")
    finally:
        db.close()
        
    print("\n✅ DATABASE READY")
    
except Exception as e:
    print(f"\n❌ DATABASE ERROR: {e}")
    import traceback
    traceback.print_exc()

print("=" * 60)
print("✅ LOADING FASTAPI APP")
print("=" * 60 + "\n")

# Import FastAPI app
from app.main import app

# Export for Vercel
app = app
