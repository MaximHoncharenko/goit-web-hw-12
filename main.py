from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Base, Contact, ContactResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, timedelta
from schemas import ContactCreate, ContactUpdate
import crud  # Імпортуємо файл crud.py

# URL для підключення до бази даних
DATABASE_URL = "postgresql://postgres:0997943465max@localhost:5432/contacts_db"

# Створення engine для з'єднання з базою даних
engine = create_engine(DATABASE_URL)

# Створення сесії для виконання запитів
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Створення таблиць, якщо вони ще не існують
Base.metadata.create_all(bind=engine)

# Ініціалізація FastAPI
app = FastAPI()

# Отримання сесії для роботи з базою даних
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Створення нового контакту
@app.post("/contacts/", response_model=ContactResponse)
def create_contact(contact: ContactCreate, db: Session = Depends(get_db)):
    return crud.create_contact(db=db, contact=contact)

@app.get("/contacts/", response_model=List[ContactResponse])
def get_contacts(db: Session = Depends(get_db)):
    return crud.get_contacts(db=db)

@app.get("/contacts/{contact_id}", response_model=ContactResponse)
def get_contact(contact_id: int, db: Session = Depends(get_db)):
    db_contact = crud.get_contact(db=db, contact_id=contact_id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact

@app.put("/contacts/{contact_id}", response_model=ContactResponse)
def update_contact(contact_id: int, contact: ContactUpdate, db: Session = Depends(get_db)):
    db_contact = crud.update_contact(db=db, contact_id=contact_id, contact=contact)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact

@app.delete("/contacts/{contact_id}")
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    db_contact = crud.delete_contact(db=db, contact_id=contact_id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return {"message": "Contact deleted successfully"}

@app.get("/contacts/search", response_model=List[ContactResponse])
def search_contacts(
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        db: Session = Depends(get_db)
):
    query = db.query(Contact)

    if first_name:
        query = query.filter(Contact.first_name.ilike(f"%{first_name}%"))
    if last_name:
        query = query.filter(Contact.last_name.ilike(f"%{last_name}%"))
    if email:
        query = query.filter(Contact.email.ilike(f"%{email}%"))

    return query.all()

@app.get("/contacts/birthdays/next_week", response_model=List[ContactResponse])
def get_contacts_with_upcoming_birthdays(db: Session = Depends(get_db)):
    today = date.today()
    next_week = today + timedelta(days=7)
    return db.query(Contact).filter(Contact.birthday >= today, Contact.birthday <= next_week).all()
