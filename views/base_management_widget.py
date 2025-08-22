from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, 
    QLineEdit, QPushButton, QStyle
)
from PySide6.QtGui import QIcon

class BaseManagementWidget(QWidget):
    """
    一個更通用的基底類別，提供管理介面的共通 UI 元素，
    例如標題、搜尋框和標準 CRUD 按鈕。
    子類別需要自行建立並加入主要的資料顯示元件（如 QTableWidget 或 QTreeWidget）。
    """
    def __init__(self, viewmodel, parent=None):
        super().__init__(parent)
        self.viewmodel = viewmodel
        self.items = []

    def _init_base_ui(self):
        """建立共通的 UI 介面。"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(10)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.setWindowTitle(self._get_window_title())

        self.title_label = QLabel(self._get_window_title())
        self.title_label.setObjectName("titleLabel")

        # 搜尋與過濾
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(20)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(self._get_search_placeholder())
        filter_layout.addWidget(QLabel("搜尋:"))
        filter_layout.addWidget(self.search_input)
        
        style = self.style()
        self.clear_search_button = QPushButton(QIcon.fromTheme("edit-clear", style.standardIcon(QStyle.SP_DialogCloseButton)), "清除")
        filter_layout.addWidget(self.clear_search_button)
        
        # 允許子類別添加特定的過濾器
        self._add_specific_filters(filter_layout)
        filter_layout.addStretch()

        # 按鈕
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        self.add_button = QPushButton(QIcon.fromTheme("list-add", style.standardIcon(QStyle.SP_FileIcon)), " 新增")
        self.edit_button = QPushButton(QIcon.fromTheme("document-edit", style.standardIcon(QStyle.SP_FileIcon)), " 編輯")
        self.delete_button = QPushButton(QIcon.fromTheme("list-remove", style.standardIcon(QStyle.SP_FileIcon)), " 刪除")
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()

        self.main_layout.addWidget(self.title_label)
        self.main_layout.addLayout(filter_layout)
        self.main_layout.addLayout(button_layout)

    # 子類別需要實作的抽象方法
    def _get_window_title(self): raise NotImplementedError
    def _get_search_placeholder(self): raise NotImplementedError
    def _add_specific_filters(self, layout): pass # 可選
    def _clear_search(self): self.search_input.clear()