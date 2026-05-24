from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.schemas import MessageResponse, RequestEmail, TokenResponse, UserCreate, UserLogin, UserResponse
from src.services.auth import AuthService

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> UserResponse:
    user = AuthService.register_user(db, user_data, background_tasks)
    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenResponse)
def login(user_data: UserLogin, db: Session = Depends(get_db)) -> TokenResponse:
    return AuthService.login_user(db, user_data.email, user_data.password)


@router.get("/verify-email", response_model=MessageResponse)
def verify_email(token: str, db: Session = Depends(get_db)) -> MessageResponse:
    AuthService.verify_email(db, token)
    return MessageResponse(message="Email successfully verified")


@router.post("/request-email", response_model=MessageResponse)
def request_email(
    payload: RequestEmail,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> MessageResponse:
    AuthService.request_verification_email(db, payload.email, background_tasks)
    return MessageResponse(message="Verification email sent")