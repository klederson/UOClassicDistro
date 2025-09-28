from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import User
from ..schemas import UserCreate
from ..security import hash_password
from ..deps import require_admin


router = APIRouter(prefix="/users", tags=["users"])
templates = Jinja2Templates(directory="app/templates")


@router.get("")
def list_users(request: Request, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    users = db.query(User).order_by(User.id.asc()).all()
    return templates.TemplateResponse("users/list.html", {"request": request, "users": users})


@router.get("/new")
def new_user_form(request: Request, _: User = Depends(require_admin)):
    return templates.TemplateResponse("users/new.html", {"request": request, "error": None})


@router.post("/new")
def create_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    is_admin: bool = Form(False),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        return templates.TemplateResponse(
            "users/new.html", {"request": request, "error": "Email já existe"}, status_code=400
        )

    user = User(email=email, hashed_password=hash_password(password), is_admin=is_admin)
    db.add(user)
    db.commit()
    return RedirectResponse(url="/users", status_code=303)


@router.post("/{user_id}/delete")
def delete_user(user_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
    return RedirectResponse(url="/users", status_code=303)

