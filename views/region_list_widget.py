from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QPushButton, QHBoxLayout, QAbstractItemView, QLineEdit, QHeaderView, QStyle, QMessageBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from views.region_dialog import RegionDialog
from viewmodels.region_dialog_viewmodel import RegionDialogViewModel

class RegionListWidget(QWidget):
    def __init__(self, viewmodel, parent=None):
        super().__init__(parent)
        self.viewmodel = viewmodel
        self.regions = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        self.setWindowTitle("地區列表")

        self.title_label = QLabel("地區列表")
        self.title_label.setObjectName("titleLabel")

        # Filter and Search Layout
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜尋地區名稱...")
        filter_layout.addWidget(QLabel("搜尋:"))
        filter_layout.addWidget(self.search_input)
        filter_layout.addStretch()

        self.table_widget = QTableWidget(self)
        self.table_widget.setColumnCount(1)
        self.table_widget.setHorizontalHeaderLabels(["地區名稱"])
        self.table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.horizontalHeader().setStretchLastSection(True)
        self.table_widget.horizontalHeader().setSortIndicatorShown(True)
        self.table_widget.horizontalHeader().setSectionsClickable(True)
        self.table_widget.horizontalHeader().sectionClicked.connect(self.sort_regions)
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
        self.delete_button.clicked.connect(self.delete_selected_region)
        self.search_input.textChanged.connect(self.filter_changed)

    def filter_changed(self):
        search_term = self.search_input.text()
        self.viewmodel.load_regions(search_term=search_term)

    def sort_regions(self, column_index):
        order = self.table_widget.horizontalHeader().sortIndicatorOrder()
        self.viewmodel.sort_regions(column_index, order)

    def display_regions(self, regions):
        self.regions = regions
        self.table_widget.setRowCount(len(regions))
        for i, region in enumerate(regions):
            self.table_widget.setItem(i, 0, QTableWidgetItem(region.name))

    def delete_selected_region(self):
        selected_row = self.table_widget.currentRow()
        if selected_row >= 0:
            region_to_delete = self.regions[selected_row]
            
            reply = QMessageBox.question(self, '確認刪除', 
                                           f'是否確定要刪除地區 "{region_to_delete.name}"?',
                                           QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                self.viewmodel.delete_region(region_to_delete.id)

    def open_add_dialog(self):
        dialog_viewmodel = RegionDialogViewModel()
        dialog = RegionDialog(dialog_viewmodel, self)
        if dialog.exec():
            region_data = dialog.get_region_data()
            dialog_viewmodel.add_region(region_data)
            self.viewmodel.load_regions()

    def open_edit_dialog(self):
        selected_row = self.table_widget.currentRow()
        if selected_row >= 0:
            region_to_edit = self.regions[selected_row]
            dialog_viewmodel = RegionDialogViewModel()
            dialog = RegionDialog(dialog_viewmodel, self)
            dialog.set_region_data(region_to_edit)
            if dialog.exec():
                region_data = dialog.get_region_data()
                dialog_viewmodel.update_region(region_to_edit.id, region_data)
                self.viewmodel.load_regions()
