import logging
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.schemas import (
    ContactCreate,
    ContactResponse,
    ContactUpdate,
    MessageResponse,
    PaginatedResponse,
)
from src.services.auth import get_current_user
from src.services.contacts import ContactService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/contacts", tags=["contacts"])


@router.post(
    "",
    response_model=ContactResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new contact",
    responses={
        201: {"description": "Contact created successfully"},
        400: {"description": "Invalid input data"},
        500: {"description": "Internal server error"},
    },
)
def create_contact(
    contact_data: ContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ContactResponse:
    """
    Create a new contact.
    
    - **first_name**: Contact's first name (1-50 characters)
    - **last_name**: Contact's last name (1-50 characters)
    - **email**: Valid email address (must be unique)
    - **phone**: Phone number (10-20 characters, must be unique)
    - **birthday**: Birthday in YYYY-MM-DD format
    - **additional_data**: Optional additional information (max 500 characters)
    """
    logger.info(f"POST /api/contacts - Creating contact: {contact_data.email}")
    return ContactService.create_contact(db, contact_data, current_user)


@router.get(
    "/upcoming-birthdays",
    response_model=PaginatedResponse[ContactResponse],
    summary="Get contacts with upcoming birthdays",
    responses={
        200: {"description": "Contacts with upcoming birthdays"},
        500: {"description": "Internal server error"},
    },
)
def get_upcoming_birthdays(
    days: int = Query(7, ge=1, le=365, description="Number of days to look ahead"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of items to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PaginatedResponse[ContactResponse]:
    """
    Get contacts with birthdays in the next N days.
    
    - **days**: Number of days to look ahead (default: 7, max: 365)
    - **skip**: Pagination offset (default: 0)
    - **limit**: Pagination limit (default: 10, max: 100)
    """
    logger.info(f"GET /api/contacts/upcoming-birthdays - days={days}, skip={skip}, limit={limit}")
    return ContactService.get_upcoming_birthdays(db, current_user, days, skip, limit)


@router.get(
    "",
    response_model=PaginatedResponse[ContactResponse],
    summary="Get all contacts with optional search",
    responses={
        200: {"description": "List of contacts"},
        500: {"description": "Internal server error"},
    },
)
def get_contacts(
    first_name: Optional[str] = Query(None, min_length=1, description="Filter by first name"),
    last_name: Optional[str] = Query(None, min_length=1, description="Filter by last name"),
    email: Optional[str] = Query(None, min_length=1, description="Filter by email"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of items to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PaginatedResponse[ContactResponse]:
    """
    Get all contacts with optional search filters.
    
    - **first_name**: Filter by first name (partial match, case-insensitive)
    - **last_name**: Filter by last name (partial match, case-insensitive)
    - **email**: Filter by email (partial match, case-insensitive)
    - **skip**: Pagination offset (default: 0)
    - **limit**: Pagination limit (default: 10, max: 100)
    
    If no search filters are provided, returns all contacts.
    Search filters are combined with OR logic.
    """
    logger.info(
        f"GET /api/contacts - first_name={first_name}, "
        f"last_name={last_name}, email={email}, skip={skip}, limit={limit}"
    )

    if first_name or last_name or email:
        return ContactService.search_contacts(
            db, current_user, first_name, last_name, email, skip, limit
        )
    else:
        return ContactService.get_all_contacts(db, current_user, skip, limit)


@router.get(
    "/{contact_id}",
    response_model=ContactResponse,
    summary="Get a specific contact",
    responses={
        200: {"description": "Contact found"},
        404: {"description": "Contact not found"},
        500: {"description": "Internal server error"},
    },
)
def get_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ContactResponse:
    """
    Get a specific contact by ID.
    
    - **contact_id**: The ID of the contact to retrieve
    """
    logger.info(f"GET /api/contacts/{contact_id} - Fetching contact")
    return ContactService.get_contact(db, contact_id, current_user)


@router.put(
    "/{contact_id}",
    response_model=ContactResponse,
    summary="Update a contact",
    responses={
        200: {"description": "Contact updated successfully"},
        404: {"description": "Contact not found"},
        400: {"description": "Invalid input data"},
        500: {"description": "Internal server error"},
    },
)
def update_contact(
    contact_id: int,
    contact_data: ContactUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ContactResponse:
    """
    Update an existing contact. All fields are optional.
    
    - **contact_id**: The ID of the contact to update
    - **first_name**: New first name (optional)
    - **last_name**: New last name (optional)
    - **email**: New email address (optional)
    - **phone**: New phone number (optional)
    - **birthday**: New birthday in YYYY-MM-DD format (optional)
    - **additional_data**: New additional information (optional)
    """
    logger.info(f"PUT /api/contacts/{contact_id} - Updating contact")
    return ContactService.update_contact(db, contact_id, contact_data, current_user)


@router.delete(
    "/{contact_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a contact",
    responses={
        204: {"description": "Contact deleted successfully"},
        404: {"description": "Contact not found"},
        500: {"description": "Internal server error"},
    },
)
def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Delete a contact by ID.
    
    - **contact_id**: The ID of the contact to delete
    """
    logger.info(f"DELETE /api/contacts/{contact_id} - Deleting contact")
    ContactService.delete_contact(db, contact_id, current_user)
