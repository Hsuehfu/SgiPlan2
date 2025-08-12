from PySide6.QtCore import QObject, Signal, Qt
from models.member_model import Member
from models.region_model import Region
from models.database import Session
from sqlalchemy import or_

class MemberListViewModel(QObject):
    members_loaded = Signal(list)
    regions_loaded = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_search_term = None
        self.current_region_id = None
        self.current_sort_column = None
        self.current_sort_order = Qt.AscendingOrder

    def load_members(self, search_term=None, region_id=None, sort_column=None, sort_order=None):
        session = Session()
        try:
            # Update current filter/sort parameters
            if search_term is not None:
                self.current_search_term = search_term
            if region_id is not None:
                self.current_region_id = region_id
            if sort_column is not None:
                self.current_sort_column = sort_column
            if sort_order is not None:
                self.current_sort_order = sort_order

            query = session.query(Member)

            # Apply search filter
            if self.current_search_term:
                query = query.filter(Member.name.ilike(f"%{self.current_search_term}%"))

            # Apply region filter
            if self.current_region_id and self.current_region_id != -1:
                query = query.filter(Member.region_id == self.current_region_id)

            # Apply sorting
            if self.current_sort_column is not None:
                if self.current_sort_column == 0: # Name column
                    if self.current_sort_order == Qt.AscendingOrder:
                        query = query.order_by(Member.name.asc())
                    else:
                        query = query.order_by(Member.name.desc())
                elif self.current_sort_column == 1: # Region column
                    # Need to join with Region table for sorting by region name
                    query = query.join(Region)
                    if self.current_sort_order == Qt.AscendingOrder:
                        query = query.order_by(Region.name.asc())
                    else:
                        query = query.order_by(Region.name.desc())

            members = query.all()
            self.members_loaded.emit(members)
        except Exception as e:
            print(f"Error loading members: {e}")
        finally:
            session.close()

    def load_regions(self):
        session = Session()
        try:
            regions = session.query(Region).all()
            self.regions_loaded.emit(regions)
        except Exception as e:
            print(f"Error loading regions: {e}")
        finally:
            session.close()

    def delete_member(self, member_id):
        session = Session()
        try:
            member = session.query(Member).filter_by(id=member_id).first()
            if member:
                session.delete(member)
                session.commit()
                self.load_members(search_term=self.current_search_term, region_id=self.current_region_id, sort_column=self.current_sort_column, sort_order=self.current_sort_order)
        except Exception as e:
            print(f"Error deleting member: {e}")
            session.rollback()
        finally:
            session.close()

    def sort_members(self, column_index, order):
        self.load_members(sort_column=column_index, sort_order=order)
