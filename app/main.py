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

# Force database initialization BEFORE anything else
print("🚀 Forcing database initialization...")
try:
    from app.models import Base
    from app.database import engine, init_db
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created")
    
    # Seed database
    init_db()
    print("✅ Database initialization complete")
except Exception as e:
    print(f"⚠️ Database init error: {e}")
    import traceback
    traceback.print_exc()

# Mount static files
static_path = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_path):
    try:
        app.mount("/static", StaticFiles(directory=static_path), name="static")
    except Exception as e:
        print(f"Static files mount error: {e}")

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
