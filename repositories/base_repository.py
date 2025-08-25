"""通用儲存庫模組。

此模組提供了一個通用的基底儲存庫類別 (BaseRepository)，用於抽象化資料庫操作。
"""

from typing import Any, Generic, List, Type, TypeVar
from sqlalchemy import select
from sqlalchemy.orm import Session

# 建立一個類型變數，用於表示任何 SQLAlchemy 模型
ModelType = TypeVar('ModelType')

class BaseRepository(Generic[ModelType]):
    """通用儲存庫基底類別，提供基本的 CRUD 操作。

    這個類別旨在被特定模型的儲存庫繼承，例如 MemberRepository。
    它封裝了與資料庫互動的通用邏輯。

    Attributes:
        session (Session): SQLAlchemy 的資料庫會話物件。
        model (Type[ModelType]): 此儲存庫操作的 SQLAlchemy 模型類別。
    """

    def __init__(self, session: Session, model: Type[ModelType]):
        """初始化儲存庫。

        Args:
            session (Session): SQLAlchemy 的資料庫會話。
            model (Type[ModelType]): 此儲存庫對應的 SQLAlchemy 模型類別。
        """
        self.session = session
        self.model = model

    def get_by_id(self, entity_id: Any) -> ModelType | None:
        """依據主鍵 ID 獲取單一實體。

        Args:
            entity_id (Any): 實體的主鍵。

        Returns:
            ModelType | None: 找到的實體，若未找到則返回 None。
        """
        return self.session.get(self.model, entity_id)

    def get_all(self) -> List[ModelType]:
        """獲取所有此模型的實體。

        Returns:
            List[ModelType]: 包含所有實體的列表。
        """
        statement = select(self.model)
        return list(self.session.execute(statement).scalars().all())

    def add(self, entity: ModelType) -> None:
        """新增一個新的實體到資料庫會話中。

        此操作僅將物件加入會話，需要呼叫 session.commit() 才會寫入資料庫。

        Args:
            entity (ModelType): 要新增的實體。
        """
        self.session.add(entity)

    def delete(self, entity: ModelType) -> None:
        """從資料庫會話中刪除一個實體。

        此操作僅將物件標記為刪除，需要呼叫 session.commit() 才會從資料庫移除。

        Args:
            entity (ModelType): 要刪除的實體。
        """
        self.session.delete(entity)

    def delete_by_id(self, entity_id: Any) -> bool:
        """依據主鍵 ID 刪除一個實體。

        Args:
            entity_id (Any): 要刪除的實體的主鍵。

        Returns:
            bool: 如果成功找到並標記為刪除則返回 True，否則返回 False。
        """
        entity = self.get_by_id(entity_id)
        if entity:
            self.session.delete(entity)
            return True
        return False
