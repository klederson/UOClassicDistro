from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import User
from ..security import verify_password
from ..deps import get_current_user


router = APIRouter(tags=["auth"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@router.post("/login")
def login_action(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user: User | None = db.query(User).filter(User.email == email).first()
    error = None
    if user is None or not verify_password(password, user.hashed_password):
        error = "Credenciais inválidas"
        return templates.TemplateResponse("login.html", {"request": request, "error": error}, status_code=400)

    request.session["user_id"] = user.id
    response = RedirectResponse(url="/", status_code=303)
    return response


@router.post("/logout")
def logout_action(request: Request, current_user=Depends(get_current_user)):
    if "user_id" in request.session:
        request.session.pop("user_id")
    return RedirectResponse(url="/login", status_code=303)

