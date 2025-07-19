# models.py для телеграм бота
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Создаем базовый класс для моделей


Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    
    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    user_name = Column(String(50), nullable=False, unique=True)
    email = Column(String(50), nullable=False, unique=True)
    password = Column(String(128), nullable=False)
    
    # Связь с записями Iris
    iris_records = relationship("Iris", back_populates="user")

    def __repr__(self):
        return f'<User {self.user_name}>'


class Iris(Base):
    __tablename__ = 'iris'
    
    id = Column(Integer, primary_key=True)
    sepal_length = Column(Float, nullable=False)
    sepal_width = Column(Float, nullable=False)
    petal_length = Column(Float, nullable=False)
    petal_width = Column(Float, nullable=False)
    prediction = Column(String(10), nullable=False)
    real = Column(String(10))
    user_name = Column(String(50), ForeignKey('user.user_name'))
    
    # Связь с пользователем
    user = relationship("User", back_populates="iris_records")

    def __repr__(self):
        return f'<Iris {self.id}>'