import logging
from PySide6.QtCore import QObject, Signal
from models.region_model import Region

logger = logging.getLogger(__name__)

class RegionDialogViewModel(QObject):
    error_occurred = Signal(str)
    region_saved = Signal()

    def __init__(self, db_session, region_data: Region = None, parent=None):
        super().__init__(parent)
        self.session = db_session  # 持有傳入的共享 Session
        self._region_data = region_data  # This is the original model object for editing

        if self.is_editing():
            # Editing mode: initialize state from the model object
            self._id = self._region_data.id
            self._name = self._region_data.name
        else:
            # Add mode: initialize with empty state
            self._id = None
            self._name = ""

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    def is_editing(self) -> bool:
        """Check if the viewmodel is in editing mode."""
        return self._region_data is not None

    def save(self):
        """Save the region data (either add new or update existing)."""
        try:
            if not self._name.strip():
                self.error_occurred.emit("地區名稱不能為空。")
                return

            if self.is_editing():
                # Update existing region. The object is already in the session.
                self._region_data.name = self._name
                logger.info(f"Updating region ID: {self._id} with name: {self._name}")
            else:
                # Add new region
                new_region = Region(name=self._name)
                self.session.add(new_region)
                logger.info(f"Adding new region with name: {self._name}")

            self.session.commit()
            logger.info("Region saved successfully.")
            self.region_saved.emit()

        except Exception as e:
            self.session.rollback()
            logger.error(f"Error saving region: {e}")
            self.error_occurred.emit(f"儲存地區時發生錯誤: {e}")
