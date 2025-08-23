import logging
from PySide6.QtCore import QObject, Signal, Qt
from models.position_model import Position

logger = logging.getLogger(__name__)

class PositionListViewModel(QObject):
    items_loaded = Signal(list)
    error_occurred = Signal(str)

    def __init__(self, db_session, parent=None):
        super().__init__(parent)
        self.session = db_session
        self.current_search_term = ""
        self.current_sort_column = 0  # 預設由 ID 排序
        self.current_sort_order = Qt.AscendingOrder

    def load_positions(self, search_term=None, sort_column=None, sort_order=None):
        """載入職務列表，可依條件搜尋與排序。"""
        if search_term is not None:
            self.current_search_term = search_term
        if sort_column is not None:
            self.current_sort_column = sort_column
        if sort_order is not None:
            self.current_sort_order = sort_order

        try:
            query = self.session.query(Position)

            if self.current_search_term:
                query = query.filter(Position.name.ilike(f"%{self.current_search_term}%"))

            sort_field = None
            if self.current_sort_column == 0:  # ID 欄位
                sort_field = Position.id
            elif self.current_sort_column == 1:  # 職務名稱欄位
                sort_field = Position.name

            # Always order by parent_id and rank for correct tree structure
            query = query.order_by(Position.parent_id.asc(), Position.rank.asc())

            positions = query.all()
            self.items_loaded.emit(positions)
        except Exception as e:
            self.error_occurred.emit(f"載入職務時發生錯誤: {e}")

    def delete_position(self, position_id):
        """刪除指定的職務。"""
        try:
            position = self.session.query(Position).filter_by(id=position_id).first()
            if position:
                # 檢查是否有子職務
                if position.children: # This relies on the relationship being loaded
                    self.error_occurred.emit("此職務底下有子職務，無法刪除。請先刪除所有子職務。")
                    return

                self.session.delete(position)
                self.session.commit()
                self.load_positions()  # 使用當前的過濾和排序設定重新載入
            else:
                self.error_occurred.emit("找不到要刪除的職務。")
        except Exception as e:
            self.session.rollback()
            self.error_occurred.emit(f"刪除職務時發生錯誤: {e}")

    def sort_positions(self, column_index, order):
        self.load_positions(sort_column=column_index, sort_order=order)

    def update_positions_hierarchy(self, hierarchy_data: list):
        """更新職務的層級和排序。"""
        try:
            for item_data in hierarchy_data:
                position = self.session.query(Position).filter_by(id=item_data['id']).first()
                if position:
                    position.parent_id = item_data['parent_id']
                    position.rank = item_data['rank'] # Update rank based on new order
            self.session.commit()
            self.load_positions() # Reload to reflect changes
        except Exception as e:
            self.session.rollback()
            self.error_occurred.emit(f"更新職務層級時發生錯誤: {e}")
