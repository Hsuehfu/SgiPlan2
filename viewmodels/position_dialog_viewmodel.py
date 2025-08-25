import logging
from PySide6.QtCore import QObject, Signal
from models.position_model import Position
from repositories.position_repository import PositionRepository
from sqlalchemy.exc import IntegrityError

logger = logging.getLogger(__name__)

class PositionDialogViewModel(QObject):
    position_saved = Signal()
    error_occurred = Signal(str)
    parents_loaded = Signal(list)
    load_failed = Signal(str)

    def __init__(self, db_session, position_data: Position = None, initial_parent_id: int = None, parent=None):
        super().__init__(parent)
        self.session = db_session
        self.position_repo = PositionRepository(db_session)
        self._position_data = position_data

        if self.is_editing():
            self._id = self._position_data.id
            self._name = self._position_data.name
            self._parent_id = self._position_data.parent_id
        else:
            self._id = None
            self._name = ""
            self._parent_id = initial_parent_id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def parent_id(self):
        return self._parent_id

    @parent_id.setter
    def parent_id(self, value):
        self._parent_id = value

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
                self._position_data.parent_id = self._parent_id
                logger.info(f"Updating position ID: {self._id} with name: {self._name}")
            else:
                new_position = Position(name=self._name, parent_id=self._parent_id)
                self.position_repo.add(new_position)
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

    def load_possible_parents(self):
        """載入所有可作為父級的職務列表。"""
        try:
            position_id_to_exclude = self._id if self.is_editing() else None
            parents = self.position_repo.get_possible_parents(position_id_to_exclude)
            self.parents_loaded.emit(parents)
        except Exception as e:
            logger.error(f"Error loading parent positions: {e}")
            self.parents_loaded.emit([])
            self.load_failed.emit(f"載入父級職務時發生錯誤: {e}")
