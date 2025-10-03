"""
Main FastAPI application for Nutrition Management System
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

from app.database import engine
from app.models import Base

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Nutrition Management System",
    description="School nutrition management system",
    version="1.0.0",
)

# Mount static files
os.makedirs("app/static", exist_ok=True)
try:
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
except:
    pass

# Import routers
from app.routes import auth_routes, admin_routes, authority_routes, parent_routes

# Include routers
app.include_router(auth_routes.router)
app.include_router(admin_routes.router)
app.include_router(authority_routes.router)
app.include_router(parent_routes.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
