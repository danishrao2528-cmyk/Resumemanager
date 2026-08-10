from pydantic import BaseModel, EmailStr, Field


class ResumeCreate(BaseModel):
    resume_text: str = Field(min_length=10)


class ResumeUpdate(BaseModel):
    resume_text: str = Field(min_length=10)


class ResumeOut(BaseModel):
    id: int
    user_id: int
    full_name: str
    username: str
    email: EmailStr
    resume_text: str


class AIRequirementIn(BaseModel):
    requirement: str = Field(min_length=10, max_length=4000)


class AIMatchOut(BaseModel):
    user_id: int
    resume_id: int
    full_name: str
    email: EmailStr
    match_score: int
    matched_skills: list[str]
    missing_skills: list[str]
    reason: str
    recommendation: str


class AISearchOut(BaseModel):
    requirement: str
    extracted_keywords: list[str]
    total_prefiltered: int
    meaningful_matches: int
    matches: list[AIMatchOut]
