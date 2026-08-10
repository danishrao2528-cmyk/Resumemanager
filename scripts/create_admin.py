import os
from pathlib import Path

from dotenv import load_dotenv

from app.database import Base, SessionLocal, engine
from app.models.resume_model import Resume  # noqa: F401
from app.models.user_model import User
from app.utils.auth import hash_password


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

load_dotenv(
    PROJECT_ROOT / ".env"
)




ADMIN_FULL_NAME="System Admin"
ADMIN_USERNAME="admin"
ADMIN_EMAIL="admin@resumemanager.com"




def create_admin():
    password = os.getenv("ADMIN_PASSWORD")

    if not password:
        raise RuntimeError(
            "ADMIN_PASSWORD is missing. "
            "Add it to .env locally or Railway Variables."
        )

    Base.metadata.create_all(
        bind=engine
    )

    db = SessionLocal()

    try:
        existing_admin = (
            db.query(User)
            .filter(
                User.role == "admin"
            )
            .first()
        )

        if existing_admin:
            print(
                f"Admin already exists: "
                f"{existing_admin.email}"
            )

            # Keep the admin information consistent
            existing_admin.full_name = ADMIN_FULL_NAME
            existing_admin.username = ADMIN_USERNAME
            existing_admin.email = ADMIN_EMAIL

            # Reset the password using ADMIN_PASSWORD
            existing_admin.password_hash = (
                hash_password(password)
            )

            db.commit()
            db.refresh(existing_admin)

            print(
                "Existing admin account updated successfully."
            )

            print(
                f"Admin email: {ADMIN_EMAIL}"
            )

            return

        admin = User(
            full_name=ADMIN_FULL_NAME,
            username=ADMIN_USERNAME,
            email=ADMIN_EMAIL,
            password_hash=hash_password(
                password
            ),
            role="admin",
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        print(
            "Admin created successfully."
        )

        print(
            f"Admin email: {ADMIN_EMAIL}"
        )

    except Exception as error:
        db.rollback()

        print(
            f"Failed to create/update admin: {error}"
        )

        raise

    finally:
        db.close()




if __name__ == "__main__":
    create_admin()