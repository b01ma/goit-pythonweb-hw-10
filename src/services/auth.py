from fastapi import BackgroundTasks, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.exceptions import AuthenticationError, ConflictError, EmailVerificationError
from src.repository.users import UserRepository
from src.schemas import TokenResponse, UserCreate
from src.services.email import send_verification_email
from src.utils.security import (
    create_access_token,
    create_email_token,
    decode_token,
    get_email_from_token,
    get_password_hash,
    verify_password,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


class AuthService:
    """Service for authentication flows."""

    @staticmethod
    def register_user(
        db: Session, user_data: UserCreate, background_tasks: BackgroundTasks
    ) -> User:
        existing_user = UserRepository.get_by_email(db, user_data.email)
        if existing_user:
            raise ConflictError(f"User with email '{user_data.email}' already exists.")

        user = UserRepository.create(
            db,
            username=user_data.username,
            email=user_data.email,
            hashed_password=get_password_hash(user_data.password),
        )
        token = create_email_token(user.email)
        background_tasks.add_task(send_verification_email, user.email, user.username, token)
        return user

    @staticmethod
    def login_user(db: Session, email: str, password: str) -> TokenResponse:
        user = UserRepository.get_by_email(db, email)
        if not user or not verify_password(password, user.hashed_password):
            raise AuthenticationError("Invalid email or password.")

        return TokenResponse(access_token=create_access_token({"sub": user.email}))

    @staticmethod
    def verify_email(db: Session, token: str) -> User:
        try:
            email = get_email_from_token(token)
        except JWTError as exc:
            raise EmailVerificationError("Invalid or expired verification token.") from exc

        user = UserRepository.get_by_email(db, email)
        if not user:
            raise AuthenticationError("User not found.")
        if user.is_verified:
            return user

        return UserRepository.mark_verified(db, user)

    @staticmethod
    def request_verification_email(
        db: Session, email: str, background_tasks: BackgroundTasks
    ) -> None:
        user = UserRepository.get_by_email(db, email)
        if not user:
            raise AuthenticationError("User not found.")
        if user.is_verified:
            return

        token = create_email_token(user.email)
        background_tasks.add_task(send_verification_email, user.email, user.username, token)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        if payload.get("scope") != "access_token":
            raise credentials_exception
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError as exc:
        raise credentials_exception from exc

    user = UserRepository.get_by_email(db, email)
    if user is None:
        raise credentials_exception
    return user