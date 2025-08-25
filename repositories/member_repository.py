"""會員儲存庫模組。"""

from typing import List
from PySide6.QtCore import Qt
from sqlalchemy.orm import Session, joinedload
from models.member_model import Member
from models.region_model import Region
from repositories.base_repository import BaseRepository

class MemberRepository(BaseRepository[Member]):
    """專門用於處理 Member 模型資料庫操作的儲存庫。"""
    def __init__(self, session: Session):
        """初始化會員儲存庫。

        Args:
            session (Session): SQLAlchemy 的資料庫會話。
        """
        super().__init__(session, Member)

    def search(self, search_term: str | None, region_id: int | None, sort_column: int | None, sort_order: Qt.SortOrder) -> List[Member]:
        """搜尋、篩選並排序會員資料。

        Args:
            search_term (str | None): 姓名搜尋關鍵字。
            region_id (int | None): 地區 ID 篩選。
            sort_column (int | None): 排序欄位索引。
            sort_order (Qt.SortOrder): 排序順序。

        Returns:
            List[Member]: 符合條件的會員列表。
        """
        query = self.session.query(self.model).options(joinedload(self.model.region))

        if search_term:
            query = query.filter(self.model.name.ilike(f"%{search_term}%"))

        if region_id and region_id != -1:
            query = query.filter(self.model.region_id == region_id)

        if sort_column is not None:
            sort_field = None
            if sort_column == 0:  # Name
                sort_field = self.model.name
            elif sort_column == 1:  # Phone Number
                sort_field = self.model.phone_number
            elif sort_column == 2:  # Is Schedulable
                sort_field = self.model.is_schedulable
            elif sort_column == 3:  # Region
                query = query.join(Region)
                sort_field = Region.name

            if sort_field is not None:
                if sort_order == Qt.AscendingOrder:
                    query = query.order_by(sort_field.asc())
                else:
                    query = query.order_by(sort_field.desc())

        return query.all()
