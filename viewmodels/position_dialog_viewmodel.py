from PySide6.QtCore import QObject, Signal
from models.position_model import Position
from models.database import Session
from sqlalchemy.exc import IntegrityError

class PositionDialogViewModel(QObject):
    position_saved = Signal()
    error_occurred = Signal(str)

    def __init__(self):
        super().__init__()
        self._position = None

    def set_position(self, position: Position = None):
        self._position = position

    def save_position(self, name: str):
        try:
            with Session() as session:
                if self._position: # Editing existing position
                    position = session.query(Position).filter_by(id=self._position.id).first()
                    if position:
                        position.name = name
                    else:
                        self.error_occurred.emit("找不到要更新的職務。")
                        return
                else: # Adding new position
                    position = Position(name=name)
                    session.add(position)
                
                session.commit()
                self.position_saved.emit()
        except IntegrityError as e:
            session.rollback()
            if "UNIQUE constraint failed: positions.name" in str(e):
                self.error_occurred.emit("職務名稱已存在，請使用其他名稱。")
            else:
                self.error_occurred.emit(f"儲存職務時發生資料庫完整性錯誤: {e}")
        except Exception as e:
            session.rollback()
            self.error_occurred.emit(f"儲存職務時發生未知錯誤: {e}")

    def get_position_name(self):
        return self._position.name if self._position else ""
