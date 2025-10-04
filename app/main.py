"""
Main FastAPI application
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os

from app.database import engine, init_db
from app.models import Base

# Initialize FastAPI app
app = FastAPI(
    title="Nutrition Management System",
    description="School nutrition management system",
    version="1.0.0",
)

# CORS middleware for Vercel
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
    except Exception:
        pass


# Startup event to initialize database
@app.on_event("startup")
async def startup_event():
    try:
        from app.database import init_db
        print("🚀 Starting database initialization...")
        init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"⚠️ Database initialization error: {e}")
        import traceback
        traceback.print_exc()


# Import routers
from app.routes import auth_routes, admin_routes, authority_routes, parent_routes

# Include routers
app.include_router(auth_routes.router)
app.include_router(admin_routes.router)
app.include_router(authority_routes.router)
app.include_router(parent_routes.router)


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "app": "Nutrition Management System"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
