import os
from pathlib import Path

from dotenv import load_dotenv

from app.database import Base, SessionLocal, engine
from app.models.resume_model import Resume  # noqa: F401
from app.models.user_model import User
from app.utils.auth import hash_password


PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(PROJECT_ROOT / ".env")

ADMIN_FULL_NAME = "System Admin"
ADMIN_USERNAME = "admin"
ADMIN_EMAIL = "admin@resumemanager.com"


def create_admin():
    password = os.getenv("ADMIN_PASSWORD")
    if not password:
        raise RuntimeError("ADMIN_PASSWORD is missing from .env")

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing_admin = db.query(User).filter(User.role == "admin").first()
        if existing_admin:
            print(f"Admin already exists: {existing_admin.email}")
            return

        admin = User(
            full_name=ADMIN_FULL_NAME,
            username=ADMIN_USERNAME,
            email=ADMIN_EMAIL,
            password_hash=hash_password(password),
            role="admin",
        )
        db.add(admin)
        db.commit()
        print(f"Admin created successfully: {ADMIN_EMAIL}")
    finally:
        db.close()


if __name__ == "__main__":
    create_admin()
