"""會員職務儲存庫模組。"""

from sqlalchemy.orm import Session
from models.member_position_model import MemberPosition
from repositories.base_repository import BaseRepository

class MemberPositionRepository(BaseRepository[MemberPosition]):
    """專門用於處理 MemberPosition 模型資料庫操作的儲存庫。"""
    def __init__(self, session: Session):
        """初始化會員職務儲存庫。

        Args:
            session (Session): SQLAlchemy 的資料庫會話。
        """
        super().__init__(session, MemberPosition)

    def find_by_member_and_position(self, member_id: int, position_id: int) -> MemberPosition | None:
        """尋找特定的會員職務分配紀錄。"""
        return self.session.query(self.model).filter_by(
            member_id=member_id, 
            position_id=position_id
        ).first()

    def has_primary_position(self, member_id: int) -> bool:
        """檢查會員是否已經有主要職務。"""
        return self.session.query(self.model).filter_by(
            member_id=member_id, 
            is_primary=True
        ).count() > 0
