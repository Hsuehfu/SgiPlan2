import logging
from PySide6.QtCore import QObject, Signal
from sqlalchemy.exc import IntegrityError
from models.region_model import Region
from repositories.region_repository import RegionRepository

logger = logging.getLogger(__name__)


class RegionDialogViewModel(QObject):
    saved_successfully = Signal()
    save_failed = Signal(str)
    parents_loaded = Signal(list)
    load_failed = Signal(str) 

    def __init__(self, db_session, region_data: Region = None, initial_parent_id: int = None, parent=None):
        super().__init__(parent)
        self.session = db_session
        self.region_repo = RegionRepository(db_session)
        self._region_data = region_data

        if self.is_editing():
            self._id = self._region_data.id
            self._name = self._region_data.name
            self._parent_id = self._region_data.parent_id
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
        """Check if the viewmodel is in editing mode."""
        return self._region_data is not None

    def save(self):
        """Save the region data (either add new or update existing)."""
        try:
            if not self._name.strip():
                self.save_failed.emit("地區名稱不能為空。")
                return

            if self.is_editing():
                self._region_data.name = self._name
                self._region_data.parent_id = self._parent_id
                logger.info(f"Updating region ID: {self._id} with name: {self._name}")
            else:
                new_region = Region(name=self._name, parent_id=self._parent_id)
                self.region_repo.add(new_region)
                logger.info(f"Adding new region with name: {self._name}")

            self.session.commit()
            logger.info("Region saved successfully.")
            self.saved_successfully.emit()

        except IntegrityError as e:
            self.session.rollback()
            logger.warning(f"Integrity error on save: {e}")
            self.save_failed.emit("儲存失敗，可能是地區名稱在同級目錄下已存在。")
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error saving region: {e}")
            self.save_failed.emit(f"儲存地區時發生錯誤: {e}")

    def load_possible_parents(self):
        """載入所有可作為父級的地區列表。"""
        try:
            region_id_to_exclude = self._id if self.is_editing() else None
            parents = self.region_repo.get_possible_parents(region_id_to_exclude)
            self.parents_loaded.emit(parents)
        except Exception as e:
            logger.error(f"Error loading parent regions: {e}")
            self.parents_loaded.emit([])
            self.load_failed.emit(f"載入父級地區時發生錯誤: {e}")
