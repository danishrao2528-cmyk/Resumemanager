import os
from pathlib import Path

from dotenv import load_dotenv

from app.database import Base, SessionLocal, engine
from app.models.auth_session_model import AuthSession  # noqa: F401
from app.models.resume_model import Resume  # noqa: F401
from app.models.user_model import User
from app.utils.auth import hash_password


PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

SUPER_ADMIN_FULL_NAME = os.getenv("SUPER_ADMIN_FULL_NAME", "System Admin")
SUPER_ADMIN_USERNAME = os.getenv("SUPER_ADMIN_USERNAME", "admin")
SUPER_ADMIN_EMAIL = os.getenv("SUPER_ADMIN_EMAIL", "admin@resumemanager.com").strip().lower()


def create_super_admin():
    # New name is preferred, but ADMIN_PASSWORD is kept as a fallback so your
    # existing .env/deployment variable does not suddenly stop working.
    password = os.getenv("SUPER_ADMIN_PASSWORD") or os.getenv("ADMIN_PASSWORD")

    if not password:
        raise RuntimeError(
            "SUPER_ADMIN_PASSWORD is missing. Add it to .env or deployment variables."
        )

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        existing_user = (
            db.query(User)
            .filter(
                (User.email == SUPER_ADMIN_EMAIL)
                | (User.username == SUPER_ADMIN_USERNAME)
            )
            .first()
        )

        if existing_user:
            existing_user.full_name = SUPER_ADMIN_FULL_NAME
            existing_user.username = SUPER_ADMIN_USERNAME
            existing_user.email = SUPER_ADMIN_EMAIL
            existing_user.password_hash = hash_password(password)
            existing_user.role = "super_admin"
            db.commit()
            db.refresh(existing_user)
            print("Existing account promoted/updated as Super Admin.")
            print(f"Super Admin email: {existing_user.email}")
            return

        super_admin = User(
            full_name=SUPER_ADMIN_FULL_NAME,
            username=SUPER_ADMIN_USERNAME,
            email=SUPER_ADMIN_EMAIL,
            password_hash=hash_password(password),
            role="super_admin",
        )
        db.add(super_admin)
        db.commit()
        db.refresh(super_admin)
        print("Super Admin created successfully.")
        print(f"Super Admin email: {super_admin.email}")

    except Exception as error:
        db.rollback()
        print(f"Failed to create/update Super Admin: {error}")
        raise
    finally:
        db.close()


# Backward-compatible function name if you previously imported create_admin().
def create_admin():
    create_super_admin()


if __name__ == "__main__":
    create_super_admin()
