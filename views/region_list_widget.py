from PySide6.QtWidgets import QTableWidgetItem
from views.base_list_widget import BaseListWidget
from views.region_dialog import RegionDialog
from viewmodels.region_dialog_viewmodel import RegionDialogViewModel

class RegionListWidget(BaseListWidget):
    def __init__(self, viewmodel, parent=None):
        super().__init__(viewmodel, parent)

    def _get_window_title(self):
        return "地區管理"

    def _get_search_placeholder(self):
        return "搜尋地區名稱..."

    def _get_table_headers(self):
        return ["地區名稱"]

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
        self.table_widget.setItem(row, 0, QTableWidgetItem(region.name))

    def _get_item_name(self, region):
        return region.name

    def _perform_delete(self, region_id):
        self.viewmodel.delete_region(region_id)

    def _get_dialog_viewmodel_class(self):
        return RegionDialogViewModel

    def _get_dialog_class(self):
        return RegionDialog

    def _perform_add(self, region_data):
        dialog_viewmodel = RegionDialogViewModel()
        dialog_viewmodel.add_region(region_data)

    def _perform_update(self, region_id, region_data):
        dialog_viewmodel = RegionDialogViewModel()
        dialog_viewmodel.update_region(region_id, region_data)

    def _load_items(self):
        search_term = self.search_input.text()
        self.viewmodel.load_regions(search_term=search_term)
