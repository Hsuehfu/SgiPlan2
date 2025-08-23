from sqlalchemy import Column, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class MemberPosition(Base):
    __tablename__ = 'member_positions'

    member_id = Column(Integer, ForeignKey('members.id'), primary_key=True)
    position_id = Column(Integer, ForeignKey('positions.id'), primary_key=True)
    is_primary = Column(Boolean, default=False, nullable=False)

    member = relationship("Member", back_populates="positions")
    position = relationship("Position") # No back_populates here, as Position doesn't need to know about MemberPosition

    def __repr__(self):
        return f"<MemberPosition(member_id={self.member_id}, position_id={self.position_id}, is_primary={self.is_primary})>"