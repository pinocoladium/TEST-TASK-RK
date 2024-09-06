import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class User(Base):
    """
    Пользователи
    """

    __tablename__ = "auth_user"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    admin = Column(Boolean, default=False)
    phone = Column(String(20), unique=True, nullable=False)
    points = Column(Float, default=0)

    def __list__(self):
        return (
            self.id,
            self.username,
            self.email,
            self.password,
            self.created_at,
            self.admin,
            self.phone,
            self.points,
        )

    def __iter__(self):
        return iter(self.__list__())
