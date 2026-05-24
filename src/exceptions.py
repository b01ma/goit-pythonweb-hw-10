import logging
from typing import Optional

from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


class APIException(HTTPException):
    """Base API exception class."""

    def __init__(
        self,
        status_code: int,
        detail: str,
        error: str = "API Error",
        headers: Optional[dict] = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error = error
        logger.error(f"{error}: {detail}")


class ContactNotFound(APIException):
    """Contact not found exception."""

    def __init__(self, contact_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error="Contact not found",
            detail=f"Contact with ID {contact_id} does not exist.",
        )


class InvalidEmail(APIException):
    """Invalid email exception."""

    def __init__(self, email: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error="Invalid email",
            detail=f"Email '{email}' is already in use or invalid.",
        )


class InvalidPhoneNumber(APIException):
    """Invalid phone number exception."""

    def __init__(self, phone: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error="Invalid phone number",
            detail=f"Phone number '{phone}' is already in use or invalid.",
        )


class InvalidBirthday(APIException):
    """Invalid birthday exception."""

    def __init__(self, birthday: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error="Invalid birthday",
            detail=f"Birthday '{birthday}' must be in YYYY-MM-DD format and not in the future.",
        )


class DatabaseError(APIException):
    """Database operation error."""

    def __init__(self, detail: str = "Database operation failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error="Database error",
            detail=detail,
        )


class ConflictError(APIException):
    """Conflict error for duplicate resources."""

    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            error="Conflict",
            detail=detail,
        )


class AuthenticationError(APIException):
    """Authentication error."""

    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error="Unauthorized",
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class EmailVerificationError(APIException):
    """Email verification error."""

    def __init__(self, detail: str = "Email verification failed"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error="Email verification error",
            detail=detail,
        )


class ValidationError(APIException):
    """Data validation error."""

    def __init__(self, detail: str = "Validation failed"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error="Validation error",
            detail=detail,
        )
