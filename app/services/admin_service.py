from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.models.user_model import User
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
    if user.role == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin account cannot be deleted",
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
