from sqlalchemy.orm import Session
import models
import schemas


# Створення нового контакту
def create_contact(db: Session, contact: schemas.ContactCreate, owner_id: int):
    db_contact = models.Contact(
        first_name=contact.first_name,
        last_name=contact.last_name,
        email=contact.email,
        phone_number=contact.phone_number,
        birthday=contact.birthday,
        additional_info=contact.additional_info,
        owner_id=owner_id  # Призначаємо власника контакту
    )
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


# Отримання всіх контактів поточного користувача
def get_contacts(db: Session, owner_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Contact).filter(models.Contact.owner_id == owner_id).offset(skip).limit(limit).all()


# Отримання контакту за id для поточного користувача
def get_contact(db: Session, contact_id: int, owner_id: int):
    return db.query(models.Contact).filter(models.Contact.id == contact_id, models.Contact.owner_id == owner_id).first()


# Оновлення контакту
def update_contact(db: Session, contact_id: int, contact: schemas.ContactUpdate, owner_id: int):
    db_contact = db.query(models.Contact).filter(models.Contact.id == contact_id, models.Contact.owner_id == owner_id).first()
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
def delete_contact(db: Session, contact_id: int, owner_id: int):
    db_contact = db.query(models.Contact).filter(models.Contact.id == contact_id, models.Contact.owner_id == owner_id).first()
    if db_contact:
        db.delete(db_contact)
        db.commit()
    return db_contact
