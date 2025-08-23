from PySide6.QtWidgets import QTableWidgetItem, QLabel, QComboBox
from PySide6.QtGui import QBrush, QColor
from views.base_list_widget import BaseListWidget
from views.member_dialog import MemberDialog
from viewmodels.member_dialog_viewmodel import MemberDialogViewModel

class MemberListWidget(BaseListWidget):
    def __init__(self, viewmodel, parent=None):
        super().__init__(viewmodel, parent)
        self.viewmodel.items_loaded.connect(self.display_items)
        self.viewmodel.regions_loaded.connect(self.populate_region_filter)
        self.viewmodel.members_count_changed.connect(self._update_member_count) # Connect new signal
        self._member_count = 0 # Initialize count
        self.viewmodel.load_regions() # This is still needed to populate the filter

    def _get_window_title(self):
        return "會員管理"

    def _get_search_placeholder(self):
        return "搜尋姓名..."

    def _get_table_headers(self):
        return ["姓名", "電話", "是否可排班", "地區"]

    def _get_status_bar_message(self):
        return f"會員資料數: {self._member_count} 筆"

    def _update_member_count(self, count):
        self._member_count = count
        # Trigger status bar update if this tab is currently active
        # This will be handled by MainWindow's _on_tab_changed

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
        self.table_widget.setItem(row, 1, QTableWidgetItem(member.phone_number))
        
        is_schedulable_text = "是" if member.is_schedulable == 1 else "否"
        is_schedulable_item = QTableWidgetItem(is_schedulable_text)
        if member.is_schedulable == 0:
            is_schedulable_item.setForeground(QBrush(QColor("red")))
        self.table_widget.setItem(row, 2, is_schedulable_item)

        self.table_widget.setItem(row, 3, QTableWidgetItem(member.region.name if member.region else ""))

    def _get_item_name(self, member):
        return member.name

    def _perform_delete(self, member_id):
        self.viewmodel.delete_member(member_id)

    def _get_dialog_viewmodel_class(self):
        return MemberDialogViewModel

    def _get_dialog_class(self):
        return MemberDialog

    def open_add_dialog(self):
        """處理新增項目的操作。"""
        # 使用共享的 session 建立 ViewModel
        dialog_viewmodel = MemberDialogViewModel(db_session=self.viewmodel.session)
        dialog_viewmodel.saved_successfully.connect(self._load_items) # 連接訊號
        
        dialog = MemberDialog(dialog_viewmodel, self)
        dialog.load_initial_data()
        dialog.exec() # 執行對話框，不需要檢查返回值，因為訊號會處理更新

    def open_edit_dialog(self):
        """處理編輯項目的操作。"""
        selected_row = self.table_widget.currentRow()
        if selected_row >= 0:
            member_to_edit = self.items[selected_row]
            # 使用共享的 session 和要編輯的 member 建立 ViewModel
            dialog_viewmodel = MemberDialogViewModel(db_session=self.viewmodel.session, member_data=member_to_edit)
            dialog_viewmodel.saved_successfully.connect(self._load_items) # 連接訊號
            
            dialog = self._get_dialog_class()(dialog_viewmodel, self)
            dialog.load_initial_data()
            dialog.exec() # 執行對話框，不需要檢查返回值，因為訊號會處理更新

    def _load_items(self):
        search_term = self.search_input.text()
        region_id = self.region_filter_combo.currentData()
        self.viewmodel.load_members(search_term=search_term, region_id=region_id)
