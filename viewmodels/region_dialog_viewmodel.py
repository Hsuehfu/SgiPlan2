from PySide6.QtCore import QObject, Signal
from models.region_model import Region
from models.database import Session

class RegionDialogViewModel(QObject):

    def __init__(self, parent=None):
        super().__init__(parent)

    def add_region(self, region_data):
        session = Session()
        try:
            new_region = Region(**region_data)
            session.add(new_region)
            session.commit()
        except Exception as e:
            print(f"Error adding region: {e}")
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
        except Exception as e:
            print(f"Error updating region: {e}")
            session.rollback()
        finally:
            session.close()
