from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, Text, Boolean
from sqlalchemy.orm import validates
import re
from project import session
Base = declarative_base()

regex = r"^\+380\d{9}$"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(String(100), unique=True, nullable=False)
    username = Column(String(200), unique=True, nullable=False)
    phone_number = Column(String(13), unique=True, nullable=False)

    @validates('phone_number')
    def validate_phone_number(self, key, value):
        if re.fullmatch(regex, value) and session.query(User).filter_by(phone_number=str(value)).first() is None:
            return value
        else:
            raise ValueError('Неправильно набраний номер або юзер з таким номером вже зареєстрований!')

    def __repr__(self):
        return f'id: {self.id}, telegram_id: {self.telegram_id}, username: {self.username}, phone_number: {self.phone_number}'


class PromoCode(Base):
    __tablename__ = "promo"

    id = Column(Integer, primary_key=True)
    code = Column(String(150), unique=True)
    prize = Column(String(150))
    is_used = Column(Boolean, default=False)
