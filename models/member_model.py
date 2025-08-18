from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Member(Base):
    __tablename__ = 'members'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    phone_number = Column(String, nullable=True)
    is_schedulable = Column(Integer, default=1, nullable=False)
    region_id = Column(Integer, ForeignKey('regions.id'))

    region = relationship("Region", back_populates="members")
    positions = relationship("MemberPosition", back_populates="member")
