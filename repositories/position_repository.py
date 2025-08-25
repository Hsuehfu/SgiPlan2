"""職務儲存庫模組。"""

from typing import List, Set
from sqlalchemy.orm import Session, joinedload
from models.position_model import Position
from repositories.base_repository import BaseRepository

class PositionRepository(BaseRepository[Position]):
    """專門用於處理 Position 模型資料庫操作的儲存庫。"""
    def __init__(self, session: Session):
        """初始化職務儲存庫。

        Args:
            session (Session): SQLAlchemy 的資料庫會話。
        """
        super().__init__(session, Position)

    def get_all_sorted(self, search_term: str | None = None) -> List[Position]:
        """獲取所有職務，並根據層級和排序值進行排序。

        Args:
            search_term (str | None, optional): 用於篩選職務名稱的搜尋字詞。 Defaults to None.

        Returns:
            List[Position]: 已排序的職務列表。
        """
        query = self.session.query(self.model)

        if search_term:
            query = query.filter(self.model.name.ilike(f"%{search_term}%"))

        # Always order by parent_id and rank for correct tree structure
        query = query.order_by(self.model.parent_id.asc(), self.model.rank.asc())

        return query.all()

    def get_all_sorted_by_rank(self) -> List[Position]:
        """獲取所有職務，並根據 rank 欄位降序排序。"""
        return self.session.query(self.model).order_by(self.model.rank.desc()).all()

    def get_by_id_with_children(self, position_id: int) -> Position | None:
        """依據 ID 獲取職務，並預先載入其子職務。

        Args:
            position_id (int): 職務的 ID。

        Returns:
            Position | None: 找到的職務實體，包含子職務，若未找到則返回 None。
        """
        return self.session.query(self.model).options(joinedload(self.model.children)).filter_by(id=position_id).first()

    def _get_all_descendant_ids(self, position_id: int) -> Set[int]:
        """遞迴獲取一個職務的所有後代ID。"""
        descendant_ids = set()
        children = (
            self.session.query(self.model.id).filter(self.model.parent_id == position_id).all()
        )

        for (child_id,) in children:
            if child_id not in descendant_ids:
                descendant_ids.add(child_id)
                descendant_ids.update(self._get_all_descendant_ids(child_id))
        return descendant_ids

    def get_possible_parents(self, position_id: int | None) -> List[Position]:
        """載入所有可作為父級的職務列表。

        在編輯模式下，會排除自身及其所有後代。

        Args:
            position_id (int | None): 正在編輯的職務ID，若是新增模式則為 None。

        Returns:
            List[Position]: 可作為父級的職務列表。
        """
        query = self.session.query(self.model)
        if position_id is not None:
            excluded_ids = {position_id}
            descendant_ids = self._get_all_descendant_ids(position_id)
            excluded_ids.update(descendant_ids)
            query = query.filter(self.model.id.notin_(excluded_ids))

        return query.order_by(self.model.name).all()
