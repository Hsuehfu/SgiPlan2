# models/department_model.py

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .database import Base

class Department(Base):
    __tablename__ = 'departments'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    members = relationship("Member", back_populates="department")