from pydantic import BaseModel
from datetime import datetime

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    username: str
    password: str
    phone_number: str = None
    parent_phone_number: str = None
    stage: str = None
    level: int = None

class UserEdit(BaseModel):
    name: str = None
    username: str = None
    password: str = None

class Attend(BaseModel):
    id: int
    time: datetime

class Mark(BaseModel):
    mark: int
