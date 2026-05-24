import logging
from typing import List, Optional

from sqlalchemy.orm import Session

from src.database.models import User
from src.repository.contacts import ContactRepository
from src.schemas import ContactCreate, ContactResponse, ContactUpdate, PaginatedResponse

logger = logging.getLogger(__name__)


class ContactService:
    """Service layer for contact operations."""

    @staticmethod
    def create_contact(db: Session, contact_data: ContactCreate, user: User) -> ContactResponse:
        """Create a new contact.
        
        Args:
            db: Database session
            contact_data: Contact creation data
            
        Returns:
            Created contact response
        """
        logger.info(f"Creating contact: {contact_data.email}")
        contact = ContactRepository.create(db, contact_data, user.id)
        return ContactResponse.model_validate(contact)

    @staticmethod
    def get_contact(db: Session, contact_id: int, user: User) -> ContactResponse:
        """Get a contact by ID.
        
        Args:
            db: Database session
            contact_id: Contact ID
            
        Returns:
            Contact response
        """
        logger.info(f"Fetching contact with ID: {contact_id}")
        contact = ContactRepository.get_by_id(db, contact_id, user.id)
        return ContactResponse.model_validate(contact)

    @staticmethod
    def get_all_contacts(
        db: Session, user: User, skip: int = 0, limit: int = 10
    ) -> PaginatedResponse[ContactResponse]:
        """Get paginated list of all contacts.
        
        Args:
            db: Database session
            skip: Number of items to skip
            limit: Number of items to return
            
        Returns:
            Paginated response with contacts
        """
        logger.info(f"Fetching all contacts (skip={skip}, limit={limit})")
        contacts, total = ContactRepository.get_all(db, user.id, skip, limit)
        return PaginatedResponse(
            data=[ContactResponse.model_validate(c) for c in contacts],
            total=total,
            skip=skip,
            limit=limit,
        )

    @staticmethod
    def search_contacts(
        db: Session,
        user: User,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> PaginatedResponse[ContactResponse]:
        """Search contacts by first name, last name, or email.
        
        Args:
            db: Database session
            first_name: Filter by first name
            last_name: Filter by last name
            email: Filter by email
            skip: Number of items to skip
            limit: Number of items to return
            
        Returns:
            Paginated response with matching contacts
        """
        logger.info(
            f"Searching contacts (first_name={first_name}, "
            f"last_name={last_name}, email={email})"
        )
        contacts, total = ContactRepository.search(
            db, user.id, first_name, last_name, email, skip, limit
        )
        return PaginatedResponse(
            data=[ContactResponse.model_validate(c) for c in contacts],
            total=total,
            skip=skip,
            limit=limit,
        )

    @staticmethod
    def get_upcoming_birthdays(
        db: Session,
        user: User,
        days: int = 7,
        skip: int = 0,
        limit: int = 10,
    ) -> PaginatedResponse[ContactResponse]:
        """Get contacts with upcoming birthdays.
        
        Args:
            db: Database session
            days: Number of days to look ahead (default: 7)
            skip: Number of items to skip
            limit: Number of items to return
            
        Returns:
            Paginated response with contacts having upcoming birthdays
        """
        logger.info(f"Fetching contacts with upcoming birthdays (next {days} days)")
        contacts, total = ContactRepository.get_upcoming_birthdays(db, user.id, days, skip, limit)
        return PaginatedResponse(
            data=[ContactResponse.model_validate(c) for c in contacts],
            total=total,
            skip=skip,
            limit=limit,
        )

    @staticmethod
    def update_contact(
        db: Session, contact_id: int, contact_data: ContactUpdate, user: User
    ) -> ContactResponse:
        """Update an existing contact.
        
        Args:
            db: Database session
            contact_id: Contact ID
            contact_data: Updated contact data
            
        Returns:
            Updated contact response
        """
        logger.info(f"Updating contact with ID: {contact_id}")
        contact = ContactRepository.update(db, contact_id, contact_data, user.id)
        return ContactResponse.model_validate(contact)

    @staticmethod
    def delete_contact(db: Session, contact_id: int, user: User) -> None:
        """Delete a contact.
        
        Args:
            db: Database session
            contact_id: Contact ID
        """
        logger.info(f"Deleting contact with ID: {contact_id}")
        ContactRepository.delete(db, contact_id, user.id)
