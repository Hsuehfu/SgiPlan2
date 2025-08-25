from PySide6.QtCore import QObject, Signal, Qt
from repositories.region_repository import RegionRepository

class RegionListViewModel(QObject):
    items_loaded = Signal(list)
    error_occurred = Signal(str)

    def __init__(self, db_session, parent=None):
        super().__init__(parent)
        self.session = db_session
        self.region_repo = RegionRepository(db_session)
        self.current_search_term = None
        self.current_sort_column = None
        self.current_sort_order = Qt.AscendingOrder

    def load_regions(self, search_term=None, sort_column=None, sort_order=None):
        try:
            if search_term is not None:
                self.current_search_term = search_term
            if sort_column is not None:
                self.current_sort_column = sort_column
            if sort_order is not None:
                self.current_sort_order = sort_order

            regions = self.region_repo.search(
                search_term=self.current_search_term, 
                sort_column=self.current_sort_column, 
                sort_order=self.current_sort_order
            )
            self.items_loaded.emit(regions)
        except Exception as e:
            self.error_occurred.emit(f"載入地區時發生錯誤: {e}")
        
    def delete_region(self, region_id):
        try:
            region = self.region_repo.get_by_id_with_children(region_id)
            
            if region:
                if region.children:
                    self.error_occurred.emit(f"無法刪除地區 '{region.name}'，\n因为它底下還有子地區。")
                    return

                self.region_repo.delete(region)
                self.session.commit()
                self.load_regions(search_term=self.current_search_term, sort_column=self.current_sort_column, sort_order=self.current_sort_order)
            else:
                self.error_occurred.emit("找不到要刪除的地區。")
        except Exception as e:
            self.error_occurred.emit(f"刪除地區時發生錯誤: {e}")
            self.session.rollback()
               
    def sort_regions(self, column_index, order):
        self.load_regions(sort_column=column_index, sort_order=order)

    