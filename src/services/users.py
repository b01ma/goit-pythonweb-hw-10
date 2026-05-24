from sqlalchemy.orm import Session

from src.database.models import User
from src.repository.users import UserRepository
from src.utils.cloudinary import upload_avatar


class UserService:
    """Service for current-user operations."""

    @staticmethod
    def update_avatar(db: Session, user: User, file) -> User:
        avatar_url = upload_avatar(file, f"user_{user.id}")
        return UserRepository.update_avatar(db, user, avatar_url)