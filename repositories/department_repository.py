"""部門儲存庫模組。"""

from sqlalchemy.orm import Session
from models.department_model import Department
from repositories.base_repository import BaseRepository

class DepartmentRepository(BaseRepository[Department]):
    """專門用於處理 Department 模型資料庫操作的儲存庫。"""
    def __init__(self, session: Session):
        """初始化部門儲存庫。

        Args:
            session (Session): SQLAlchemy 的資料庫會話。
        """
        super().__init__(session, Department)
