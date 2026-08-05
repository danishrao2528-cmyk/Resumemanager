from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.utils.logger import logger
from app.models.resume_model import Resume
from app.schemas.resume_schema import ResumeCreate


def get_all_resumes_service(db: Session):
    return db.query(Resume).all()


def get_resume_by_id_service(resume_id: int, db: Session):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()

    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")

    return resume


def create_resume_service(resume_data: ResumeCreate, db: Session):
    try:
        logger.info(
            "Creating resume for candidate: %s",
            resume_data.candidate_name,
        )

        new_resume = Resume(
            candidate_name=resume_data.candidate_name,
            email=resume_data.email,
            resume_text=resume_data.resume_text,
        )

        db.add(new_resume)
        db.commit()
        db.refresh(new_resume)

        logger.info(
            "Resume created successfully with ID: %s",
            new_resume.id,
        )

        return new_resume

    except Exception as error:
        db.rollback()

        logger.exception(
            "Database error while creating resume: %s",
            error,
        )

        raise RuntimeError(
            "Unable to create resume."
        ) from error


def update_resume_service(
    resume_id: int,
    updated_resume: ResumeCreate,
    db: Session,
):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()

    if resume is None:
        logger.warning("update failed: resumeID %s not found",resume_id,)
        raise HTTPException(status_code=404, detail="Resume not found")
    try:
        logger.info("updating resume id: %s",resume_id)
        resume.candidate_name = updated_resume.candidate_name
        resume.email = updated_resume.email
        resume.resume_text = updated_resume.resume_text

        db.commit()
        db.refresh(resume)
        logger.info(
            "Resume ID %s updated successfully",
            resume_id,
        )
        return resume
    except Exception as error:
        db.rollback()
        logger.exception(
            "Database error while updating the Resume ID %s:%s",
            resume_id,
            error
        )
        raise RuntimeError(
            "Unable to update resume."
        ) from error

def delete_resume_service(resume_id: int, db: Session):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()

    if resume is None:
        logger.warning("Resume id %s not found",resume_id,)
        raise HTTPException(status_code=404, detail="Resume not found")
    try:
        db.delete(resume)
        db.commit()
        logger.info("Resume id %s is successfully deleted",resume_id,)
        return {
        "message": "Resume deleted successfully",
        "resume_id": resume_id,
         }
    except Exception:
        db.rollback()
        logger.exception("Unexpected error while deleting resume. ID: %s",
            resume_id,)
        raise HTTPException(
            status_code=500,
            detail="Unable to delete resume"
        )

