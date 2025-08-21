from PySide6.QtCore import QObject, Signal, Qt
from models.region_model import Region
from sqlalchemy.orm import joinedload

class RegionListViewModel(QObject):
    regions_loaded = Signal(list)
    error_occurred = Signal(str)

    def __init__(self, db_session, parent=None):
        super().__init__(parent)
        self.session = db_session
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

            query = self.session.query(Region)

            if self.current_search_term:
                query = query.filter(Region.name.ilike(f"%{self.current_search_term}%"))

            if self.current_sort_column is not None:
                sort_field = None
                if self.current_sort_column == 0:  # ID 欄位
                    sort_field = Region.id
                elif self.current_sort_column == 1:  # 地區名稱欄位
                    sort_field = Region.name

                if sort_field is not None:
                    if self.current_sort_order == Qt.AscendingOrder:
                        query = query.order_by(sort_field.asc())
                    else:
                        query = query.order_by(sort_field.desc())

            regions = query.all()
            self.regions_loaded.emit(regions)
        except Exception as e:
            self.error_occurred.emit(f"載入地區時發生錯誤: {e}")
        
    def delete_region(self, region_id):       
        try:
            # 使用 joinedload 預先載入子地區，以便進行檢查
            region = self.session.query(Region).options(joinedload(Region.children)).filter_by(id=region_id).first()
            
            if region:
                # [新增] 檢查是否有子地區
                if region.children:
                    self.error_occurred.emit(f"無法刪除地區 '{region.name}'，\n因为它底下還有子地區。")
                    return

                self.session.delete(region)
                self.session.commit()
                self.load_regions(search_term=self.current_search_term, sort_column=self.current_sort_column, sort_order=self.current_sort_order)
            else:
                self.error_occurred.emit("找不到要刪除的地區。")
        except Exception as e:
            self.error_occurred.emit(f"刪除地區時發生錯誤: {e}")
            self.session.rollback()
               
    def sort_regions(self, column_index, order):
        self.load_regions(sort_column=column_index, sort_order=order)

    