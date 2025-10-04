"""
Parent routes for viewing child's health information
"""

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Kid, NutritionReport, UserRole
from app.auth import get_current_user_from_cookie
from app.nutrition_calculator import calculate_age

router = APIRouter(prefix="/parent", tags=["parent"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/dashboard", response_class=HTMLResponse)
async def parent_dashboard(request: Request, db: Session = Depends(get_db)):
    """Parent dashboard showing kid's health information"""
    current_user = get_current_user_from_cookie(request, db)
    if not current_user or current_user.role != UserRole.PARENT:
        return RedirectResponse(url="/", status_code=302)

    # Get kid associated with this parent
    kid = db.query(Kid).filter(Kid.parent_id == current_user.id).first()

    if not kid:
        return templates.TemplateResponse(
            "parent_dashboard.html",
            {
                "request": request,
                "current_user": current_user,
                "error": "No child record found. Please contact school administration.",
            },
        )

    # Calculate current age
    age_years, age_months = calculate_age(kid.date_of_birth)

    # Get latest nutrition report
    latest_report = (
        db.query(NutritionReport)
        .filter(NutritionReport.kid_id == kid.id)
        .order_by(NutritionReport.report_date.desc())
        .first()
    )

    context = {
        "request": request,
        "current_user": current_user,
        "kid": kid,
        "age_years": age_years,
        "age_months": age_months,
        "latest_report": latest_report,
    }

    return templates.TemplateResponse("parent_dashboard.html", context)
