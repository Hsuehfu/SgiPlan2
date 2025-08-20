import logging
from PySide6.QtCore import QObject, Signal
from models.position_model import Position
from sqlalchemy.exc import IntegrityError

logger = logging.getLogger(__name__)

class PositionDialogViewModel(QObject):
    position_saved = Signal()
    error_occurred = Signal(str)

    def __init__(self, db_session, position_data: Position = None, parent=None):
        super().__init__(parent)
        self.session = db_session
        self._position_data = position_data

        if self.is_editing():
            self._id = self._position_data.id
            self._name = self._position_data.name
        else:
            self._id = None
            self._name = ""

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    def is_editing(self) -> bool:
        """檢查是否為編輯模式。"""
        return self._position_data is not None

    def save(self):
        """儲存職務資料 (新增或更新)。"""
        try:
            if not self._name.strip():
                self.error_occurred.emit("職務名稱不能為空。")
                return

            if self.is_editing():
                self._position_data.name = self._name
                logger.info(f"Updating position ID: {self._id} with name: {self._name}")
            else:
                new_position = Position(name=self._name)
                self.session.add(new_position)
                logger.info(f"Adding new position with name: {self._name}")

            self.session.commit()
            logger.info("Position saved successfully.")
            self.position_saved.emit()
        except IntegrityError as e:
            self.session.rollback()
            logger.error(f"Integrity error saving position: {e}")
            if "UNIQUE constraint failed: positions.name" in str(e):
                self.error_occurred.emit("職務名稱已存在，請使用其他名稱。")
            else:
                self.error_occurred.emit(f"儲存職務時發生資料庫完整性錯誤: {e}")
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error saving position: {e}")
            self.error_occurred.emit(f"儲存職務時發生未知錯誤: {e}")
