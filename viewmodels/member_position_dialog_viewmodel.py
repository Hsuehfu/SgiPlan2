from PySide6.QtCore import QObject, Signal
from repositories.position_repository import PositionRepository

class MemberPositionDialogViewModel(QObject):
    positions_loaded = Signal(list)

    def __init__(self, db_session, parent=None):
        super().__init__(parent)
        self.position_repo = PositionRepository(db_session)

    def load_positions(self):
        try:
            positions = self.position_repo.get_all()
            self.positions_loaded.emit(positions)
        except Exception as e:
            print(f"Error loading positions: {e}")
