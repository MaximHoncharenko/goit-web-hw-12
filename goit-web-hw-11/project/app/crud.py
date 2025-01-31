from django.conf.global_settings import SECRET_KEY
from sqlalchemy.orm import Session
import models
import schemas
from sqlalchemy.orm import Session
from models import User, Contact
from schemas import UserCreate, ContactCreate, ContactUpdate
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer

# Функція хешування пароля
def hash_password(password: str, pwd_context=None) -> str:
    return pwd_context.hash(password)


# Функція перевірки пароля
def verify_password(plain_password: str, hashed_password: str, pwd_context=None) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# Функція для отримання користувача за email
def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

# Функція для створення нового користувача
def create_user(db: Session, user: UserCreate):
    hashed_password = hash_password(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password, created_at=datetime.utcnow())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# Функція аутентифікації користувача
def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


# Функція для створення JWT-токена
def create_access_token(data: dict, expires_delta: timedelta = None, ALGORITHM=None, ACCESS_TOKEN_EXPIRE_MINUTES=None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# Функція для створення рефреш-токена
def create_refresh_token(data: dict, ALGORITHM=None, REFRESH_TOKEN_EXPIRE_DAYS=None):
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# Функція для отримання поточного користувача за JWT-токеном
def get_current_user(db: Session, token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=401, detail="Could not validate credentials")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user_by_email(db, email)
    if user is None:
        raise credentials_exception
    return user


# ======= Модифіковані функції для контактів =======

# Створення нового контакту
def create_contact(db: Session, contact: schemas.ContactCreate, owner_id: int):
    db_contact = models.Contact(
        first_name=contact.first_name,
        last_name=contact.last_name,
        email=contact.email,
        phone_number=contact.phone_number,
        birthday=contact.birthday,
        additional_info=contact.additional_info,
        owner_id=owner_id
    )
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


# Отримання всіх контактів поточного користувача
def get_contacts(db: Session, user: User, skip: int = 0, limit: int = 100):
    return db.query(Contact).filter(Contact.owner_id == user.id).offset(skip).limit(limit).all()


# Отримання контакту поточного користувача за ID
def get_contact(db: Session, contact_id: int, user: User):
    return db.query(Contact).filter(Contact.id == contact_id, Contact.owner_id == user.id).first()


# Оновлення контакту (тільки для його власника)
def update_contact(db: Session, contact_id: int, contact: ContactUpdate, user: User):
    db_contact = db.query(Contact).filter(Contact.id == contact_id, Contact.owner_id == user.id).first()
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


# Видалення контакту (тільки для його власника)
def delete_contact(db: Session, contact_id: int, user: User):
    db_contact = db.query(Contact).filter(Contact.id == contact_id, Contact.owner_id == user.id).first()
    if db_contact:
        db.delete(db_contact)
        db.commit()
    return db_contact
