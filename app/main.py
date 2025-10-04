"""
Main FastAPI application
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os

# Initialize FastAPI app FIRST
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

@app.on_event("startup")
async def startup_event():
    """This runs on EVERY cold start"""
    print("=" * 60)
    print("🚀 STARTUP EVENT TRIGGERED")
    print("=" * 60)
    
    # Check environment
    print("\n🔍 Environment check:")
    postgres_vars = [k for k in os.environ.keys() if 'POSTGRES' in k and 'URL' in k]
    print(f"   Found {len(postgres_vars)} POSTGRES_URL variables")
    for var in postgres_vars[:3]:
        val = os.environ[var]
        print(f"   - {var}: {val[:50]}...")
    
    # Find database URL
    DATABASE_URL = None
    for key in postgres_vars:
        if 'NON_POOLING' not in key and 'PRISMA' not in key:
            DATABASE_URL = os.environ[key]
            print(f"\n✅ Selected: {key}")
            break
    
    if not DATABASE_URL:
        DATABASE_URL = "sqlite:///./nutrition_app.db"
        print("\n⚠️  NO POSTGRES - Using SQLite")
    
    # Fix URL format
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        print("✅ Fixed URL format")
    
    print(f"\n🔗 Final URL: {DATABASE_URL[:70]}...")
    
    # Set override for database module
    os.environ['DATABASE_URL_OVERRIDE'] = DATABASE_URL
    
    # Initialize database
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from app.models import Base, User, UserRole
        from app.auth import get_password_hash
        
        print("\n🔧 Creating engine...")
        if DATABASE_URL.startswith("sqlite"):
            engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
        else:
            engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        
        print("✅ Engine created")
        
        print("🔧 Creating tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created")
        
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        print("🌱 Seeding database...")
        db = SessionLocal()
        try:
            existing = db.query(User).filter(User.username == "admin").first()
            if existing:
                print("✅ Users already exist")
            else:
                admin = User(username="admin", password=get_password_hash("admin123"), role=UserRole.ADMIN)
                head = User(username="head1", password=get_password_hash("pass123"), role=UserRole.AUTHORITY)
                parent = User(username="parent1", password=get_password_hash("pass123"), role=UserRole.PARENT)
                
                db.add_all([admin, head, parent])
                db.commit()
                print("✅ Seeded 3 users")
        finally:
            db.close()
            
    except Exception as e:
        print(f"\n❌ INITIALIZATION FAILED: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("✅ STARTUP COMPLETE")
    print("=" * 60 + "\n")

# Mount static files
static_path = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_path):
    try:
        app.mount("/static", StaticFiles(directory=static_path), name="static")
    except:
        pass

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
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
