from PySide6.QtWidgets import QTableWidgetItem, QLabel, QComboBox
from PySide6.QtCore import Qt
from views.base_list_widget import BaseListWidget
from views.member_dialog import MemberDialog
from viewmodels.member_dialog_viewmodel import MemberDialogViewModel

class MemberListWidget(BaseListWidget):
    def __init__(self, viewmodel, parent=None):
        super().__init__(viewmodel, parent)
        self.viewmodel.regions_loaded.connect(self.populate_region_filter)
        self.viewmodel.load_regions() # This is still needed to populate the filter

    def _get_window_title(self):
        return "會員管理"

    def _get_search_placeholder(self):
        return "搜尋姓名..."

    def _get_table_headers(self):
        return ["姓名", "地區"]

    def _add_specific_filters(self, layout):
        self.region_filter_combo = QComboBox()
        layout.addWidget(QLabel("地區過濾:"))
        layout.addWidget(self.region_filter_combo)
        self.region_filter_combo.currentIndexChanged.connect(self._filter_changed)

    def populate_region_filter(self, regions):
        self.region_filter_combo.addItem("所有地區", -1)
        for region in regions:
            self.region_filter_combo.addItem(region.name, region.id)

    def _filter_changed(self):
        self._load_items()

    def _sort_items(self, column_index):
        order = self.table_widget.horizontalHeader().sortIndicatorOrder()
        self.viewmodel.sort_members(column_index, order)

    def display_items(self, items):
        self.items = items
        self.table_widget.setRowCount(len(items))
        for i, item in enumerate(items):
            self._display_item_row(i, item)

    def _display_item_row(self, row, member):
        self.table_widget.setItem(row, 0, QTableWidgetItem(member.name))
        self.table_widget.setItem(row, 1, QTableWidgetItem(member.region.name if member.region else ""))

    def _get_item_name(self, member):
        return member.name

    def _perform_delete(self, member_id):
        self.viewmodel.delete_member(member_id)

    def _get_dialog_viewmodel_class(self):
        return MemberDialogViewModel

    def _get_dialog_class(self):
        return MemberDialog

    def _perform_add(self, member_data):
        dialog_viewmodel = MemberDialogViewModel()
        dialog_viewmodel.add_member(member_data)

    def _perform_update(self, member_id, member_data):
        dialog_viewmodel = MemberDialogViewModel()
        dialog_viewmodel.update_member(member_id, member_data)

    def _load_items(self):
        search_term = self.search_input.text()
        region_id = self.region_filter_combo.currentData()
        self.viewmodel.load_members(search_term=search_term, region_id=region_id)
