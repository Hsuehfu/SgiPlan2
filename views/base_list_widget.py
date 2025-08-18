from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QLabel, QPushButton, QHBoxLayout, QAbstractItemView, QLineEdit, QStyle, QMessageBox
from PySide6.QtGui import QIcon

class BaseListWidget(QWidget):
    def __init__(self, viewmodel, parent=None):
        super().__init__(parent)
        self.viewmodel = viewmodel
        self.items = [] # This will hold the list of members or regions
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        self.setWindowTitle(self._get_window_title())

        self.title_label = QLabel(self._get_window_title())
        self.title_label.setObjectName("titleLabel")

        # Filter and Search Layout
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(20)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(self._get_search_placeholder())
        filter_layout.addWidget(QLabel("搜尋:"))
        filter_layout.addWidget(self.search_input)
        
        # Add clear button
        style = self.style()
        self.clear_search_button = QPushButton(QIcon.fromTheme("edit-clear", style.standardIcon(QStyle.SP_DialogCloseButton)), "清除")
        filter_layout.addWidget(self.clear_search_button)
        
        # Add specific filter widgets if needed by subclasses
        self._add_specific_filters(filter_layout)

        filter_layout.addStretch()

        self.table_widget = QTableWidget(self)
        self.table_widget.setColumnCount(len(self._get_table_headers()))
        self.table_widget.setHorizontalHeaderLabels(self._get_table_headers())
        self.table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.horizontalHeader().setStretchLastSection(True)
        self.table_widget.horizontalHeader().setSortIndicatorShown(True)
        self.table_widget.horizontalHeader().setSectionsClickable(True)
        self.table_widget.horizontalHeader().sectionClicked.connect(self._sort_items)
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        style = self.style()
        self.add_button = QPushButton(QIcon.fromTheme("list-add", style.standardIcon(QStyle.SP_FileIcon)), " 新增")
        self.edit_button = QPushButton(QIcon.fromTheme("document-edit", style.standardIcon(QStyle.SP_FileIcon)), " 編輯")
        self.delete_button = QPushButton(QIcon.fromTheme("list-remove", style.standardIcon(QStyle.SP_FileIcon)), " 刪除")
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()

        layout.addWidget(self.title_label)
        layout.addLayout(filter_layout)
        layout.addLayout(button_layout)
        layout.addWidget(self.table_widget)

        self.setLayout(layout)

        self.add_button.clicked.connect(self.open_add_dialog)
        self.edit_button.clicked.connect(self.open_edit_dialog)
        self.delete_button.clicked.connect(self._delete_selected_item)
        self.search_input.textChanged.connect(self._filter_changed)
        self.clear_search_button.clicked.connect(self._clear_search)

    # Abstract methods to be implemented by subclasses
    def _get_window_title(self):
        raise NotImplementedError

    def _get_search_placeholder(self):
        raise NotImplementedError

    def _get_table_headers(self):
        raise NotImplementedError

    def _add_specific_filters(self, layout):
        # Optional: Subclasses can override this to add more filter widgets
        pass

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
            
            reply = QMessageBox.question(self, '確認刪除', 
                                           f'是否確定要刪除 "{self._get_item_name(item_to_delete)}"?',
                                           QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                self._perform_delete(item_to_delete.id)

    def _get_item_name(self, item):
        raise NotImplementedError

    def _perform_delete(self, item_id):
        raise NotImplementedError

    def open_add_dialog(self):
        dialog_viewmodel = self._get_dialog_viewmodel_class()()
        dialog = self._get_dialog_class()(dialog_viewmodel, self)
        if dialog.exec():
            member_data = dialog.get_item_data()
            dialog_viewmodel.add_member(member_data)
            self._load_items() # Call generic load method

    def open_edit_dialog(self):
        selected_row = self.table_widget.currentRow()
        if selected_row >= 0:
            item_to_edit = self.items[selected_row]
            dialog_viewmodel = self._get_dialog_viewmodel_class()()
            dialog = self._get_dialog_class()(dialog_viewmodel, self)
            dialog.set_item_data(item_to_edit) # Use a generic method name
            if dialog.exec():
                member_data = dialog.get_item_data()
                dialog_viewmodel.update_member(item_to_edit.id, member_data)
                self._load_items() # Call generic load method

    def _get_dialog_viewmodel_class(self):
        raise NotImplementedError

    def _get_dialog_class(self):
        raise NotImplementedError    

    def _load_items(self):
        raise NotImplementedError

    def _clear_search(self):
        self.search_input.clear()