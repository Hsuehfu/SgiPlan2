from PySide6.QtWidgets import (
    QMessageBox, QTreeWidget, QTreeWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt
from .base_management_widget import BaseManagementWidget
from views.region_dialog import RegionDialog
from viewmodels.region_dialog_viewmodel import RegionDialogViewModel

class RegionListWidget(BaseManagementWidget):
    def __init__(self, viewmodel, parent=None):
        super().__init__(viewmodel, parent)
        self.init_ui()

        self.viewmodel.items_loaded.connect(self.display_items)
        self.viewmodel.error_occurred.connect(self._show_error_message)

    def init_ui(self):
        """建立樹狀檢視的 UI 介面。"""
        super()._init_base_ui() # 初始化共通 UI

        # 樹狀檢視
        self.tree_widget = QTreeWidget(self)
        self.tree_widget.setColumnCount(len(self._get_table_headers()))
        self.tree_widget.setHeaderLabels(self._get_table_headers())
        self.tree_widget.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tree_widget.setAlternatingRowColors(True)
        self.tree_widget.setSelectionBehavior(QTreeWidget.SelectRows)

        self.main_layout.addWidget(self.tree_widget)

        # 連接訊號
        self.add_button.clicked.connect(self.open_add_dialog)
        self.edit_button.clicked.connect(self.open_edit_dialog)
        self.delete_button.clicked.connect(self._delete_selected_item)
        self.search_input.textChanged.connect(self._filter_changed)
        self.clear_search_button.clicked.connect(self._clear_search)

    def _get_window_title(self):
        return "地區管理"

    def _get_search_placeholder(self):
        return "搜尋地區名稱..."

    def _get_table_headers(self):
        return ["地區名稱", "ID"]

    def _filter_changed(self):
        """在客戶端過濾樹狀檢視。"""
        search_text = self.search_input.text().lower()
        for i in range(self.tree_widget.topLevelItemCount()):
            self._apply_filter_recursive(self.tree_widget.topLevelItem(i), search_text)

    def _apply_filter_recursive(self, item, search_text):
        """遞迴地檢查一個項目及其所有子項目是否符合搜尋文字。
        如果項目本身或其任何子孫符合，則該項目可見。
        """
        item_text = item.text(0).lower()
        self_match = search_text in item_text

        child_match = False
        for i in range(item.childCount()):
            if self._apply_filter_recursive(item.child(i), search_text):
                child_match = True

        is_visible = self_match or child_match
        item.setHidden(not is_visible)
        return is_visible

    def _sort_items(self, column_index):
        # 樹狀結構的排序較複雜，暫不實作
        pass

    def display_items(self, items):
        """將扁平的地區列表建立為樹狀結構並顯示。"""
        self.items = items
        self.tree_widget.clear()

        region_items = {}  # 映射: region.id -> QTreeWidgetItem
        root_items = []

        # 第一輪：建立所有 QTreeWidgetItem
        for region in items:
            tree_item = QTreeWidgetItem([region.name, str(region.id)])
            tree_item.setData(0, Qt.UserRole, region)  # 將 region 物件儲存在項目中
            region_items[region.id] = tree_item

        # 第二輪：建立父子關係
        for region in items:
            if region.parent_id and region.parent_id in region_items:
                parent_item = region_items[region.parent_id]
                parent_item.addChild(region_items[region.id])
            else:
                root_items.append(region_items[region.id])

        self.tree_widget.addTopLevelItems(root_items)
        self.tree_widget.expandAll()
        self.tree_widget.resizeColumnToContents(0)

    def _get_delete_confirmation_text(self, item) -> str:
        """取得刪除地區時的確認訊息文字。"""
        return f'是否確定要刪除地區 "{self._get_item_name(item)}"?\n\n注意：只有當地區底下沒有子地區時才能刪除。'

    def _delete_selected_item(self):
        selected_item = self.tree_widget.currentItem()
        if selected_item:
            region_to_delete = selected_item.data(0, Qt.UserRole)
            confirmation_text = self._get_delete_confirmation_text(region_to_delete)
            reply = QMessageBox.question(self, '確認刪除',
                                           confirmation_text,
                                           QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self._perform_delete(region_to_delete.id)

    def _get_item_name(self, region):
        return region.name

    def _perform_delete(self, region_id):
        self.viewmodel.delete_region(region_id)

    def open_add_dialog(self):
        """處理新增地區的操作。"""
        selected_parent_id = None
        selected_item = self.tree_widget.currentItem()
        if selected_item:
            region_data = selected_item.data(0, Qt.UserRole)
            selected_parent_id = region_data.id

        dialog_viewmodel = RegionDialogViewModel(db_session=self.viewmodel.session, initial_parent_id=selected_parent_id)
        dialog_viewmodel.saved_successfully.connect(self._load_items)
        dialog = RegionDialog(dialog_viewmodel, self)
        dialog.exec()

    def open_edit_dialog(self):
        """處理編輯地區的操作。"""
        selected_item = self.tree_widget.currentItem()
        if selected_item:
            region_to_edit = selected_item.data(0, Qt.UserRole)
            dialog_viewmodel = RegionDialogViewModel(
                db_session=self.viewmodel.session, 
                region_data=region_to_edit
            )
            dialog_viewmodel.saved_successfully.connect(self._load_items)
            dialog = RegionDialog(dialog_viewmodel, self)
            dialog.exec()
            
    def _load_items(self):
        # 為了建立完整的樹，我們總是載入所有地區
        # 過濾操作在客戶端完成
        self.viewmodel.load_regions()

    def _show_error_message(self, message):
        QMessageBox.critical(self, "錯誤", message)
