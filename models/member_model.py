from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Member(Base):
    __tablename__ = 'members'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    phone_number = Column(String, unique=True, index=True, nullable=True)
    is_schedulable = Column(Integer, default=1, nullable=False)
    region_id = Column(Integer, ForeignKey('regions.id'))
    department_id = Column(Integer, ForeignKey('departments.id'), nullable=True)

    region = relationship("Region", back_populates="members")
    positions = relationship("MemberPosition", back_populates="member", cascade="all, delete-orphan")
    department = relationship("Department", back_populates="members")
