from fastapi import APIRouter, Depends, File, Request, UploadFile
from slowapi import Limiter
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.schemas import UserResponse
from src.services.auth import get_current_user
from src.services.users import UserService

router = APIRouter(prefix="/api/users", tags=["users"])
limiter = Limiter(key_func=lambda request: request.client.host if request.client else "unknown")


@router.get("/me", response_model=UserResponse)
@limiter.limit("10/minute")
def get_me(request: Request, current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.patch("/avatar", response_model=UserResponse)
def update_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    user = UserService.update_avatar(db, current_user, file)
    return UserResponse.model_validate(user)