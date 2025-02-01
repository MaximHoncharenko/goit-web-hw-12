from pydantic import BaseModel
from datetime import date
from typing import Optional

# Модель для створення контакту
class ContactCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone_number: str
    birthday: date
    additional_info: Optional[str] = None

    class Config:
        orm_mode = True

# Модель для відповіді на запит контакту
class ContactResponse(ContactCreate):
    id: int

    class Config:
        orm_mode = True

# Модель для пошукових запитів
class ContactSearch(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None

# Модель для оновлення контакту
class ContactUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    birthday: Optional[date] = None
    additional_info: Optional[str] = None

    class Config:
        orm_mode = True
