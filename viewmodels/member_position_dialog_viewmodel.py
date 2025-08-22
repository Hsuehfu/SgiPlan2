from PySide6.QtCore import QObject, Signal
from models.position_model import Position
from models.database import Session

class MemberPositionDialogViewModel(QObject):
    positions_loaded = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)

    def load_positions(self):
        session = Session()
        try:
            positions = session.query(Position).all()
            self.positions_loaded.emit(positions)
        except Exception as e:
            print(f"Error loading positions: {e}")
        finally:
            session.close()
