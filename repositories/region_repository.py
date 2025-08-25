from typing import List, Set
from PySide6.QtCore import Qt
from sqlalchemy.orm import Session, joinedload
from models.region_model import Region
from repositories.base_repository import BaseRepository

class RegionRepository(BaseRepository[Region]):
    """專門用於處理 Region 模型資料庫操作的儲存庫。"""
    def __init__(self, session: Session):
        """初始化地區儲存庫。

        Args:
            session (Session): SQLAlchemy 的資料庫會話。
        """
        super().__init__(session, Region)

    def search(self, search_term: str | None, sort_column: int | None, sort_order: Qt.SortOrder) -> List[Region]:
        """搜尋並排序地區資料。

        Args:
            search_term (str | None): 搜尋關鍵字。
            sort_column (int | None): 排序的欄位索引。
            sort_order (Qt.SortOrder): 排序順序。

        Returns:
            List[Region]: 符合條件的地區列表。
        """
        query = self.session.query(self.model)

        if search_term:
            query = query.filter(self.model.name.ilike(f"%{search_term}%"))

        if sort_column is not None:
            sort_field = None
            if sort_column == 0:  # ID 欄位
                sort_field = self.model.id
            elif sort_column == 1:  # 地區名稱欄位
                sort_field = self.model.name

            if sort_field is not None:
                if sort_order == Qt.AscendingOrder:
                    query = query.order_by(sort_field.asc())
                else:
                    query = query.order_by(sort_field.desc())
        
        return query.all()

    def get_by_id_with_children(self, region_id: int) -> Region | None:
        """依據 ID 獲取地區，並預先載入其子地區。

        Args:
            region_id (int): 地區的 ID。

        Returns:
            Region | None: 找到的地區實體，包含子地區，若未找到則返回 None。
        """
        return self.session.query(self.model).options(joinedload(self.model.children)).filter_by(id=region_id).first()

    def _get_all_descendant_ids(self, region_id: int) -> Set[int]:
        """遞迴獲取一個地區的所有後代ID。"""
        descendant_ids = set()
        children = (
            self.session.query(self.model.id).filter(self.model.parent_id == region_id).all()
        )

        for (child_id,) in children:
            if child_id not in descendant_ids:
                descendant_ids.add(child_id)
                descendant_ids.update(self._get_all_descendant_ids(child_id))
        return descendant_ids

    def get_possible_parents(self, region_id: int | None) -> List[Region]:
        """載入所有可作為父級的地區列表。

        在編輯模式下，會排除自身及其所有後代。

        Args:
            region_id (int | None): 正在編輯的地區ID，若是新增模式則為 None。

        Returns:
            List[Region]: 可作為父級的地區列表。
        """
        query = self.session.query(self.model)
        if region_id is not None:
            excluded_ids = {region_id}
            descendant_ids = self._get_all_descendant_ids(region_id)
            excluded_ids.update(descendant_ids)
            query = query.filter(self.model.id.notin_(excluded_ids))

        return query.order_by(self.model.name).all()
