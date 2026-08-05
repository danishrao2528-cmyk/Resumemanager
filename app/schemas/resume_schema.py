from pydantic import BaseModel, EmailStr, Field


class ResumeCreate(BaseModel):
    candidate_name: str = Field(min_length=3)
    email: EmailStr
    resume_text: str = Field(min_length=10)


class ResumeOut(BaseModel):
    id: int
    candidate_name: str
    email: EmailStr
    resume_text: str

    class Config:
        from_attributes = True

class ResumeAnalysisOut(BaseModel):
    resume_id: int
    candidate_name: str
    analysis: str



    