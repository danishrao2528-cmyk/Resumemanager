from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.models.user_model import User
from app.schemas.user_schema import AdminCreate
from app.utils.auth import hash_password
from app.utils.logger import logger


def get_admin_stats_service(db: Session) -> dict:
    candidates = db.query(User).filter(User.role == "candidate").all()
    with_resume = sum(1 for user in candidates if user.resume is not None)
    return {
        "total_candidates": len(candidates),
        "candidates_with_resume": with_resume,
        "candidates_without_resume": len(candidates) - with_resume,
    }


def get_candidates_service(db: Session) -> list[dict]:
    candidates = (
        db.query(User)
        .options(joinedload(User.resume))
        .filter(User.role == "candidate")
        .order_by(User.id.desc())
        .all()
    )
    return [
        {
            "id": user.id,
            "full_name": user.full_name,
            "username": user.username,
            "email": user.email,
            "has_resume": user.resume is not None,
        }
        for user in candidates
    ]


def get_candidate_detail_service(user_id: int, db: Session) -> dict:
    user = (
        db.query(User)
        .options(joinedload(User.resume))
        .filter(User.id == user_id, User.role == "candidate")
        .first()
    )
    if user is None:
        raise HTTPException(status_code=404, detail="Candidate not found")

    return {
        "id": user.id,
        "full_name": user.full_name,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "resume_id": user.resume.id if user.resume else None,
        "resume_text": user.resume.resume_text if user.resume else None,
    }


def delete_candidate_service(user_id: int, db: Session) -> None:
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    if user.role in {"admin", "super_admin"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator account cannot be deleted from the candidate endpoint",
        )
    if user.role != "candidate":
        raise HTTPException(status_code=404, detail="Candidate not found")

    try:
        db.delete(user)
        db.commit()
        logger.info("Admin deleted candidate user_id=%s and associated resume", user_id)
    except Exception as error:
        db.rollback()
        logger.exception("Failed to delete candidate user_id=%s", user_id)
        raise HTTPException(status_code=500, detail="Unable to delete candidate") from error


def get_admin_accounts_service(db: Session) -> list[User]:
    return (
        db.query(User)
        .filter(User.role.in_(["super_admin", "admin"]))
        .order_by(User.id.asc())
        .all()
    )


def create_admin_account_service(admin_data: AdminCreate, db: Session) -> User:
    email = str(admin_data.email).strip().lower()
    username = admin_data.username.strip()

    existing_user = (
        db.query(User)
        .filter(or_(User.email == email, User.username == username))
        .first()
    )
    if existing_user:
        if existing_user.email == email:
            detail = "An account with this email already exists"
        else:
            detail = "Username already exists"
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)

    try:
        admin = User(
            full_name=admin_data.full_name.strip(),
            username=username,
            email=email,
            password_hash=hash_password(admin_data.password),
            role="admin",
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        logger.info("Super Admin created administrator user_id=%s email=%s", admin.id, admin.email)
        return admin
    except HTTPException:
        raise
    except Exception as error:
        db.rollback()
        logger.exception("Failed to create administrator email=%s", email)
        raise HTTPException(status_code=500, detail="Unable to create administrator") from error
