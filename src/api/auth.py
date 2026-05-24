from urllib.parse import parse_qs

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from pydantic import ValidationError as PydanticValidationError
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.exceptions import ValidationError
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
async def login(
    request: Request,
    db: Session = Depends(get_db),
) -> TokenResponse:
    content_type = request.headers.get("content-type", "")

    if "application/json" in content_type:
        try:
            payload = UserLogin.model_validate(await request.json())
        except PydanticValidationError as exc:
            raise ValidationError(str(exc)) from exc
        return AuthService.login_user(db, payload.email, payload.password)

    if "application/x-www-form-urlencoded" in content_type:
        form_payload = parse_qs((await request.body()).decode())
        username = form_payload.get("username", [""])[0]
        password = form_payload.get("password", [""])[0]
        if username and password:
            return AuthService.login_user(db, username, password)

    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="Email and password are required.",
    )


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