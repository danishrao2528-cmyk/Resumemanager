import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user_model import User


load_dotenv()


SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "change-this-secret-key",
)

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 30


password_hash = PasswordHash.recommended()


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
)


def hash_password(
    password: str,
) -> str:
    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    try:
        return password_hash.verify(
            plain_password,
            hashed_password,
        )
    except Exception:
        return False


def authenticate_user(
    username: str,
    password: str,
    db: Session,
):
    user = (
        db.query(User)
        .filter(
            User.username == username
        )
        .first()
    )

    if user is None:
        return None

    if not verify_password(
        password,
        user.password_hash,
    ):
        return None

    return user


def create_access_token(
    username: str,
) -> str:
    expiration_time = (
        datetime.now(timezone.utc)
        + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    payload = {
        "sub": username,
        "exp": expiration_time,
    }

    encoded_jwt = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    return encoded_jwt


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    authentication_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={
            "WWW-Authenticate": "Bearer",
        },
    )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        username = payload.get("sub")

        if username is None:
            raise authentication_error

    except InvalidTokenError as error:
        raise authentication_error from error

    user = (
        db.query(User)
        .filter(
            User.username == username
        )
        .first()
    )

    if user is None:
        raise authentication_error

    return user