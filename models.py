from sqlalchemy import Column, Integer, String, Date, Text
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from datetime import date

# Базовий клас для всіх моделей
Base = declarative_base()

# Описуємо модель для таблиці "contacts"
class Contact(Base):
    __tablename__ = 'contacts'  # Назва таблиці в базі даних

    # Опис полів таблиці
    id = Column(Integer, primary_key=True, index=True)  # Унікальний ідентифікатор
    first_name = Column(String, index=True)  # Ім'я контакту
    last_name = Column(String, index=True)  # Прізвище контакту
    email = Column(String, unique=True, index=True)  # Електронна адреса контакту
    phone_number = Column(String)  # Номер телефону контакту
    birthday = Column(Date)  # Дата народження контакту
    additional_info = Column(Text, nullable=True)  # Додаткові дані (необов'язкові)


class ContactResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    phone_number: str
    birthday: date  # Якщо хочете, щоб це було як об'єкт типу `date`
    additional_info: str | None

    class Config:
        orm_mode = True
