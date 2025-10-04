"""
Admin routes for District CEO dashboard and analytics
"""

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import json

from app.database import get_db
from app.models import User, Kid, NutritionReport, NutritionStatus, UserRole
from app.auth import get_current_user_from_cookie

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    """Admin dashboard with aggregated district statistics"""
    current_user = get_current_user_from_cookie(request, db)
    if not current_user or current_user.role != UserRole.ADMIN:
        return RedirectResponse(url="/", status_code=302)

    try:
        total_kids = db.query(Kid).count()
        total_schools = db.query(User).filter(User.role == UserRole.AUTHORITY).count()

        # Get nutrition stats - pass as dict directly, not JSON string
        nutrition_stats = {"underweight": 0, "healthy": 0, "overweight": 0, "obese": 0}

        try:
            for status in NutritionStatus:
                count = (
                    db.query(NutritionReport)
                    .filter(NutritionReport.status == status)
                    .count()
                )
                nutrition_stats[status.value] = count
        except Exception as e:
            print(f"Error counting nutrition stats: {e}")

        context = {
            "request": request,
            "current_user": current_user,
            "total_kids": total_kids,
            "total_schools": total_schools,
            "nutrition_stats": nutrition_stats,  # Pass dict directly, not JSON
        }
        return templates.TemplateResponse("admin_dashboard.html", context)

    except Exception as e:
        print(f"Admin dashboard error: {e}")
        return templates.TemplateResponse(
            "admin_dashboard.html",
            {
                "request": request,
                "current_user": current_user,
                "total_kids": 0,
                "total_schools": 0,
                "nutrition_stats": {
                    "underweight": 0,
                    "healthy": 0,
                    "overweight": 0,
                    "obese": 0,
                },
            },
        )
