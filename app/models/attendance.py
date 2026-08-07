from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean
from app.database import Base

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    time = Column(DateTime, nullable=False)
    mark = Column(Integer, nullable=True)