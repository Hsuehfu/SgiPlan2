"""項目儲存庫模組。"""

from sqlalchemy.orm import Session
from models.item_model import Item
from repositories.base_repository import BaseRepository

class ItemRepository(BaseRepository[Item]):
    """專門用於處理 Item 模型資料庫操作的儲存庫。"""
    def __init__(self, session: Session):
        """初始化項目儲存庫。

        Args:
            session (Session): SQLAlchemy 的資料庫會話。
        """
        super().__init__(session, Item)
