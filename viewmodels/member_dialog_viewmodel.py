# viewmodels/member_dialog_viewmodel.py

from PySide6.QtCore import QObject, Signal
from sqlalchemy.exc import IntegrityError
from models.region_model import Region
from models.member_model import Member
from models.position_model import Position
from models.member_position_model import MemberPosition

class MemberDialogViewModel(QObject):
    """
    ViewModel for the member creation/editing dialog.
    Manages the state and logic for creating or updating a member,
    including their assigned positions.
    """
    regions_loaded = Signal(list)
    saved_successfully = Signal()
    save_failed = Signal(str)
    positions_loaded = Signal(list)
    assigned_positions_changed = Signal(list)

    def __init__(self, db_session, member_data=None, parent=None):
        super().__init__(parent)
        self.session = db_session
        self._member_data = member_data

        self._all_positions = []  # Stores all available Position objects
        # Stores MemberPosition objects for the current member
        self._assigned_positions = []
        # A temporary store for position changes before saving
        self._position_assignments_to_update = []

        if self._member_data:  # Edit mode
            self._name = self._member_data.name
            self._phone_number = self._member_data.phone_number
            self._is_schedulable = bool(self._member_data.is_schedulable)
            self._region_id = self._member_data.region_id
            # Load existing assigned positions
            self._assigned_positions = list(self._member_data.positions)
        else:  # Add mode
            self._name = ""
            self._phone_number = ""
            self._is_schedulable = True
            self._region_id = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def phone_number(self):
        return self._phone_number if self._phone_number is not None else ""

    @phone_number.setter
    def phone_number(self, value):
        self._phone_number = value if value else None

    @property
    def is_schedulable(self):
        return self._is_schedulable

    @is_schedulable.setter
    def is_schedulable(self, value):
        self._is_schedulable = value

    @property
    def region_id(self):
        return self._region_id

    @region_id.setter
    def region_id(self, value):
        self._region_id = value

    @property
    def all_positions(self) -> list[Position]:
        """Returns the list of all available positions."""
        return self._all_positions

    @property
    def assigned_positions(self) -> list[MemberPosition]:
        """Returns the list of currently assigned positions for the member."""
        return self._assigned_positions

    def load_regions(self):
        """Loads region data from the database."""
        try:
            regions = self.session.query(Region).order_by(Region.id).all()
            region_data = [(region.id, region.name) for region in regions]
            self.regions_loaded.emit(region_data)
        except Exception as e:
            print(f"Error loading regions: {e}")
            self.regions_loaded.emit([])

    def load_positions(self):
        """Loads all available positions from the database."""
        try:
            self._all_positions = self.session.query(Position).order_by(Position.rank.desc()).all()
            # Emit data suitable for a view, e.g., a list of (id, name) tuples
            position_data = [(pos.id, pos.name) for pos in self._all_positions]
            self.positions_loaded.emit(position_data)
        except Exception as e:
            print(f"Error loading positions: {e}")
            self.positions_loaded.emit([])

    def add_position(self, position_id: int, is_primary: bool = False):
        """
        Adds a position to the member's assigned positions list.
        Note: This only stages the change. Call save() to persist.
        """
        # Check if this position is already assigned
        if any(mp.position_id == position_id for mp in self._assigned_positions):
            print(f"Position {position_id} is already assigned.")
            return

        position = self.session.query(Position).get(position_id)
        if position:
            # If setting a new primary, ensure no other position is primary
            if is_primary:
                for mp in self._assigned_positions:
                    mp.is_primary = False

            new_assignment = MemberPosition(
                member_id=self._member_data.id if self.is_editing() else None,
                position_id=position_id,
                is_primary=is_primary,
                position=position  # Associate the Position object
            )
            self._assigned_positions.append(new_assignment)
            self.assigned_positions_changed.emit(self.get_assigned_positions_for_view())

    def remove_position(self, position_id: int):
        """
        Removes a position from the member's assigned positions list.
        Note: This only stages the change. Call save() to persist.
        """
        self._assigned_positions = [
            mp for mp in self._assigned_positions if mp.position_id != position_id
        ]
        self.assigned_positions_changed.emit(self.get_assigned_positions_for_view())

    def set_primary_position(self, position_id: int):
        """Sets a specific assigned position as the primary one."""
        for mp in self._assigned_positions:
            mp.is_primary = (mp.position_id == position_id)
        self.assigned_positions_changed.emit(self.get_assigned_positions_for_view())

    def get_assigned_positions_for_view(self) -> list[dict]:
        """
        Returns a list of dictionaries representing assigned positions,
        suitable for display in the view.
        """
        return [
            {"id": mp.position_id, "name": mp.position.name, "is_primary": mp.is_primary}
            for mp in self._assigned_positions
        ]

    def save(self):
        """Saves member data and their position assignments."""
        if not self._name or not self._name.strip():
            self.save_failed.emit("姓名不能為空。")
            return
            
        try:
            # Step 1: Save Member object to get an ID for new members
            if self.is_editing():
                member = self._member_data
                member.name = self._name
                member.phone_number = self._phone_number
                member.is_schedulable = self._is_schedulable
                member.region_id = self._region_id
            else:
                member = Member(
                    name=self._name,
                    phone_number=self._phone_number,
                    is_schedulable=self._is_schedulable,
                    region_id=self._region_id
                )
                self.session.add(member)
            
            # We need to flush to get the member.id for new members
            self.session.flush()

            # Step 2: Synchronize MemberPosition associations
            existing_assignments = {
                mp.position_id: mp for mp in member.positions
            }
            current_assignment_pids = {mp.position_id for mp in self._assigned_positions}

            # Delete positions that were removed
            for pid, assignment in existing_assignments.items():
                if pid not in current_assignment_pids:
                    self.session.delete(assignment)

            # Add or update positions
            for mp_stub in self._assigned_positions:
                if mp_stub.position_id in existing_assignments:
                    # Update existing one
                    existing_mp = existing_assignments[mp_stub.position_id]
                    existing_mp.is_primary = mp_stub.is_primary
                else:
                    # Add new one
                    new_mp = MemberPosition(
                        member_id=member.id,
                        position_id=mp_stub.position_id,
                        is_primary=mp_stub.is_primary
                    )
                    self.session.add(new_mp)

            self.session.commit()
            self.saved_successfully.emit()
            
        except IntegrityError as e:
            self.session.rollback()
            if "UNIQUE constraint failed: members.phone_number" in str(e):
                self.save_failed.emit("電話號碼重複，請輸入不同的號碼。")
            else:
                self.save_failed.emit(f"儲存失敗，資料庫錯誤：\n{e}")
        except Exception as e:
            self.session.rollback()
            print(f"Error saving member data: {e}")
            self.save_failed.emit(f"發生未預期的錯誤：\n{e}")

    def is_editing(self) -> bool:
        """Checks if the ViewModel is in edit mode."""
        return self._member_data is not None
