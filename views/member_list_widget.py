from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QPushButton, QHBoxLayout, QAbstractItemView, QLineEdit, QComboBox, QHeaderView, QStyle, QMessageBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from views.member_dialog import MemberDialog
from viewmodels.member_dialog_viewmodel import MemberDialogViewModel

class MemberListWidget(QWidget):
    def __init__(self, viewmodel, parent=None):
        super().__init__(parent)
        self.viewmodel = viewmodel
        self.members = []
        self.init_ui()
        self.viewmodel.regions_loaded.connect(self.populate_region_filter)
        self.viewmodel.load_regions()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        self.setWindowTitle("會員列表")

        self.title_label = QLabel("會員列表")
        self.title_label.setObjectName("titleLabel")

        # Filter and Search Layout
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜尋姓名...")
        self.region_filter_combo = QComboBox()
        filter_layout.addWidget(QLabel("搜尋:"))
        filter_layout.addWidget(self.search_input)
        filter_layout.addWidget(QLabel("地區過濾:"))
        filter_layout.addWidget(self.region_filter_combo)
        filter_layout.addStretch()

        self.table_widget = QTableWidget(self)
        self.table_widget.setColumnCount(2)
        self.table_widget.setHorizontalHeaderLabels(["姓名", "地區"])
        self.table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.horizontalHeader().setStretchLastSection(True)
        self.table_widget.horizontalHeader().setSortIndicatorShown(True)
        self.table_widget.horizontalHeader().setSectionsClickable(True)
        self.table_widget.horizontalHeader().sectionClicked.connect(self.sort_members)
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
        self.delete_button.clicked.connect(self.delete_selected_member)
        self.search_input.textChanged.connect(self.filter_changed)
        self.region_filter_combo.currentIndexChanged.connect(self.filter_changed)

    def populate_region_filter(self, regions):
        self.region_filter_combo.addItem("所有地區", -1)
        for region in regions:
            self.region_filter_combo.addItem(region.name, region.id)

    def filter_changed(self):
        search_term = self.search_input.text()
        region_id = self.region_filter_combo.currentData()
        self.viewmodel.load_members(search_term=search_term, region_id=region_id)

    def sort_members(self, column_index):
        order = self.table_widget.horizontalHeader().sortIndicatorOrder()
        self.viewmodel.sort_members(column_index, order)

    def display_members(self, members):
        self.members = members
        self.table_widget.setRowCount(len(members))
        for i, member in enumerate(members):
            self.table_widget.setItem(i, 0, QTableWidgetItem(member.name))
            self.table_widget.setItem(i, 1, QTableWidgetItem(member.region.name if member.region else ""))

    def delete_selected_member(self):
        selected_row = self.table_widget.currentRow()
        if selected_row >= 0:
            member_to_delete = self.members[selected_row]
            
            reply = QMessageBox.question(self, '確認刪除', 
                                           f'是否確定要刪除會員 "{member_to_delete.name}"?',
                                           QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                self.viewmodel.delete_member(member_to_delete.id)

    def open_add_dialog(self):
        dialog_viewmodel = MemberDialogViewModel()
        dialog = MemberDialog(dialog_viewmodel, self)
        if dialog.exec():
            member_data = dialog.get_member_data()
            dialog_viewmodel.add_member(member_data)
            self.viewmodel.load_members()

    def open_edit_dialog(self):
        selected_row = self.table_widget.currentRow()
        if selected_row >= 0:
            member_to_edit = self.members[selected_row]
            dialog_viewmodel = MemberDialogViewModel()
            dialog = MemberDialog(dialog_viewmodel, self)
            dialog.set_member_data(member_to_edit)
            if dialog.exec():
                member_data = dialog.get_member_data()
                dialog_viewmodel.update_member(member_to_edit.id, member_data)
                self.viewmodel.load_members()
