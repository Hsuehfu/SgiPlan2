import logging
from PySide6.QtCore import QObject, Signal, Qt
from repositories.position_repository import PositionRepository

logger = logging.getLogger(__name__)

class PositionListViewModel(QObject):
    items_loaded = Signal(list)
    error_occurred = Signal(str)

    def __init__(self, db_session, parent=None):
        super().__init__(parent)
        self.session = db_session
        self.position_repo = PositionRepository(db_session)
        self.current_search_term = ""

    def load_positions(self, search_term=None):
        """載入職務列表，可依條件搜尋與排序。"""
        if search_term is not None:
            self.current_search_term = search_term

        try:
            positions = self.position_repo.get_all_sorted(self.current_search_term)
            self.items_loaded.emit(positions)
        except Exception as e:
            self.error_occurred.emit(f"載入職務時發生錯誤: {e}")

    def delete_position(self, position_id):
        """刪除指定的職務。"""
        try:
            position = self.position_repo.get_by_id_with_children(position_id)
            if position:
                if position.children:
                    self.error_occurred.emit("此職務底下有子職務，無法刪除。請先刪除所有子職務。")
                    return

                self.position_repo.delete(position)
                self.session.commit()
                self.load_positions()  # 使用當前的過濾和排序設定重新載入
            else:
                self.error_occurred.emit("找不到要刪除的職務。")
        except Exception as e:
            self.session.rollback()
            self.error_occurred.emit(f"刪除職務時發生錯誤: {e}")

    def update_positions_hierarchy(self, hierarchy_data: list):
        """更新職務的層級和排序。"""
        try:
            for item_data in hierarchy_data:
                position = self.position_repo.get_by_id(item_data['id'])
                if position:
                    position.parent_id = item_data['parent_id']
                    position.rank = item_data['rank']
            self.session.commit()
            self.load_positions()
        except Exception as e:
            self.session.rollback()
            self.error_occurred.emit(f"更新職務層級時發生錯誤: {e}")
