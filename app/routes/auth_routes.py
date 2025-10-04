"""
Authentication routes for login and logout
"""

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database import get_db
from app.models import UserRole
from app.auth import (
    authenticate_user,
    create_access_token,
    get_current_user_from_cookie,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def root(request: Request, db: Session = Depends(get_db)):
    """Root endpoint - serves login page or redirects based on auth"""
    current_user = get_current_user_from_cookie(request, db)
    if current_user:
        if current_user.role == UserRole.ADMIN:
            return RedirectResponse(url="/admin/dashboard", status_code=302)
        elif current_user.role == UserRole.AUTHORITY:
            return RedirectResponse(url="/authority/dashboard", status_code=302)
        elif current_user.role == UserRole.PARENT:
            return RedirectResponse(url="/parent/dashboard", status_code=302)

    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    """Handle login form submission"""
    user = authenticate_user(db, username, password)
    if not user:
        return templates.TemplateResponse(
            "login.html", {"request": request, "error": "Invalid username or password"}
        )

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    # Redirect based on role
    if user.role == UserRole.ADMIN:
        response = RedirectResponse(url="/admin/dashboard", status_code=302)
    elif user.role == UserRole.AUTHORITY:
        response = RedirectResponse(url="/authority/dashboard", status_code=302)
    elif user.role == UserRole.PARENT:
        response = RedirectResponse(url="/parent/dashboard", status_code=302)
    else:
        return templates.TemplateResponse(
            "login.html", {"request": request, "error": "Invalid user role"}
        )

    # Set JWT token in cookie
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

    return response


@router.post("/logout")
async def logout():
    """Handle logout - clear cookie and redirect"""
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("access_token")
    return response
