import logging
from PySide6.QtCore import QObject, Signal
from models.region_model import Region
from models.database import Session

loggin = logging.getLogger(__name__)

class RegionDialogViewModel(QObject):
    error_occurred = Signal(str)
    region_saved = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def add_region(self, region_data):
        session = Session()
        try:
            new_region = Region(**region_data)
            session.add(new_region)
            session.commit()
            self.region_saved.emit()
            loggin.info("Region added successfully.")
        except Exception as e:
            self.error_occurred.emit(f"新增錯誤: {e}")
            loggin.error(f"Error adding region: {e}")
            session.rollback()
        finally:
            session.close()

    def update_region(self, region_id, region_data):
        session = Session()
        try:
            region = session.query(Region).filter_by(id=region_id).first()
            if region:
                region.name = region_data['name']
                session.commit()
                self.region_saved.emit()
            else:
                self.error_occurred.emit("找不到要修改的區域。")
                logging.error("Region not found for update.")
        except Exception as e:
            self.error_occurred.emit(f"修改錯誤: {e}")
            logging.error(f"Error updating region: {e}")
            session.rollback()
        finally:
            session.close()
