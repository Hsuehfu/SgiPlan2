from PySide6.QtCore import QObject, Signal
from models.region_model import Region
from models.member_model import Member
from models.database import Session

class MemberDialogViewModel(QObject):
    regions_loaded = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)

    def load_regions(self):
        session = Session()
        try:
            regions = session.query(Region).all()
            self.regions_loaded.emit(regions)
        except Exception as e:
            print(f"Error loading regions: {e}")
        finally:
            session.close()

    def add_member(self, member_data):
        session = Session()
        try:
            new_member = Member(**member_data)
            session.add(new_member)
            session.commit()
        except Exception as e:
            print(f"Error adding member: {e}")
            session.rollback()
        finally:
            session.close()

    def update_member(self, member_id, member_data):
        session = Session()
        try:
            member = session.query(Member).filter_by(id=member_id).first()
            if member:
                member.name = member_data['name']
                member.region_id = member_data['region_id']
                session.commit()
        except Exception as e:
            print(f"Error updating member: {e}")
            session.rollback()
        finally:
            session.close()