from sqlalchemy import Column, Integer, String
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    phone_number = Column(String, nullable=False, unique=True)
    parent_phone_number = Column(String, nullable=True)
    stage = Column(String, nullable=True)
    level = Column(Integer, nullable=True)
    role = Column(String, nullable=False)