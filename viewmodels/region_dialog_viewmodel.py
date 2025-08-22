import logging
from PySide6.QtCore import QObject, Signal
from sqlalchemy.exc import IntegrityError
from models.region_model import Region

logger = logging.getLogger(__name__)


class RegionDialogViewModel(QObject):
    saved_successfully = Signal()
    save_failed = Signal(str)
    parents_loaded = Signal(list)
    load_failed = Signal(str) 

    def __init__(self, db_session, region_data: Region = None, parent=None):
        super().__init__(parent)
        self.session = db_session  # 持有傳入的共享 Session
        self._region_data = region_data  # This is the original model object for editing

        if self.is_editing():
            # Editing mode: initialize state from the model object
            self._id = self._region_data.id
            self._name = self._region_data.name
            self._parent_id = self._region_data.parent_id
        else:
            # Add mode: initialize with empty state
            self._id = None
            self._name = ""
            self._parent_id = None

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
                # Update existing region. The object is already in the session.
                self._region_data.name = self._name
                self._region_data.parent_id = self._parent_id
                logger.info(f"Updating region ID: {self._id} with name: {self._name}")
            else:
                # Add new region
                new_region = Region(name=self._name, parent_id=self._parent_id)
                self.session.add(new_region)
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

    def _get_all_descendant_ids(self, region_id):
        """遞迴獲取一個地區的所有後代ID。"""
        descendant_ids = set()
        children = (
            self.session.query(Region.id).filter(Region.parent_id == region_id).all()
        )

        for (child_id,) in children:
            if child_id not in descendant_ids:
                descendant_ids.add(child_id)
                descendant_ids.update(self._get_all_descendant_ids(child_id))
        return descendant_ids

    def load_possible_parents(self):
        """載入所有可作為父級的地區列表。"""
        try:
            query = self.session.query(Region)
            if self.is_editing():
                # 建立一個禁止成為父級的ID列表
                excluded_ids = {self._id}  # 排除自己
                descendant_ids = self._get_all_descendant_ids(self._id)
                excluded_ids.update(descendant_ids)

                query = query.filter(Region.id.notin_(excluded_ids))

            parents = query.order_by(Region.name).all()
            self.parents_loaded.emit(parents)
        except Exception as e:
            logger.error(f"Error loading parent regions: {e}")
            # 注意：這裡的錯誤處理也有問題，請見下一點
            self.parents_loaded.emit([])  # 發送一個空列表，而不是錯誤字串
            self.load_failed.emit(
                f"載入父級地區時發生錯誤: {e}"
            )  # 使用另一個信號來傳遞錯誤訊息
