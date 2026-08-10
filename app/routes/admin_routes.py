from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user_model import User
from app.schemas.resume_schema import AIRequirementIn, AISearchOut, ResumeOut
from app.schemas.user_schema import AdminStats, CandidateDetail, CandidateListItem
from app.services.admin_service import (
    delete_candidate_service,
    get_admin_stats_service,
    get_candidate_detail_service,
    get_candidates_service,
)
from app.services.ai_service import (
    extract_requirement_keywords,
    prefilter_resumes,
    rank_candidates,
    recommendation_from_score,
)
from app.services.resume_service import (
    get_all_resumes_admin_service,
    get_resume_admin_service,
)
from app.utils.auth import get_current_admin
from app.utils.logger import logger


router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/stats", response_model=AdminStats)
def admin_stats(
    _admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    return get_admin_stats_service(db)


@router.get("/candidates", response_model=list[CandidateListItem])
def list_candidates(
    _admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    return get_candidates_service(db)


@router.get("/candidates/{user_id}", response_model=CandidateDetail)
def candidate_detail(
    user_id: int,
    _admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    return get_candidate_detail_service(user_id, db)


@router.delete("/candidates/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_candidate(
    user_id: int,
    _admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    delete_candidate_service(user_id, db)
    return None


@router.get("/resumes", response_model=list[ResumeOut])
def all_resumes(
    _admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    return get_all_resumes_admin_service(db)


@router.get("/resumes/{resume_id}", response_model=ResumeOut)
def resume_detail(
    resume_id: int,
    _admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    return get_resume_admin_service(resume_id, db)


@router.post("/ai-search", response_model=AISearchOut)
def ai_candidate_search(
    search: AIRequirementIn,
    _admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    requirement = search.requirement.strip()
    logger.info("Admin AI candidate search started")

    try:
        keywords = extract_requirement_keywords(requirement)
        resumes = get_all_resumes_admin_service(db)
        prefiltered = prefilter_resumes(resumes, keywords, limit=20)

        if not prefiltered:
            logger.info("AI pre-filter found 0 likely candidates")
            return {
                "requirement": requirement,
                "extracted_keywords": keywords,
                "total_prefiltered": 0,
                "meaningful_matches": 0,
                "matches": [],
            }

        ranked = rank_candidates(requirement, prefiltered)
        by_key = {(item["user_id"], item["id"]): item for item in prefiltered}
        matches = []

        for item in ranked:
            try:
                user_id = int(item["user_id"])
                resume_id = int(item["resume_id"])
                score = max(0, min(100, int(item.get("match_score", 0))))
            except (KeyError, TypeError, ValueError):
                continue

            source = by_key.get((user_id, resume_id))
            if source is None or score < 60:
                continue

            matches.append(
                {
                    "user_id": user_id,
                    "resume_id": resume_id,
                    "full_name": source["full_name"],
                    "email": source["email"],
                    "match_score": score,
                    "matched_skills": [str(x) for x in item.get("matched_skills", [])][:10],
                    "missing_skills": [str(x) for x in item.get("missing_skills", [])][:10],
                    "reason": str(item.get("reason", "Relevant candidate match."))[:500],
                    "recommendation": recommendation_from_score(score),
                }
            )

        matches.sort(key=lambda x: x["match_score"], reverse=True)
        logger.info(
            "AI candidate search completed prefiltered=%s meaningful=%s",
            len(prefiltered),
            len(matches),
        )
        return {
            "requirement": requirement,
            "extracted_keywords": keywords,
            "total_prefiltered": len(prefiltered),
            "meaningful_matches": len(matches),
            "matches": matches,
        }
    except RuntimeError as error:
        logger.exception("AI candidate search unavailable")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error),
        ) from error
    except Exception as error:
        logger.exception("Unexpected AI candidate search failure")
        raise HTTPException(
            status_code=500,
            detail="AI candidate search failed unexpectedly",
        ) from error
