from PySide6.QtWidgets import (
    QMessageBox, QTreeWidget, QTreeWidgetItem, QHeaderView, QAbstractItemView, QMenu
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QDropEvent, QAction # Import QDropEvent and QAction
from views.base_management_widget import BaseManagementWidget # Changed base class
from views.position_dialog import PositionDialog
from viewmodels.position_dialog_viewmodel import PositionDialogViewModel
from viewmodels.position_list_viewmodel import PositionListViewModel

class PositionListWidget(BaseManagementWidget): # Changed base class
    def __init__(self, viewmodel: PositionListViewModel, parent=None):
        super().__init__(viewmodel, parent)
        self.init_ui() # Call init_ui here
        self.viewmodel.items_loaded.connect(self.display_items)
        self.viewmodel.error_occurred.connect(self._show_error_message)

    def init_ui(self):
        """建立樹狀檢視的 UI 介面。"""
        super()._init_base_ui() # Initialize common UI from BaseManagementWidget

        # 樹狀檢視
        self.tree_widget = QTreeWidget(self)
        self.tree_widget.setColumnCount(len(self._get_table_headers()))
        self.tree_widget.setHeaderLabels(self._get_table_headers())
        self.tree_widget.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tree_widget.setAlternatingRowColors(True)
        self.tree_widget.setSelectionBehavior(QTreeWidget.SelectRows)

        # 啟用拖放
        self.tree_widget.setDragEnabled(True)
        self.tree_widget.setDropIndicatorShown(True)
        self.tree_widget.setDragDropMode(QAbstractItemView.InternalMove)
        self.tree_widget.setDefaultDropAction(Qt.MoveAction)
        self.tree_widget.setDragDropOverwriteMode(False) # 插入，而不是覆蓋

        # 啟用上下文選單
        self.tree_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_widget.customContextMenuRequested.connect(self._show_context_menu)

        self.main_layout.addWidget(self.tree_widget)

        # 連接訊號 (from BaseListWidget, adapted for QTreeWidget)
        self.add_button.clicked.connect(self.open_add_dialog)
        self.edit_button.clicked.connect(self.open_edit_dialog)
        self.delete_button.clicked.connect(self._delete_selected_item)
        self.search_input.textChanged.connect(self._filter_changed)
        self.clear_search_button.clicked.connect(self._clear_search)
        # No sectionClicked for QTreeWidget header, sorting is more complex
        # self.tree_widget.horizontalHeader().sectionClicked.connect(self._sort_items)

    def _get_window_title(self):
        return "職務管理"

    def _get_search_placeholder(self):
        return "搜尋職務名稱..." # Added ellipsis for consistency

    def _get_table_headers(self):
        return ["職務名稱", "ID"] # Changed order and names for consistency with Region

    def _get_status_bar_message(self):
        return "職務列表已載入"

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
        """將扁平的職務列表建立為樹狀結構並顯示。"""
        self.items = items # Store the flat list of items
        self.tree_widget.clear()

        position_items = {}  # 映射: position.id -> QTreeWidgetItem
        root_items = []

        # 第一輪：建立所有 QTreeWidgetItem
        for position in items:
            tree_item = QTreeWidgetItem([position.name, str(position.id)])
            tree_item.setData(0, Qt.UserRole, position)  # 將 position 物件儲存在項目中
            position_items[position.id] = tree_item

        # 第二輪：建立父子關係
        for position in items:
            if position.parent_id and position.parent_id in position_items:
                parent_item = position_items[position.parent_id]
                parent_item.addChild(position_items[position.id])
            else:
                root_items.append(position_items[position.id])

        self.tree_widget.addTopLevelItems(root_items)
        self.tree_widget.expandAll()
        self.tree_widget.resizeColumnToContents(0)

    def _get_delete_confirmation_text(self, item) -> str:
        """取得刪除職務時的確認訊息文字。"""
        return f'是否確定要刪除職務 "{self._get_item_name(item)}"?\n\n注意：只有當職務底下沒有子職務時才能刪除。'

    def _delete_selected_item(self):
        selected_item = self.tree_widget.currentItem()
        if selected_item:
            position_to_delete = selected_item.data(0, Qt.UserRole)
            confirmation_text = self._get_delete_confirmation_text(position_to_delete)
            reply = QMessageBox.question(self, '確認刪除',
                                           confirmation_text,
                                           QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self._perform_delete(position_to_delete.id)

    def _get_item_name(self, position):
        return position.name

    def _perform_delete(self, position_id):
        self.viewmodel.delete_position(position_id)

    def _load_items(self):
        # 為了建立完整的樹，我們總是載入所有職務
        # 過濾操作在客戶端完成
        self.viewmodel.load_positions()

    def _show_error_message(self, message):
        QMessageBox.critical(self, "錯誤", message)

    def open_add_dialog(self):
        """處理新增職務的操作。"""
        selected_parent_id = None
        selected_item = self.tree_widget.currentItem()
        if selected_item:
            position_data = selected_item.data(0, Qt.UserRole)
            selected_parent_id = position_data.id

        dialog_viewmodel = PositionDialogViewModel(db_session=self.viewmodel.session, initial_parent_id=selected_parent_id)
        dialog_viewmodel.position_saved.connect(self._load_items)
        dialog = PositionDialog(dialog_viewmodel, self)
        dialog.exec()

    def open_edit_dialog(self):
        """處理編輯職務的操作。"""
        selected_item = self.tree_widget.currentItem()
        if selected_item:
            position_to_edit = selected_item.data(0, Qt.UserRole)
            dialog_viewmodel = PositionDialogViewModel(
                db_session=self.viewmodel.session, 
                position_data=position_to_edit
            )
            dialog_viewmodel.position_saved.connect(self._load_items)
            dialog = PositionDialog(dialog_viewmodel, self)
            dialog.exec()

    def dropEvent(self, event: QDropEvent):
        # 讓基礎 QTreeWidget 處理視覺移動
        super().dropEvent(event)

        # 在視覺移動後，更新底層資料模型
        self._update_position_hierarchy_in_viewmodel()
        event.acceptProposedAction()

    def _update_position_hierarchy_in_viewmodel(self):
        # 此方法將遍歷 QTreeWidget 並將更新後的層次結構發送到 ViewModel
        updated_hierarchy = []
        for i in range(self.tree_widget.topLevelItemCount()):
            self._traverse_tree_item(self.tree_widget.topLevelItem(i), None, updated_hierarchy)
        self.viewmodel.update_positions_hierarchy(updated_hierarchy)

    def _traverse_tree_item(self, item: QTreeWidgetItem, parent_id: int | None, hierarchy_list: list):
        position = item.data(0, Qt.UserRole)
        if position:
            # 計算 rank: 在其父級中的索引
            if item.parent():
                rank = item.parent().indexOfChild(item)
            else:
                rank = item.treeWidget().indexOfTopLevelItem(item)

            hierarchy_list.append({
                'id': position.id,
                'parent_id': parent_id,
                'rank': rank
            })
        for i in range(item.childCount()):
            self._traverse_tree_item(item.child(i), position.id if position else None, hierarchy_list)

    def _show_context_menu(self, position):
        menu = QMenu(self)

        add_action = QAction("新增", self)
        add_action.triggered.connect(self.open_add_dialog)
        menu.addAction(add_action)

        edit_action = QAction("修改", self)
        edit_action.triggered.connect(self.open_edit_dialog)
        menu.addAction(edit_action)

        selected_item = self.tree_widget.currentItem()
        if selected_item: # Only enable move actions if an item is selected
            menu.addSeparator() # Separator for move actions

            move_up_action = QAction("上移", self)
            move_up_action.triggered.connect(self._move_item_up)
            menu.addAction(move_up_action)

            move_down_action = QAction("下移", self)
            move_down_action.triggered.connect(self._move_item_down)
            menu.addAction(move_down_action)

        menu.exec(self.tree_widget.mapToGlobal(position))

    def _move_item_up(self):
        selected_item = self.tree_widget.currentItem()
        if not selected_item:
            return

        parent_item = selected_item.parent()
        if parent_item:
            index = parent_item.indexOfChild(selected_item)
            if index > 0:
                # Move visually
                item_to_move = parent_item.takeChild(index)
                parent_item.insertChild(index - 1, item_to_move)

                # Update ViewModel
                self._update_position_hierarchy_in_viewmodel()
        else: # Top-level item
            index = self.tree_widget.indexOfTopLevelItem(selected_item)
            if index > 0:
                # Move visually
                item_to_move = self.tree_widget.takeTopLevelItem(index)
                self.tree_widget.insertTopLevelItem(index - 1, item_to_move)

                # Update ViewModel
                self._update_position_hierarchy_in_viewmodel()

    def _move_item_down(self):
        selected_item = self.tree_widget.currentItem()
        if not selected_item:
            return

        parent_item = selected_item.parent()
        if parent_item:
            index = parent_item.indexOfChild(selected_item)
            if index < parent_item.childCount() - 1:
                # Move visually
                item_to_move = parent_item.takeChild(index)
                parent_item.insertChild(index + 1, item_to_move)

                # Update ViewModel
                self._update_position_hierarchy_in_viewmodel()
        else: # Top-level item
            index = self.tree_widget.indexOfTopLevelItem(selected_item)
            if index < self.tree_widget.topLevelItemCount() - 1:
                # Move visually
                item_to_move = self.tree_widget.takeTopLevelItem(index)
                self.tree_widget.insertTopLevelItem(index + 1, item_to_move)

                # Update ViewModel
                self._update_position_hierarchy_in_viewmodel()

