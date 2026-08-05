from fastapi import APIRouter, Depends,HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db 
from app.services.ai_service import analyze_resume
from app.schemas.resume_schema import (
    ResumeAnalysisOut,
    ResumeCreate,
    ResumeOut,
)
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


@router.get(
    "/Aianalysis/{resume_id}",
    response_model=ResumeAnalysisOut,
)
def get_resume_analysis(
    resume_id: int,
    db: Session = Depends(get_db),
):
    
    resume = get_resume_by_id_service(resume_id, db)

    try:
        # Send the saved resume text to Gemini
        analysis = analyze_resume(resume.resume_text)

        return {
            "resume_id": resume.id,
            "candidate_name": resume.candidate_name,
            "analysis": analysis,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    except RuntimeError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error),
        ) from error

 
    
    