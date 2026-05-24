import logging

from sqlalchemy.orm import Session

from src.database.models import User

logger = logging.getLogger(__name__)


class UserRepository:
    """Repository for user persistence."""

    @staticmethod
    def get_by_email(db: Session, email: str) -> User | None:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> User | None:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def create(db: Session, username: str, email: str, hashed_password: str) -> User:
        user = User(username=username, email=email, hashed_password=hashed_password)
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info("Created user with email: %s", email)
        return user

    @staticmethod
    def mark_verified(db: Session, user: User) -> User:
        user.is_verified = True
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update_avatar(db: Session, user: User, avatar_url: str) -> User:
        user.avatar_url = avatar_url
        db.commit()
        db.refresh(user)
        return user