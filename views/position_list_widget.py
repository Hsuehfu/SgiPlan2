from PySide6.QtWidgets import QTableWidgetItem, QMessageBox
from views.base_list_widget import BaseListWidget
from views.position_dialog import PositionDialog
from viewmodels.position_dialog_viewmodel import PositionDialogViewModel
from viewmodels.position_list_viewmodel import PositionListViewModel

class PositionListWidget(BaseListWidget):
    def __init__(self, viewmodel: PositionListViewModel, parent=None):
        super().__init__(viewmodel, parent)
        self.viewmodel.positions_loaded.connect(self.display_items)
        self.viewmodel.error_occurred.connect(self._show_error_message)

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

    def open_add_dialog(self):
        """處理新增職務的操作。"""
        dialog_viewmodel = PositionDialogViewModel(db_session=self.viewmodel.session)
        dialog_viewmodel.position_saved.connect(self._load_items)
        
        dialog = PositionDialog(dialog_viewmodel, self)
        dialog.exec()

    def open_edit_dialog(self):
        """處理編輯職務的操作。"""
        selected_row = self.table_widget.currentRow()
        if selected_row >= 0:
            position_to_edit = self.items[selected_row]
            dialog_viewmodel = PositionDialogViewModel(
                db_session=self.viewmodel.session, 
                position_data=position_to_edit
            )
            dialog_viewmodel.position_saved.connect(self._load_items)
            
            dialog = PositionDialog(dialog_viewmodel, self)
            dialog.exec()
