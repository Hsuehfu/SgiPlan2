from PySide6.QtWidgets import QTableWidgetItem, QMessageBox
from views.base_list_widget import BaseListWidget
from views.position_dialog import PositionDialog # Will create this next
from viewmodels.position_list_viewmodel import PositionListViewModel
from viewmodels.position_dialog_viewmodel import PositionDialogViewModel # Will use this

class PositionListWidget(BaseListWidget):
    def __init__(self, viewmodel: PositionListViewModel, parent=None):
        super().__init__(viewmodel, parent)
        self.viewmodel = viewmodel
        self.viewmodel.positions_loaded.connect(self.display_items)
        self.viewmodel.operation_successful.connect(self._load_items)
        self.viewmodel.error_occurred.connect(self._show_error_message)
        self._load_items() # Initial load

    def _get_window_title(self):
        return "職務管理"

    def _get_search_placeholder(self):
        return "搜尋職務名稱"

    def _get_table_headers(self):
        return ["ID", "職務名稱"]

    def _display_item_row(self, row, position):
        self.table_widget.setItem(row, 0, QTableWidgetItem(str(position.id)))
        self.table_widget.setItem(row, 1, QTableWidgetItem(position.name))

    def _get_item_name(self, position):
        return position.name

    def _perform_delete(self, position_id):
        self.viewmodel.delete_position(position_id)

    def _get_dialog_viewmodel_class(self):
        return PositionDialogViewModel

    def _get_dialog_class(self):
        return PositionDialog
    
    def _load_items(self):
        search_term = self.search_input.text()
        self.viewmodel.load_positions(search_term=search_term)

    def _filter_changed(self):
        self._load_items()

    def _sort_items(self, column_index):
        order = self.table_widget.horizontalHeader().sortIndicatorOrder()
        self.viewmodel.sort_positions(column_index, order)

    def _show_error_message(self, message):
        QMessageBox.critical(self, "錯誤", message)
