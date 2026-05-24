import logging
from datetime import date, timedelta
from typing import List, Optional

from sqlalchemy import IntegrityError, and_, func, or_
from sqlalchemy.orm import Session

from src.database.models import Contact
from src.exceptions import ContactNotFound, ConflictError, DatabaseError
from src.schemas import ContactCreate, ContactUpdate

logger = logging.getLogger(__name__)


class ContactRepository:
    """Repository for contact database operations."""

    @staticmethod
    def create(db: Session, contact_data: ContactCreate, user_id: int) -> Contact:
        """Create a new contact.
        
        Args:
            db: Database session
            contact_data: Contact creation data
            
        Returns:
            Created contact object
            
        Raises:
            DatabaseError: If creation fails
        """
        try:
            contact = Contact(
                user_id=user_id,
                first_name=contact_data.first_name,
                last_name=contact_data.last_name,
                email=contact_data.email,
                phone=contact_data.phone,
                birthday=contact_data.birthday,
                additional_data=contact_data.additional_data,
            )
            db.add(contact)
            db.commit()
            db.refresh(contact)
            logger.info(f"Created contact: {contact}")
            return contact
        except IntegrityError as e:
            db.rollback()
            error_message = str(e.orig)
            if "contacts_email_key" in error_message or "ix_contacts_email" in error_message:
                raise ConflictError(f"Contact email '{contact_data.email}' already exists.") from e
            if "contacts_phone_key" in error_message or "ix_contacts_phone" in error_message:
                raise ConflictError(f"Contact phone '{contact_data.phone}' already exists.") from e
            raise ConflictError("Contact with provided email or phone already exists.") from e
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create contact: {str(e)}")
            raise DatabaseError(f"Failed to create contact: {str(e)}")

    @staticmethod
    def get_by_id(db: Session, contact_id: int, user_id: int) -> Contact:
        """Get contact by ID.
        
        Args:
            db: Database session
            contact_id: Contact ID
            
        Returns:
            Contact object
            
        Raises:
            ContactNotFound: If contact doesn't exist
        """
        contact = (
            db.query(Contact)
            .filter(and_(Contact.id == contact_id, Contact.user_id == user_id))
            .first()
        )
        if not contact:
            logger.warning(f"Contact with ID {contact_id} not found")
            raise ContactNotFound(contact_id)
        return contact

    @staticmethod
    def get_all(db: Session, user_id: int, skip: int = 0, limit: int = 10) -> tuple[List[Contact], int]:
        """Get paginated list of all contacts.
        
        Args:
            db: Database session
            skip: Number of items to skip
            limit: Number of items to return
            
        Returns:
            Tuple of (contacts list, total count)
        """
        total = (
            db.query(func.count(Contact.id)).filter(Contact.user_id == user_id).scalar() or 0
        )
        contacts = (
            db.query(Contact)
            .filter(Contact.user_id == user_id)
            .order_by(Contact.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        logger.debug(f"Retrieved {len(contacts)} contacts (skip={skip}, limit={limit})")
        return contacts, total

    @staticmethod
    def search(
        db: Session,
        user_id: int,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> tuple[List[Contact], int]:
        """Search contacts by first name, last name, or email.
        
        Args:
            db: Database session
            first_name: Filter by first name (partial match)
            last_name: Filter by last name (partial match)
            email: Filter by email (partial match)
            skip: Number of items to skip
            limit: Number of items to return
            
        Returns:
            Tuple of (contacts list, total count)
        """
        query = db.query(Contact).filter(Contact.user_id == user_id)
        filters = []

        if first_name:
            filters.append(Contact.first_name.ilike(f"%{first_name}%"))
        if last_name:
            filters.append(Contact.last_name.ilike(f"%{last_name}%"))
        if email:
            filters.append(Contact.email.ilike(f"%{email}%"))

        if filters:
            query = query.filter(or_(*filters))

        total = query.with_entities(func.count(Contact.id)).scalar() or 0
        contacts = query.order_by(Contact.created_at.desc()).offset(skip).limit(limit).all()

        logger.debug(
            f"Search found {len(contacts)} contacts "
            f"(first_name={first_name}, last_name={last_name}, email={email})"
        )
        return contacts, total

    @staticmethod
    def get_upcoming_birthdays(
        db: Session,
        user_id: int,
        days: int = 7,
        skip: int = 0,
        limit: int = 10,
    ) -> tuple[List[Contact], int]:
        """Get contacts with birthdays in the next N days.
        
        Args:
            db: Database session
            days: Number of days to look ahead (default: 7)
            skip: Number of items to skip
            limit: Number of items to return
            
        Returns:
            Tuple of (contacts list, total count)
        """
        today = date.today()
        end_date = today + timedelta(days=days)

        # Get all contacts and filter in Python for simplicity
        # (date comparison across years is complex in SQL)
        all_contacts = db.query(Contact).filter(Contact.user_id == user_id).all()
        upcoming = []

        for contact in all_contacts:
            birthday_this_year = contact.birthday.replace(year=today.year)

            if birthday_this_year < today:
                birthday_this_year = contact.birthday.replace(year=today.year + 1)

            if today <= birthday_this_year <= end_date:
                upcoming.append(contact)

        total = len(upcoming)
        upcoming = sorted(upcoming, key=lambda c: c.birthday)
        result = upcoming[skip : skip + limit]

        logger.debug(f"Found {total} contacts with upcoming birthdays")
        return result, total

    @staticmethod
    def update(db: Session, contact_id: int, contact_data: ContactUpdate, user_id: int) -> Contact:
        """Update an existing contact.
        
        Args:
            db: Database session
            contact_id: Contact ID
            contact_data: Updated contact data
            
        Returns:
            Updated contact object
            
        Raises:
            ContactNotFound: If contact doesn't exist
            DatabaseError: If update fails
        """
        contact = ContactRepository.get_by_id(db, contact_id, user_id)

        try:
            update_data = contact_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(contact, field, value)

            db.commit()
            db.refresh(contact)
            logger.info(f"Updated contact: {contact}")
            return contact
        except IntegrityError as e:
            db.rollback()
            raise ConflictError("Contact with provided email or phone already exists.") from e
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to update contact {contact_id}: {str(e)}")
            raise DatabaseError(f"Failed to update contact: {str(e)}")

    @staticmethod
    def delete(db: Session, contact_id: int, user_id: int) -> None:
        """Delete a contact.
        
        Args:
            db: Database session
            contact_id: Contact ID
            
        Raises:
            ContactNotFound: If contact doesn't exist
            DatabaseError: If deletion fails
        """
        contact = ContactRepository.get_by_id(db, contact_id, user_id)

        try:
            db.delete(contact)
            db.commit()
            logger.info(f"Deleted contact with ID: {contact_id}")
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to delete contact {contact_id}: {str(e)}")
            raise DatabaseError(f"Failed to delete contact: {str(e)}")
