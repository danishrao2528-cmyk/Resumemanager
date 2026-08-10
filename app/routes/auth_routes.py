from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user_model import User
from app.schemas.user_schema import Token, UserCreate, UserOut
from app.utils.auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    hash_password,
)
from app.utils.logger import logger


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_candidate(user_data: UserCreate, db: Session = Depends(get_db)):
    email = str(user_data.email).strip().lower()
    username = user_data.username.strip()

    existing_user = (
        db.query(User)
        .filter(or_(User.email == email, User.username == username))
        .first()
    )
    if existing_user:
        if existing_user.email == email:
            detail = "An account with this email already exists"
        else:
            detail = "Username already exists"
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)

    try:
        new_user = User(
            full_name=user_data.full_name.strip(),
            username=username,
            email=email,
            password_hash=hash_password(user_data.password),
            role="candidate",
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        logger.info("Candidate registered user_id=%s email=%s", new_user.id, new_user.email)
        return new_user
    except HTTPException:
        raise
    except Exception as error:
        db.rollback()
        logger.exception("Candidate registration failed for email=%s", email)
        raise HTTPException(status_code=500, detail="Unable to create account") from error


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    # OAuth2PasswordRequestForm calls this field `username`, but this app uses email login.
    email = form_data.username.strip().lower()
    user = authenticate_user(email=email, password=form_data.password, db=db)

    if user is None:
        logger.warning("Failed login attempt for email=%s", email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(user.id)
    logger.info("Successful login user_id=%s role=%s", user.id, user.role)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "full_name": user.full_name,
        "username": user.username,
        "email": user.email,
        "role": user.role,
    }
@router.get("/me", response_model=UserOut)
def get_logged_in_user(
    current_user: User = Depends(get_current_user),
):
    return current_user
