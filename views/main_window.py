import logging
from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QMainWindow,
    QListView,
    QVBoxLayout,
    QWidget,
    QTabWidget,
)

from views.member_list_widget import MemberListWidget
from viewmodels.member_list_viewmodel import MemberListViewModel
from .region_list_widget import RegionListWidget
from viewmodels.region_list_viewmodel import RegionListViewModel
from .position_list_widget import PositionListWidget
from viewmodels.position_list_viewmodel import PositionListViewModel

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    def __init__(self, viewmodel):
        super().__init__()
        self.setWindowTitle("SGI企劃管理系統")
        self.viewmodel = viewmodel

        self._load_settings()
        self.apply_stylesheet()

        # Create Tab Widget as the central widget
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.tab_widget.removeTab)

        # Create the first tab, which contains the original list view
        self.item_list_tab = QWidget()
        self.item_list_layout = QVBoxLayout(self.item_list_tab)
        self.item_list_view = QListView()
        self.item_list_layout.addWidget(self.item_list_view)
        self.tab_widget.addTab(self.item_list_tab, "項目列表")

        # Create Member List Tab
        self.member_list_viewmodel = MemberListViewModel(self.viewmodel.session) # Pass db_session
        self.member_list_widget = MemberListWidget(self.member_list_viewmodel)
        self.tab_widget.addTab(self.member_list_widget, "會員列表")
        self.tab_widget.setCurrentWidget(self.member_list_widget)
        self.member_list_widget._load_items() # Initial load of members after connection

        # Create a second placeholder tab
        self.placeholder_tab = QWidget() # Define the placeholder tab
        self.tab_widget.addTab(self.placeholder_tab, "分頁二")

        # Bind the view to the viewmodel
        self.item_list_view.setModel(self.viewmodel.items)

        # Create the menu bar
        self._create_menu_bar()

        # Create Status Bar
        self.statusBar().showMessage("準備就緒")

    def _load_settings(self):
        self.settings = QSettings("SgiPlan", "SgiPlan2")
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)

    def closeEvent(self, event):
        self.settings.setValue("geometry", self.saveGeometry())
        super().closeEvent(event)

    def _create_menu_bar(self):
        menu_bar = self.menuBar()

        # File Menu
        file_menu = menu_bar.addMenu("檔案")
        exit_action = QAction("離開", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Basic Data Menu
        basic_data_menu = menu_bar.addMenu("基本資料")
        region_management_action = QAction("地區管理", self)
        region_management_action.triggered.connect(self._open_region_management_tab)
        basic_data_menu.addAction(region_management_action)

        position_management_action = QAction("職務管理", self)
        position_management_action.triggered.connect(self._open_position_management_tab)
        basic_data_menu.addAction(position_management_action)

        # Help Menu
        help_menu = menu_bar.addMenu("說明")
        about_action = QAction("關於", self)
        # You can connect this to a function that shows an about dialog
        # about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    def _open_region_management_tab(self):
        # [修改] 直接呼叫通用方法
        self._open_management_tab(RegionListWidget, RegionListViewModel, "地區管理")

    def _open_position_management_tab(self):
        # [修改] 直接呼叫通用方法
        self._open_management_tab(PositionListWidget, PositionListViewModel, "職務管理")
        
    # views/main_window.py

    # [新增] 一個通用的方法來開啟管理分頁
    def _open_management_tab(self, widget_class, viewmodel_class, tab_name):
        """
        一個通用的方法，用於開啟或切換到一個管理分頁。

        Args:
            widget_class: 要建立的 Widget 類別 (例如 MemberListWidget)。
            viewmodel_class: 要建立的 ViewModel 類別 (例如 MemberListViewModel)。
            tab_name: 分頁要顯示的名稱 (例如 "會員管理")。
        """
        # 檢查分頁是否已存在
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) == tab_name:
                self.tab_widget.setCurrentIndex(i)
                return

        # 如果不存在，則建立新的分頁
        # 將共享的 session 傳遞給新的 ViewModel
        viewmodel = viewmodel_class(self.viewmodel.session)
        widget = widget_class(viewmodel)

        # 將 ViewModel 和 Widget 暫時儲存在 Widget 自己身上，方便管理
        widget.setProperty("viewmodel", viewmodel)

        # 連接訊號-槽來更新畫面
        # 假設所有 ListViewModel 都有一個 items_loaded 訊號
        if hasattr(viewmodel, "items_loaded"):
            viewmodel.items_loaded.connect(widget.display_items, Qt.QueuedConnection)
        else:
            logger.warning(f"ViewModel {viewmodel_class.__name__} does not have an 'items_loaded' signal.")            
        
        # 觸發初始資料載入
        if hasattr(widget, "_load_items"):
            widget._load_items()

        index = self.tab_widget.addTab(widget, tab_name)
        self.tab_widget.setCurrentIndex(index)            

    def apply_stylesheet(self):
        self.setStyleSheet("""
            QWidget {
                font-size: 14px;
            }
            #titleLabel {
                font-size: 24px;
                font-weight: bold;
            }
            QTableWidget {
                border: 1px solid #cccccc;
                gridline-color: #e0e0e0;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 4px;
                border: 1px solid #cccccc;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                text-align: center;
                text-decoration: none;
                font-size: 14px;
                margin: 4px 2px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLineEdit, QComboBox {
                padding: 5px;
                border: 1px solid #cccccc;
                border-radius: 4px;
            }
            #clearSearchButton {
                background-color: #D9B300;
            }
            #deleteButton {
                background-color: #dd6666;
            }                              
        """)
