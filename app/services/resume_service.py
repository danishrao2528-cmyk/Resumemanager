from fastapi import HTTPException
from sqlalchemy.orm import Session

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
    new_resume = Resume(
        candidate_name=resume_data.candidate_name,
        email=resume_data.email,
        resume_text=resume_data.resume_text,
    )

    db.add(new_resume)
    db.commit()
    db.refresh(new_resume)

    return new_resume


def update_resume_service(
    resume_id: int,
    updated_resume: ResumeCreate,
    db: Session,
):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()

    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")

    resume.candidate_name = updated_resume.candidate_name
    resume.email = updated_resume.email
    resume.resume_text = updated_resume.resume_text

    db.commit()
    db.refresh(resume)

    return resume


def delete_resume_service(resume_id: int, db: Session):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()

    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")

    db.delete(resume)
    db.commit()

    return {
        "message": "Resume deleted successfully",
        "resume_id": resume_id,
    }
