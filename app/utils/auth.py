import os
import secrets
import time
from datetime import datetime, timezone
from pathlib import Path

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.auth_session_model import AuthSession
from app.models.user_model import User
from app.utils.logger import logger


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is required. Add it to .env or deployment variables.")

ALGORITHM = "HS256"

# One JWT can remain valid for the maximum login session.
# Idle timeout is checked separately from the JWT expiration.
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))
IDLE_TIMEOUT_MINUTES = int(os.getenv("IDLE_TIMEOUT_MINUTES", "15"))
SESSION_MAX_HOURS = int(os.getenv("SESSION_MAX_HOURS", "8"))

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return password_hash.verify(plain_password, hashed_password)
    except Exception:
        return False


def authenticate_user(email: str, password: str, db: Session):
    normalized_email = email.strip().lower()
    user = db.query(User).filter(User.email == normalized_email).first()

    if user is None or not verify_password(password, user.password_hash):
        return None

    return user


def create_auth_session(user_id: int, db: Session) -> AuthSession:
    now = int(time.time())
    session = AuthSession(
        id=secrets.token_urlsafe(32),
        user_id=user_id,
        created_at=now,
        last_activity_at=now,
        expires_at=now + (SESSION_MAX_HOURS * 60 * 60),
        revoked_at=None,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def create_access_token(user_id: int, session: AuthSession) -> str:
    now = int(time.time())
    token_expires_at = min(
        now + (ACCESS_TOKEN_EXPIRE_MINUTES * 60),
        session.expires_at,
    )

    payload = {
        "sub": str(user_id),
        "sid": session.id,
        "iat": datetime.fromtimestamp(now, tz=timezone.utc),
        "exp": datetime.fromtimestamp(token_expires_at, tz=timezone.utc),
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def _authentication_error(detail: str = "Invalid or expired token") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def _decode_identity(token: str) -> tuple[int, str]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        subject = payload.get("sub")
        session_id = payload.get("sid")

        if subject is None or not session_id:
            raise _authentication_error()

        return int(subject), str(session_id)
    except HTTPException:
        raise
    except (InvalidTokenError, ValueError, TypeError) as error:
        raise _authentication_error() from error


def _validate_user_session(
    token: str,
    db: Session,
    *,
    touch_activity: bool,
) -> tuple[User, AuthSession]:
    user_id, session_id = _decode_identity(token)
    now = int(time.time())

    auth_session = (
        db.query(AuthSession)
        .filter(
            AuthSession.id == session_id,
            AuthSession.user_id == user_id,
        )
        .first()
    )

    if auth_session is None:
        raise _authentication_error("Login session no longer exists")

    if auth_session.revoked_at is not None:
        raise _authentication_error("Login session has been logged out")

    if auth_session.expires_at <= now:
        auth_session.revoked_at = now
        db.commit()
        raise _authentication_error("Login session has expired")

    idle_seconds = IDLE_TIMEOUT_MINUTES * 60
    if now - auth_session.last_activity_at > idle_seconds:
        auth_session.revoked_at = now
        db.commit()
        raise _authentication_error("Session expired due to inactivity")

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        auth_session.revoked_at = now
        db.commit()
        raise _authentication_error("User account no longer exists")

    if touch_activity:
        auth_session.last_activity_at = now
        db.commit()

    return user, auth_session


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    user, _session = _validate_user_session(
        token,
        db,
        touch_activity=True,
    )
    return user


def get_current_user_no_touch(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Validate login without resetting the inactivity timer."""
    user, _session = _validate_user_session(
        token,
        db,
        touch_activity=False,
    )
    return user


def revoke_token_session(token: str, db: Session) -> None:
    """Best-effort server-side logout. It is safe to call for an expired token."""
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"verify_exp": False},
        )
        session_id = payload.get("sid")
        if not session_id:
            return

        auth_session = db.query(AuthSession).filter(AuthSession.id == str(session_id)).first()
        if auth_session is not None and auth_session.revoked_at is None:
            auth_session.revoked_at = int(time.time())
            db.commit()
    except Exception:
        db.rollback()


def get_current_candidate(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != "candidate":
        logger.warning("Non-candidate user %s attempted candidate-only action", current_user.id)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Candidate access required",
        )
    return current_user


def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role not in {"admin", "super_admin"}:
        logger.warning("User %s attempted admin-only action", current_user.id)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


def get_current_super_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != "super_admin":
        logger.warning("User %s attempted super-admin-only action", current_user.id)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super Admin access required",
        )
    return current_user
