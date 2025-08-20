from PySide6.QtWidgets import QTableWidgetItem, QMessageBox
from views.base_list_widget import BaseListWidget
from views.region_dialog import RegionDialog
from viewmodels.region_dialog_viewmodel import RegionDialogViewModel

class RegionListWidget(BaseListWidget):
    def __init__(self, viewmodel, parent=None):
        super().__init__(viewmodel, parent)
        self.viewmodel.regions_loaded.connect(self.display_items)
        self.viewmodel.error_occurred.connect(self._show_error_message)

    def _get_window_title(self):
        return "地區管理"

    def _get_search_placeholder(self):
        return "搜尋地區名稱..."

    def _get_table_headers(self):
        return ["ID", "地區名稱"]

    def _filter_changed(self):
        self._load_items()

    def _sort_items(self, column_index):
        order = self.table_widget.horizontalHeader().sortIndicatorOrder()
        self.viewmodel.sort_regions(column_index, order)

    def display_items(self, items):
        self.items = items
        self.table_widget.setRowCount(len(items))
        for i, item in enumerate(items):
            self._display_item_row(i, item)

    def _display_item_row(self, row, region):
        self.table_widget.setItem(row, 0, QTableWidgetItem(str(region.id)))
        self.table_widget.setItem(row, 1, QTableWidgetItem(region.name))

    def _get_item_name(self, region):
        return region.name

    def _perform_delete(self, region_id):
        self.viewmodel.delete_region(region_id)

    def _get_dialog_viewmodel_class(self):
        return RegionDialogViewModel

    def _get_dialog_class(self):
        return RegionDialog

    # [新增] 覆寫 BaseListWidget 的方法，採用 PositionListWidget 的正確模式
    def open_add_dialog(self):
        """處理新增地區的操作。"""
        dialog_viewmodel = RegionDialogViewModel(db_session=self.viewmodel.session)
        dialog_viewmodel.region_saved.connect(self._load_items)
        
        dialog = RegionDialog(dialog_viewmodel, self)
        dialog.exec()

    def open_edit_dialog(self):
        """處理編輯地區的操作。"""
        selected_row = self.table_widget.currentRow()
        if selected_row >= 0:
            region_to_edit = self.items[selected_row]
            dialog_viewmodel = RegionDialogViewModel(
                db_session=self.viewmodel.session, 
                region_data=region_to_edit
            )
            dialog_viewmodel.region_saved.connect(self._load_items)
            
            dialog = RegionDialog(dialog_viewmodel, self)
            dialog.exec()
            
    def _load_items(self):
        search_term = self.search_input.text()
        self.viewmodel.load_regions(search_term=search_term)

    def _show_error_message(self, message):
        QMessageBox.critical(self, "錯誤", message)
