from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from .database import Base

class Position(Base):
    __tablename__ = 'positions'
    __table_args__ = (UniqueConstraint('parent_id', 'name', name='_parent_name_uc'),)

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    parent_id = Column(Integer, ForeignKey('positions.id'), nullable=True)

    parent = relationship("Position", remote_side=[id], back_populates="children", lazy="joined")
    children = relationship("Position", back_populates="parent", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Position(id={self.id}, name='{self.name}', parent_id={self.parent_id})>"

