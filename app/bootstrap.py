from sqlalchemy.orm import Session

from .config import settings
from .db import SessionLocal
from .models import User
from .security import hash_password


def ensure_admin():
    if not settings.admin_email or not settings.admin_password:
        return
    db: Session = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == settings.admin_email).first()
        if existing:
            return
        user = User(
            email=settings.admin_email,
            hashed_password=hash_password(settings.admin_password),
            is_admin=True,
        )
        db.add(user)
        db.commit()
    finally:
        db.close()

