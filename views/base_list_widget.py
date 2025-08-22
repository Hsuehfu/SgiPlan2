from PySide6.QtWidgets import QTableWidget, QAbstractItemView, QMessageBox
from .base_management_widget import BaseManagementWidget

class BaseListWidget(BaseManagementWidget):
    def __init__(self, viewmodel, parent=None):
        super().__init__(viewmodel, parent)
        self.init_ui()
 
    def init_ui(self):
        super()._init_base_ui() # 初始化共通 UI

        self.table_widget = QTableWidget(self)
        self.table_widget.setColumnCount(len(self._get_table_headers()))
        self.table_widget.setHorizontalHeaderLabels(self._get_table_headers())
        self.table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.horizontalHeader().setStretchLastSection(True)
        self.table_widget.horizontalHeader().setSortIndicatorShown(True)
        self.table_widget.horizontalHeader().setSectionsClickable(True)
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.main_layout.addWidget(self.table_widget)

        self.add_button.clicked.connect(self.open_add_dialog)
        self.edit_button.clicked.connect(self.open_edit_dialog)
        self.delete_button.clicked.connect(self._delete_selected_item)
        self.search_input.textChanged.connect(self._filter_changed)
        self.clear_search_button.clicked.connect(self._clear_search)
        self.table_widget.horizontalHeader().sectionClicked.connect(self._sort_items)

    # Abstract methods to be implemented by subclasses
    def _get_window_title(self):
        raise NotImplementedError

    def _get_search_placeholder(self):
        raise NotImplementedError

    def _get_table_headers(self):
        raise NotImplementedError

    def _filter_changed(self):
        raise NotImplementedError

    def _sort_items(self, column_index):
        raise NotImplementedError

    def display_items(self, items):
        self.items = items
        self.table_widget.setRowCount(len(items))
        for i, item in enumerate(items):
            self._display_item_row(i, item)

    def _display_item_row(self, row, item):
        raise NotImplementedError

    def _delete_selected_item(self):
        selected_row = self.table_widget.currentRow()
        if selected_row >= 0:
            item_to_delete = self.items[selected_row]
            confirmation_text = self._get_delete_confirmation_text(item_to_delete)
            reply = QMessageBox.question(self, '確認刪除',
                                           confirmation_text,
                                           QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                self._perform_delete(item_to_delete.id)

    def _get_delete_confirmation_text(self, item) -> str:
        """
        取得刪除項目時的確認訊息文字。
        子類別可以覆寫此方法以提供更具體的訊息。
        """
        return f'是否確定要刪除 "{self._get_item_name(item)}"?'

    def _get_item_name(self, item):
        raise NotImplementedError

    def _perform_delete(self, item_id):
        raise NotImplementedError

    def open_add_dialog(self):
        raise NotImplementedError

    def open_edit_dialog(self):
        raise NotImplementedError

    def _get_dialog_viewmodel_class(self):
        raise NotImplementedError

    def _get_dialog_class(self):
        raise NotImplementedError    

    def _load_items(self): raise NotImplementedError