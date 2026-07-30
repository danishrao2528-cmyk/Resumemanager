from sqlalchemy import Column, Integer, String, Text

from app.database import Base


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    candidate_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    resume_text = Column(Text, nullable=False)
