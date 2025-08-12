from PySide6.QtCore import QObject, Signal, Qt
from models.region_model import Region
from models.database import Session

class RegionListViewModel(QObject):
    regions_loaded = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_search_term = None
        self.current_sort_column = None
        self.current_sort_order = Qt.AscendingOrder

    def load_regions(self, search_term=None, sort_column=None, sort_order=None):
        session = Session()
        try:
            if search_term is not None:
                self.current_search_term = search_term
            if sort_column is not None:
                self.current_sort_column = sort_column
            if sort_order is not None:
                self.current_sort_order = sort_order

            query = session.query(Region)

            if self.current_search_term:
                query = query.filter(Region.name.ilike(f"%{self.current_search_term}%"))

            if self.current_sort_column is not None:
                if self.current_sort_column == 0: # Name column
                    if self.current_sort_order == Qt.AscendingOrder:
                        query = query.order_by(Region.name.asc())
                    else:
                        query = query.order_by(Region.name.desc())

            regions = query.all()
            self.regions_loaded.emit(regions)
        except Exception as e:
            print(f"Error loading regions: {e}")
        finally:
            session.close()

    def add_region(self, region_data):
        session = Session()
        try:
            new_region = Region(**region_data)
            session.add(new_region)
            session.commit()
            self.load_regions(search_term=self.current_search_term, sort_column=self.current_sort_column, sort_order=self.current_sort_order)
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
                self.load_regions(search_term=self.current_search_term, sort_column=self.current_sort_column, sort_order=self.current_sort_order)
        except Exception as e:
            print(f"Error updating region: {e}")
            session.rollback()
        finally:
            session.close()

    def delete_region(self, region_id):
        session = Session()
        try:
            region = session.query(Region).filter_by(id=region_id).first()
            if region:
                session.delete(region)
                session.commit()
                self.load_regions(search_term=self.current_search_term, sort_column=self.current_sort_column, sort_order=self.current_sort_order)
        except Exception as e:
            print(f"Error deleting region: {e}")
            session.rollback()
        finally:
            session.close()

    def sort_regions(self, column_index, order):
        self.load_regions(sort_column=column_index, sort_order=order)
