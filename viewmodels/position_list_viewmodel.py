import logging
from PySide6.QtCore import QObject, Signal, Qt
from models.position_model import Position
from models.database import Session

logger = logging.getLogger(__name__)

class PositionListViewModel(QObject):
    positions_loaded = Signal(list)
    operation_successful = Signal()
    error_occurred = Signal(str)

    def __init__(self):
        super().__init__()
        self.current_search_term = ""
        self.current_sort_column = 0  # 預設由 ID 排序
        self.current_sort_order = Qt.AscendingOrder

    def load_positions(self, search_term=None, sort_column=None, sort_order=None):
        if search_term is not None:
            self.current_search_term = search_term
        if sort_column is not None:
            self.current_sort_column = sort_column
        if sort_order is not None:
            self.current_sort_order = sort_order

        try:
            with Session() as session:
                query = session.query(Position)

                if self.current_search_term:
                    query = query.filter(Position.name.ilike(f"%{self.current_search_term}%"))

                sort_field = None
                if self.current_sort_column == 0:  # ID 欄位
                    sort_field = Position.id
                elif self.current_sort_column == 1:  # 職務名稱欄位
                    sort_field = Position.name

                if sort_field is not None:
                    if self.current_sort_order == Qt.AscendingOrder:
                        query = query.order_by(sort_field.asc())
                    else:
                        query = query.order_by(sort_field.desc())

                positions = query.all()
                self.positions_loaded.emit(positions)
        except Exception as e:
            self.error_occurred.emit(f"載入職務時發生錯誤: {e}")

    def delete_position(self, position_id):
        try:
            with Session() as session:
                position = session.query(Position).filter_by(id=position_id).first()
                if position:
                    session.delete(position)
                    session.commit()
                    self.operation_successful.emit()
                    self.load_positions()  # 使用當前的過濾和排序設定重新載入
                else:
                    self.error_occurred.emit("找不到要刪除的職務。")
        except Exception as e:
            session.rollback()
            self.error_occurred.emit(f"刪除職務時發生錯誤: {e}")

    def sort_positions(self, column_index, order):
        self.load_positions(sort_column=column_index, sort_order=order)
