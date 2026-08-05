import os
import secrets

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.utils.logger import logger


load_dotenv()

security = HTTPBasic()

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")


def authenticate_user(
    credentials: HTTPBasicCredentials = Depends(security),
) -> str:
    username_is_correct = secrets.compare_digest(
        credentials.username,
        ADMIN_USERNAME,
    )

    password_is_correct = secrets.compare_digest(
        credentials.password,
        ADMIN_PASSWORD,
    )

    if not username_is_correct or not password_is_correct:
        logger.warning(
            "Failed login attempt for username: %s",
            credentials.username,
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    logger.info(
        "User authenticated successfully: %s",
        credentials.username,
    )

    return credentials.username