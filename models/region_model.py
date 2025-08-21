from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base

class Region(Base):
    __tablename__ = 'regions'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    parent_id = Column(Integer, ForeignKey('regions.id'), nullable=True)

    # --- 關係對應 ---
    # 對應到 Member 模型
    members = relationship("Member", back_populates="region")

    # 自我參考，用於建立樹狀結構
    # `remote_side=[id]` 告訴 SQLAlchemy 如何將 parent_id 連接到同一個資料表的 id
    parent = relationship("Region", remote_side=[id], back_populates="children", lazy="joined")
    children = relationship("Region", back_populates="parent", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Region(id={self.id}, name='{self.name}', parent_id={self.parent_id})>"