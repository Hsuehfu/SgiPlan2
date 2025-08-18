from sqlalchemy import Column, Integer, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from .database import Base

class MemberPosition(Base):
    __tablename__ = 'member_positions'

    member_id = Column(Integer, ForeignKey('members.id'), primary_key=True)
    position_id = Column(Integer, ForeignKey('positions.id'), primary_key=True)
    is_primary = Column(Integer, nullable=False)
    __table_args__ = (
        CheckConstraint('is_primary IN (0, 1)', name='check_is_primary_boolean'),
    )

    member = relationship("Member", back_populates="positions")
    position = relationship("Position")
