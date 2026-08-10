from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user_model import User
from app.schemas.resume_schema import ResumeCreate, ResumeOut, ResumeUpdate
from app.services.resume_service import (
    create_my_resume_service,
    get_my_resume_service,
    update_my_resume_service,
)
from app.utils.auth import get_current_candidate


router = APIRouter(prefix="/resume", tags=["Candidate Resume"])


@router.get("/me", response_model=ResumeOut)
def get_my_resume(
    current_user: User = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    return get_my_resume_service(current_user, db)


@router.post("/me", response_model=ResumeOut, status_code=status.HTTP_201_CREATED)
def create_my_resume(
    resume: ResumeCreate,
    current_user: User = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    return create_my_resume_service(resume, current_user, db)


@router.patch("/me", response_model=ResumeOut)
def update_my_resume(
    resume: ResumeUpdate,
    current_user: User = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    return update_my_resume_service(resume, current_user, db)
