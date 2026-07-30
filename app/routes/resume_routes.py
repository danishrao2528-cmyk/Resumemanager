from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.resume_schema import ResumeCreate, ResumeOut
from app.services.resume_service import (
    create_resume_service,
    delete_resume_service,
    get_all_resumes_service,
    get_resume_by_id_service,
    update_resume_service,
)

router = APIRouter(prefix="/resume", tags=["Resumes"])


@router.get("", response_model=list[ResumeOut])
def get_all_resumes(db: Session = Depends(get_db)):
    return get_all_resumes_service(db)


@router.get("/{resume_id}", response_model=ResumeOut)
def get_resume(resume_id: int, db: Session = Depends(get_db)):
    return get_resume_by_id_service(resume_id, db)


@router.post("", response_model=ResumeOut, status_code=201)
def create_resume(
    resume: ResumeCreate,
    db: Session = Depends(get_db),
):
    return create_resume_service(resume, db)


@router.put("/{resume_id}", response_model=ResumeOut)
def update_resume(
    resume_id: int,
    updated_resume: ResumeCreate,
    db: Session = Depends(get_db),
):
    return update_resume_service(resume_id, updated_resume, db)


@router.delete("/{resume_id}")
def delete_resume(resume_id: int, db: Session = Depends(get_db)):
    return delete_resume_service(resume_id, db)
