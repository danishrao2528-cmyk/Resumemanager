from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


UserRole = Literal["super_admin", "admin", "candidate"]


class UserCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str = Field(min_length=8, max_length=128)

    @field_validator("full_name", "username", mode="before")
    @classmethod
    def strip_text(cls, value):
        return value.strip() if isinstance(value, str) else value

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value):
        return value.strip().lower() if isinstance(value, str) else value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not any(char.isupper() for char in value):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in value):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contain at least one number")
        return value

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class AdminCreate(UserCreate):
    """Only a Super Admin can submit this schema to create an administrator."""


class UserOut(BaseModel):
    id: int
    full_name: str
    username: str
    email: EmailStr
    role: UserRole

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    full_name: str
    username: str
    email: EmailStr
    role: UserRole


class CandidateListItem(BaseModel):
    id: int
    full_name: str
    username: str
    email: EmailStr
    has_resume: bool


class CandidateDetail(BaseModel):
    id: int
    full_name: str
    username: str
    email: EmailStr
    role: UserRole
    resume_id: int | None = None
    resume_text: str | None = None


class AdminStats(BaseModel):
    total_candidates: int
    candidates_with_resume: int
    candidates_without_resume: int
