"""
Main FastAPI application
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os

print("=" * 50)
print("🚀 STARTING APPLICATION")
print("=" * 50)

# Check for database environment variables
print("\n🔍 Checking environment variables:")
postgres_vars = [key for key in os.environ.keys() if 'POSTGRES' in key]
print(f"Found {len(postgres_vars)} POSTGRES variables:")
for var in postgres_vars[:5]:  # Show first 5
    print(f"  - {var}")

# Find database URL
DATABASE_URL = None
for key in os.environ:
    if 'POSTGRES' in key and 'URL' in key and 'NON_POOLING' not in key and 'PRISMA' not in key:
        DATABASE_URL = os.environ[key]
        print(f"\n✅ Using database: {key}")
        print(f"   URL preview: {DATABASE_URL[:60]}...")
        break

if not DATABASE_URL:
    print("\n⚠️  NO POSTGRES URL FOUND - Using SQLite")
    DATABASE_URL = "sqlite:///./nutrition_app.db"

# Fix postgres:// to postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    print("✅ Fixed URL format: postgres:// → postgresql://")

# Now import database with the URL set
os.environ['DATABASE_URL_OVERRIDE'] = DATABASE_URL

from app.database import engine, SessionLocal
from app.models import Base, User, UserRole
from app.auth import get_password_hash

print("\n🔧 Creating database tables...")
try:
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully")
except Exception as e:
    print(f"❌ Table creation failed: {e}")

print("\n🌱 Seeding database...")
db = SessionLocal()
try:
    existing_admin = db.query(User).filter(User.username == "admin").first()
    if existing_admin:
        print("✅ Database already has users")
    else:
        admin = User(username="admin", password=get_password_hash("admin123"), role=UserRole.ADMIN)
        headmaster = User(username="head1", password=get_password_hash("pass123"), role=UserRole.AUTHORITY)
        parent = User(username="parent1", password=get_password_hash("pass123"), role=UserRole.PARENT)
        
        db.add(admin)
        db.add(headmaster)
        db.add(parent)
        db.commit()
        print("✅ Seeded 3 users: admin, head1, parent1")
except Exception as e:
    print(f"❌ Seeding failed: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()

print("\n" + "=" * 50)
print("✅ DATABASE INITIALIZATION COMPLETE")
print("=" * 50 + "\n")

# Initialize FastAPI app
app = FastAPI(
    title="Nutrition Management System",
    description="School nutrition management system",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_path = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_path):
    try:
        app.mount("/static", StaticFiles(directory=static_path), name="static")
    except Exception as e:
        print(f"Static files error: {e}")

# Import routers
from app.routes import auth_routes, admin_routes, authority_routes, parent_routes

# Include routers
app.include_router(auth_routes.router)
app.include_router(admin_routes.router)
app.include_router(authority_routes.router)
app.include_router(parent_routes.router)

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "app": "Nutrition Management System"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
