"""
Authority routes for headmaster/school administration
"""

from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime
import json

from app.database import get_db
from app.models import (
    User,
    Kid,
    Classroom,
    Measurement,
    NutritionReport,
    UserRole,
    Gender,
    VegPreference,
)
from app.auth import get_current_user_from_cookie, get_password_hash
from app.nutrition_calculator import (
    calculate_age,
    calculate_bmi,
    classify_bmi_status,
    identify_deficiencies,
    generate_diet_recommendation,
)

router = APIRouter(prefix="/authority", tags=["authority"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/dashboard", response_class=HTMLResponse)
async def authority_dashboard(request: Request, db: Session = Depends(get_db)):
    """Authority dashboard with school statistics"""
    current_user = get_current_user_from_cookie(request, db)
    if not current_user or current_user.role != UserRole.AUTHORITY:
        return RedirectResponse(url="/", status_code=302)

    # Get classrooms managed by this authority
    classrooms = (
        db.query(Classroom).filter(Classroom.authority_id == current_user.id).all()
    )

    classroom_ids = [c.id for c in classrooms]
    total_kids = (
        db.query(Kid).filter(Kid.classroom_id.in_(classroom_ids)).count()
        if classroom_ids
        else 0
    )

    # Count assessed kids (kids with nutrition reports)
    assessed_kids = 0
    if classroom_ids:
        kid_ids = [kid.id for classroom in classrooms for kid in classroom.kids]
        if kid_ids:
            assessed_kids = (
                db.query(Kid)
                .filter(Kid.id.in_(kid_ids), Kid.nutrition_reports.any())
                .count()
            )

    context = {
        "request": request,
        "current_user": current_user,
        "classrooms": classrooms,
        "total_kids": total_kids,
        "assessed_kids": assessed_kids,
    }

    return templates.TemplateResponse("authority_dashboard.html", context)


@router.get("/create-kid", response_class=HTMLResponse)
async def create_kid_form(request: Request, db: Session = Depends(get_db)):
    """Display create kid form"""
    current_user = get_current_user_from_cookie(request, db)
    if not current_user or current_user.role != UserRole.AUTHORITY:
        return RedirectResponse(url="/", status_code=302)

    classrooms = (
        db.query(Classroom).filter(Classroom.authority_id == current_user.id).all()
    )

    context = {
        "request": request,
        "current_user": current_user,
        "classrooms": classrooms,
    }

    return templates.TemplateResponse("create_kid.html", context)


@router.post("/create-kid")
async def create_kid(
    request: Request,
    kid_name: str = Form(...),
    dob: str = Form(...),
    gender: str = Form(...),
    veg_preference: str = Form(...),
    parent_username: str = Form(...),
    parent_password: str = Form(...),
    classroom_id: int = Form(...),
    db: Session = Depends(get_db),
):
    """Create a new kid account with parent credentials"""
    current_user = get_current_user_from_cookie(request, db)
    if not current_user or current_user.role != UserRole.AUTHORITY:
        return RedirectResponse(url="/", status_code=302)

    try:
        # Parse date
        dob_date = datetime.strptime(dob, "%Y-%m-%d")

        # Check if parent username already exists
        existing_user = db.query(User).filter(User.username == parent_username).first()
        if existing_user:
            classrooms = (
                db.query(Classroom)
                .filter(Classroom.authority_id == current_user.id)
                .all()
            )
            return templates.TemplateResponse(
                "create_kid.html",
                {
                    "request": request,
                    "current_user": current_user,
                    "classrooms": classrooms,
                    "error": "Parent username already exists",
                },
            )

        # Create parent user
        parent_user = User(
            username=parent_username,
            password=get_password_hash(parent_password),
            role=UserRole.PARENT,
        )
        db.add(parent_user)
        db.flush()

        # Create kid
        kid = Kid(
            name=kid_name,
            date_of_birth=dob_date,
            gender=Gender(gender),
            veg_preference=VegPreference(veg_preference),
            parent_id=parent_user.id,
            classroom_id=classroom_id,
        )
        db.add(kid)
        db.commit()

        return RedirectResponse(url="/authority/dashboard", status_code=302)

    except Exception as e:
        db.rollback()
        classrooms = (
            db.query(Classroom).filter(Classroom.authority_id == current_user.id).all()
        )
        return templates.TemplateResponse(
            "create_kid.html",
            {
                "request": request,
                "current_user": current_user,
                "classrooms": classrooms,
                "error": f"Error creating kid account: {str(e)}",
            },
        )


@router.get("/create-classroom", response_class=HTMLResponse)
async def create_classroom_form(request: Request, db: Session = Depends(get_db)):
    """Display create classroom form"""
    current_user = get_current_user_from_cookie(request, db)
    if not current_user or current_user.role != UserRole.AUTHORITY:
        return RedirectResponse(url="/", status_code=302)

    return templates.TemplateResponse(
        "create_classroom.html", {"request": request, "current_user": current_user}
    )


@router.post("/create-classroom")
async def create_classroom(
    request: Request, classroom_name: str = Form(...), db: Session = Depends(get_db)
):
    """Create a new classroom"""
    current_user = get_current_user_from_cookie(request, db)
    if not current_user or current_user.role != UserRole.AUTHORITY:
        return RedirectResponse(url="/", status_code=302)

    classroom = Classroom(name=classroom_name, authority_id=current_user.id)
    db.add(classroom)
    db.commit()

    return RedirectResponse(url="/authority/dashboard", status_code=302)


@router.get("/nutrition-calculator", response_class=HTMLResponse)
async def nutrition_calculator_form(request: Request, db: Session = Depends(get_db)):
    """Display nutrition calculator form"""
    current_user = get_current_user_from_cookie(request, db)
    if not current_user or current_user.role != UserRole.AUTHORITY:
        return RedirectResponse(url="/", status_code=302)

    # Get kids in authority's classrooms
    classrooms = (
        db.query(Classroom).filter(Classroom.authority_id == current_user.id).all()
    )
    classroom_ids = [c.id for c in classrooms]
    kids = (
        db.query(Kid).filter(Kid.classroom_id.in_(classroom_ids)).all()
        if classroom_ids
        else []
    )

    return templates.TemplateResponse(
        "nutrition_calculator.html",
        {"request": request, "current_user": current_user, "kids": kids},
    )


@router.post("/nutrition-calculator")
async def calculate_nutrition(
    request: Request,
    kid_id: int = Form(...),
    height: float = Form(...),
    weight: float = Form(...),
    db: Session = Depends(get_db),
):
    """Calculate nutrition for a kid"""
    current_user = get_current_user_from_cookie(request, db)
    if not current_user or current_user.role != UserRole.AUTHORITY:
        return RedirectResponse(url="/", status_code=302)

    # Get kid
    kid = db.query(Kid).filter(Kid.id == kid_id).first()
    if not kid:
        raise HTTPException(status_code=404, detail="Kid not found")

    # Save measurement
    measurement = Measurement(kid_id=kid_id, height=height, weight=weight)
    db.add(measurement)

    # Calculate nutrition
    age_years, age_months = calculate_age(kid.date_of_birth)
    bmi = calculate_bmi(height, weight)
    status, percentile = classify_bmi_status(bmi, age_years, kid.gender)
    deficiencies = identify_deficiencies(status, age_years)
    recommendation = generate_diet_recommendation(
        status, age_years, kid.gender, kid.veg_preference, deficiencies
    )

    # Save nutrition report
    nutrition_report = NutritionReport(
        kid_id=kid_id,
        bmi=bmi,
        bmi_percentile=percentile,
        status=status,
        deficiencies=json.dumps(deficiencies),
        recommendation=recommendation,
    )
    db.add(nutrition_report)
    db.commit()

    # Display results
    context = {
        "request": request,
        "current_user": current_user,
        "kid": kid,
        "bmi": bmi,
        "status": status.value.title(),
        "percentile": percentile,
        "deficiencies": deficiencies,
        "recommendation": recommendation,
        "age_years": age_years,
        "age_months": age_months,
    }

    return templates.TemplateResponse("nutrition_results.html", context)
