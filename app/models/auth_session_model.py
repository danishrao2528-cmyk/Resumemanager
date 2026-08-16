from sqlalchemy import Column, ForeignKey, Integer, String

from app.database import Base


class AuthSession(Base):
    __tablename__ = "auth_sessions"

    id = Column(String(128), primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at = Column(Integer, nullable=False)
    last_activity_at = Column(Integer, nullable=False, index=True)
    expires_at = Column(Integer, nullable=False, index=True)
    revoked_at = Column(Integer, nullable=True)
