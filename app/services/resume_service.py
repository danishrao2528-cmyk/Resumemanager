from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.models.resume_model import Resume
from app.models.user_model import User
from app.schemas.resume_schema import ResumeCreate, ResumeUpdate
from app.utils.logger import logger


def resume_to_dict(resume: Resume) -> dict:
    return {
        "id": resume.id,
        "user_id": resume.user_id,
        "full_name": resume.user.full_name,
        "username": resume.user.username,
        "email": resume.user.email,
        "resume_text": resume.resume_text,
    }


def get_my_resume_service(current_user: User, db: Session) -> dict:
    resume = (
        db.query(Resume)
        .options(joinedload(Resume.user))
        .filter(Resume.user_id == current_user.id)
        .first()
    )

    if resume is None:
        raise HTTPException(status_code=404, detail="You have not created a resume yet")

    return resume_to_dict(resume)


def create_my_resume_service(
    resume_data: ResumeCreate,
    current_user: User,
    db: Session,
) -> dict:
    existing_resume = db.query(Resume).filter(Resume.user_id == current_user.id).first()
    if existing_resume:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You already have a resume. You can update your existing resume.",
        )

    try:
        new_resume = Resume(
            user_id=current_user.id,
            resume_text=resume_data.resume_text.strip(),
        )
        db.add(new_resume)
        db.commit()
        db.refresh(new_resume)
        logger.info("Resume created for candidate user_id=%s", current_user.id)

        new_resume.user = current_user
        return resume_to_dict(new_resume)
    except HTTPException:
        raise
    except Exception as error:
        db.rollback()
        logger.exception("Database error while creating resume for user_id=%s", current_user.id)
        raise HTTPException(
            status_code=500,
            detail="Unable to create resume",
        ) from error


def update_my_resume_service(
    resume_data: ResumeUpdate,
    current_user: User,
    db: Session,
) -> dict:
    resume = (
        db.query(Resume)
        .options(joinedload(Resume.user))
        .filter(Resume.user_id == current_user.id)
        .first()
    )
    if resume is None:
        raise HTTPException(status_code=404, detail="You have not created a resume yet")

    try:
        resume.resume_text = resume_data.resume_text.strip()
        db.commit()
        db.refresh(resume)
        logger.info("Resume updated for candidate user_id=%s", current_user.id)
        return resume_to_dict(resume)
    except Exception as error:
        db.rollback()
        logger.exception("Database error while updating resume for user_id=%s", current_user.id)
        raise HTTPException(status_code=500, detail="Unable to update resume") from error


def get_all_resumes_admin_service(db: Session) -> list[dict]:
    resumes = (
        db.query(Resume)
        .options(joinedload(Resume.user))
        .order_by(Resume.id.desc())
        .all()
    )
    return [resume_to_dict(resume) for resume in resumes]


def get_resume_admin_service(resume_id: int, db: Session) -> dict:
    resume = (
        db.query(Resume)
        .options(joinedload(Resume.user))
        .filter(Resume.id == resume_id)
        .first()
    )
    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume_to_dict(resume)
