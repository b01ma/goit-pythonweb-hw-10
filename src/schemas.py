from datetime import date, datetime
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, EmailStr, Field


T = TypeVar("T")


class ContactBase(BaseModel):
    """Base schema for contact data."""

    first_name: str = Field(..., min_length=1, max_length=50, description="First name")
    last_name: str = Field(..., min_length=1, max_length=50, description="Last name")
    email: EmailStr = Field(..., description="Email address")
    phone: str = Field(..., min_length=10, max_length=20, description="Phone number")
    birthday: date = Field(..., description="Birthday")
    additional_data: Optional[str] = Field(None, max_length=500, description="Additional info")


class ContactCreate(ContactBase):
    """Schema for creating a new contact."""

    pass


class ContactUpdate(BaseModel):
    """Schema for updating a contact."""

    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    birthday: Optional[date] = None
    additional_data: Optional[str] = Field(None, max_length=500)


class ContactResponse(ContactBase):
    """Schema for contact response."""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserBase(BaseModel):
    """Base schema for user data."""

    username: str = Field(..., min_length=1, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    """Schema for user registration."""

    password: str = Field(..., min_length=6, max_length=128)


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)


class UserResponse(UserBase):
    """Schema for user response."""

    id: int
    is_verified: bool
    avatar_url: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    """Schema for token response."""

    access_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    """Schema for requesting email verification."""

    email: EmailStr


class AvatarResponse(BaseModel):
    """Schema for avatar upload response."""

    avatar_url: str


class PaginationParams(BaseModel):
    """Schema for pagination parameters."""

    skip: int = Field(0, ge=0, description="Number of items to skip")
    limit: int = Field(10, ge=1, le=100, description="Number of items to return")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response schema."""

    data: List[T]
    total: int = Field(..., ge=0, description="Total number of items")
    skip: int = Field(..., ge=0, description="Number of items skipped")
    limit: int = Field(..., ge=1, description="Items per page")

    @property
    def pages(self) -> int:
        """Calculate total number of pages."""
        return (self.total + self.limit - 1) // self.limit


class MessageResponse(BaseModel):
    """Schema for simple message responses."""

    message: str
    detail: Optional[str] = None


class ErrorResponse(BaseModel):
    """Schema for error responses."""

    error: str
    detail: Optional[str] = None
    status_code: int
