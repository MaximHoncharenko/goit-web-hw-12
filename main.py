from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext
from datetime import datetime, timedelta, date
from jose import JWTError, jwt
from typing import List, Optional

import models
import crud
import schemas

# URL для підключення до бази даних
DATABASE_URL = "postgresql://postgres:0997943465max@localhost:5432/contacts_db"

# Створення engine для з'єднання з базою даних
engine = create_engine(DATABASE_URL)

# Створення сесії для виконання запитів
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Створення таблиць, якщо вони ще не існують
models.Base.metadata.create_all(bind=engine)

# Ініціалізація FastAPI
app = FastAPI()

# **Хешування паролів**
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# **JWT-конфігурація**
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# **Функція для отримання БД-сесії**
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# **Функція для створення токена**
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# **Функція для отримання поточного користувача**
def get_current_user(db: Session = Depends(get_db), token: str = Depends(lambda: None)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

# **Реєстрація користувача**
@app.post("/register/")
def register_user(email: str, password: str, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(password)
    db_user = models.User(email=email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    return {"message": "User registered successfully"}

# **Авторизація користувача**
@app.post("/login/")
def login(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not pwd_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user.email}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}

# **Створення нового контакту**
@app.post("/contacts/", response_model=schemas.ContactResponse)
def create_contact(contact: schemas.ContactCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.create_contact(db=db, contact=contact, owner_id=current_user.id)

# **Отримання всіх контактів користувача**
@app.get("/contacts/", response_model=List[schemas.ContactResponse])
def get_contacts(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Contact).filter(models.Contact.owner_id == current_user.id).all()

# **Отримання конкретного контакту**
@app.get("/contacts/{contact_id}", response_model=schemas.ContactResponse)
def get_contact(contact_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_contact = crud.get_contact(db=db, contact_id=contact_id)
    if db_contact is None or db_contact.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact

# **Оновлення контакту**
@app.put("/contacts/{contact_id}", response_model=schemas.ContactResponse)
def update_contact(contact_id: int, contact: schemas.ContactUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_contact = crud.update_contact(db=db, contact_id=contact_id, contact=contact)
    if db_contact is None or db_contact.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact

# **Видалення контакту**
@app.delete("/contacts/{contact_id}")
def delete_contact(contact_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_contact = crud.delete_contact(db=db, contact_id=contact_id)
    if db_contact is None or db_contact.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Contact not found")
    return {"message": "Contact deleted successfully"}
