from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.utils.auth import (
    authenticate_user,
    create_access_token,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    user_is_valid = authenticate_user(
        username=form_data.username,
        password=form_data.password,
    )

    if not user_is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    access_token = create_access_token(
        username=form_data.username,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }