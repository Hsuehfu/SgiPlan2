import logging
from PySide6.QtCore import QObject, Signal
from sqlalchemy.exc import IntegrityError
from models.member_model import Member
from models.position_model import Position
from models.member_position_model import MemberPosition

from repositories.member_repository import MemberRepository
from repositories.region_repository import RegionRepository
from repositories.department_repository import DepartmentRepository
from repositories.position_repository import PositionRepository
from repositories.member_position_repository import MemberPositionRepository

logger = logging.getLogger(__name__)

class MemberDialogViewModel(QObject):
    """
    ViewModel for the member creation/editing dialog.
    Manages the state and logic for creating or updating a member,
    including their assigned positions.
    """
    regions_loaded = Signal(list)
    departments_loaded = Signal(list)
    saved_successfully = Signal()
    save_failed = Signal(str)
    positions_loaded = Signal(list)
    assigned_positions_changed = Signal(list)

    def __init__(self, db_session, member_data=None, parent=None):
        super().__init__(parent)
        self.session = db_session
        self._member_data = member_data

        # Repositories
        self.member_repo = MemberRepository(db_session)
        self.region_repo = RegionRepository(db_session)
        self.department_repo = DepartmentRepository(db_session)
        self.position_repo = PositionRepository(db_session)
        self.member_position_repo = MemberPositionRepository(db_session)

        self._all_positions = []
        self._assigned_positions = []

        if self._member_data:  # Edit mode
            logger.debug(f"Initializing MemberDialogViewModel in edit mode for member ID: {self._member_data.id}")
            self._name = self._member_data.name
            self._phone_number = self._member_data.phone_number
            self._is_schedulable = bool(self._member_data.is_schedulable)
            self._region_id = self._member_data.region_id
            self._department_id = self._member_data.department_id
            self._assigned_positions = list(self._member_data.positions)
        else:  # Add mode
            logger.debug("Initializing MemberDialogViewModel in add mode.")
            self._name = ""
            self._phone_number = ""
            self._is_schedulable = True
            self._region_id = None
            self._department_id = None

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
    def department_id(self):
        return self._department_id

    @department_id.setter
    def department_id(self, value):
        self._department_id = value

    @property
    def all_positions(self) -> list[Position]:
        return self._all_positions

    @property
    def assigned_positions(self) -> list[MemberPosition]:
        return self._assigned_positions

    def load_regions(self):
        logger.debug("Loading regions.")
        try:
            regions = self.region_repo.get_all()
            region_data = [(region.id, region.name) for region in regions]
            self.regions_loaded.emit(region_data)
        except Exception as e:
            logger.error(f"Error loading regions: {e}")
            self.regions_loaded.emit([])

    def load_departments(self):
        logger.debug("Loading departments.")
        try:
            departments = self.department_repo.get_all()
            department_data = [(department.id, department.name) for department in departments]
            self.departments_loaded.emit(department_data)
        except Exception as e:
            logger.error(f"Error loading departments: {e}")
            self.departments_loaded.emit([])

    def load_positions(self):
        logger.debug("Loading positions.")
        try:
            self._all_positions = self.position_repo.get_all_sorted_by_rank()
            position_data = [(pos.id, pos.name) for pos in self._all_positions]
            self.positions_loaded.emit(position_data)
        except Exception as e:
            logger.error(f"Error loading positions: {e}")
            self.positions_loaded.emit([])

    def add_position(self, position_id: int, is_primary: bool = False):
        if any(mp.position_id == position_id for mp in self._assigned_positions):
            logger.warning(f"Attempted to add already assigned position ID: {position_id}")
            return

        position = self.position_repo.get_by_id(position_id)
        if position:
            logger.debug(f"Adding position ID: {position_id} to member.")
            if is_primary:
                for mp in self._assigned_positions:
                    mp.is_primary = False

            new_assignment = MemberPosition(
                member_id=self._member_data.id if self.is_editing() else None,
                position_id=position_id,
                is_primary=is_primary,
                position=position
            )
            self._assigned_positions.append(new_assignment)
            self.assigned_positions_changed.emit(self.get_assigned_positions_for_view())

    def remove_position(self, position_id: int):
        logger.debug(f"Removing position ID: {position_id} from member.")
        self._assigned_positions = [
            mp for mp in self._assigned_positions if mp.position_id != position_id
        ]
        self.assigned_positions_changed.emit(self.get_assigned_positions_for_view())

    def set_primary_position(self, position_id: int):
        logger.debug(f"Setting primary position to ID: {position_id}.")
        for mp in self._assigned_positions:
            mp.is_primary = (mp.position_id == position_id)
        self.assigned_positions_changed.emit(self.get_assigned_positions_for_view())

    def get_assigned_positions_for_view(self) -> list[dict]:
        return [
            {"id": mp.position_id, "name": mp.position.name, "is_primary": mp.is_primary}
            for mp in self._assigned_positions
        ]

    def save(self):
        logger.info("Attempting to save member data.")
        if not self._name or not self._name.strip():
            logger.warning("Save failed: Name is empty.")
            self.save_failed.emit("姓名不能為空。")
            return
            
        try:
            if self.is_editing():
                logger.info(f"Updating member ID: {self._member_data.id}")
                member = self._member_data
                member.name = self._name
                member.phone_number = self._phone_number
                member.is_schedulable = self._is_schedulable
                member.region_id = self._region_id
                member.department_id = self._department_id
            else:
                logger.info(f"Creating new member with name: {self._name}")
                member = Member(
                    name=self._name,
                    phone_number=self._phone_number,
                    is_schedulable=self._is_schedulable,
                    region_id=self._region_id,
                    department_id=self._department_id
                )
                self.member_repo.add(member)
            
            self.session.flush()
            logger.debug(f"Member flushed. ID is now: {member.id}")

            existing_assignments = {mp.position_id: mp for mp in member.positions}
            current_assignment_pids = {mp.position_id for mp in self._assigned_positions}

            logger.debug(f"Synchronizing positions. Existing: {list(existing_assignments.keys())}, Current: {list(current_assignment_pids)}")
            for pid, assignment in existing_assignments.items():
                if pid not in current_assignment_pids:
                    logger.debug(f"Deleting position assignment for position ID: {pid}")
                    self.member_position_repo.delete(assignment)

            for mp_stub in self._assigned_positions:
                if mp_stub.position_id in existing_assignments:
                    existing_mp = existing_assignments[mp_stub.position_id]
                    if existing_mp.is_primary != mp_stub.is_primary:
                        logger.debug(f"Updating primary status for position ID: {mp_stub.position_id}")
                        existing_mp.is_primary = mp_stub.is_primary
                else:
                    logger.debug(f"Adding new position assignment for position ID: {mp_stub.position_id}")
                    new_mp = MemberPosition(
                        member_id=member.id,
                        position_id=mp_stub.position_id,
                        is_primary=mp_stub.is_primary
                    )
                    self.member_position_repo.add(new_mp)

            self.session.commit()
            logger.info(f"Successfully saved member ID: {member.id}")
            self.saved_successfully.emit()
            
        except IntegrityError as e:
            self.session.rollback()
            logger.warning(f"Database integrity error on save: {e}")
            if "UNIQUE constraint failed: members.phone_number" in str(e):
                self.save_failed.emit("電話號碼重複，請輸入不同的號碼。")
            else:
                self.save_failed.emit(f"儲存失敗，資料庫錯誤：{e}")
        except Exception as e:
            self.session.rollback()
            logger.error(f"Unexpected error saving member data: {e}", exc_info=True)
            self.save_failed.emit(f"發生未預期的錯誤：{e}")

    def is_editing(self) -> bool:
        return self._member_data is not None
