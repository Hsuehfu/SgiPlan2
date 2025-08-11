from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .database import Base

class Region(Base):
    __tablename__ = 'regions'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    members = relationship("Member", back_populates="region")
