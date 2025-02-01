from sqlalchemy.orm import Session
import models
import schemas


# Створення нового контакту
def create_contact(db: Session, contact: schemas.ContactCreate):
    db_contact = models.Contact(
        first_name=contact.first_name,
        last_name=contact.last_name,
        email=contact.email,
        phone_number=contact.phone_number,
        birthday=contact.birthday,
        additional_info=contact.additional_info
    )
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

# Отримання всіх контактів
def get_contacts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Contact).offset(skip).limit(limit).all()

# Отримання контакту за id
def get_contact(db: Session, contact_id: int):
    return db.query(models.Contact).filter(models.Contact.id == contact_id).first()

# Оновлення контакту
def update_contact(db: Session, contact_id: int, contact: schemas.ContactUpdate):
    db_contact = db.query(models.Contact).filter(models.Contact.id == contact_id).first()
    if db_contact:
        if contact.first_name:
            db_contact.first_name = contact.first_name
        if contact.last_name:
            db_contact.last_name = contact.last_name
        if contact.email:
            db_contact.email = contact.email
        if contact.phone_number:
            db_contact.phone_number = contact.phone_number
        if contact.birthday:
            db_contact.birthday = contact.birthday
        if contact.additional_info:
            db_contact.additional_info = contact.additional_info

        db.commit()
        db.refresh(db_contact)
    return db_contact


# Видалення контакту
def delete_contact(db: Session, contact_id: int):
    db_contact = db.query(models.Contact).filter(models.Contact.id == contact_id).first()
    if db_contact:
        db.delete(db_contact)
        db.commit()
    return db_contact
