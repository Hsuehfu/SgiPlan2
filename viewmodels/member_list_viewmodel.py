from PySide6.QtCore import QObject, Signal, Qt
from repositories.member_repository import MemberRepository
from repositories.region_repository import RegionRepository

class MemberListViewModel(QObject):
    items_loaded = Signal(list)
    regions_loaded = Signal(list)
    members_count_changed = Signal(int)

    def __init__(self, db_session, parent=None):
        super().__init__(parent)
        self.session = db_session
        self.member_repo = MemberRepository(db_session)
        self.region_repo = RegionRepository(db_session)
        self.current_search_term = None
        self.current_region_id = None
        self.current_sort_column = None
        self.current_sort_order = Qt.AscendingOrder

    def load_members(self, search_term=None, region_id=None, sort_column=None, sort_order=None):
        try:
            if search_term is not None:
                self.current_search_term = search_term
            if region_id is not None:
                self.current_region_id = region_id
            if sort_column is not None:
                self.current_sort_column = sort_column
            if sort_order is not None:
                self.current_sort_order = sort_order

            members = self.member_repo.search(
                search_term=self.current_search_term,
                region_id=self.current_region_id,
                sort_column=self.current_sort_column,
                sort_order=self.current_sort_order
            )
            self.items_loaded.emit(members)
            self.members_count_changed.emit(len(members))
        except Exception as e:
            print(f"Error loading members: {e}")

    def load_regions(self):
        try:
            regions = self.region_repo.get_all()
            self.regions_loaded.emit(regions)
        except Exception as e:
            print(f"Error loading regions: {e}")

    def delete_member(self, member_id):
        try:
            if self.member_repo.delete_by_id(member_id):
                self.session.commit()
                self.load_members(
                    search_term=self.current_search_term, 
                    region_id=self.current_region_id, 
                    sort_column=self.current_sort_column, 
                    sort_order=self.current_sort_order
                )
        except Exception as e:
            print(f"Error deleting member: {e}")
            self.session.rollback()

    def sort_members(self, column_index, order):
        self.load_members(sort_column=column_index, sort_order=order)
