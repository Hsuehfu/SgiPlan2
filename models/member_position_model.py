from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class MemberPosition(Base):
    __tablename__ = 'member_positions'

    member_id = Column(Integer, ForeignKey('members.id'), primary_key=True)
    position_id = Column(Integer, ForeignKey('positions.id'), primary_key=True)

    member = relationship("Member", back_populates="positions")
    position = relationship("Position")
