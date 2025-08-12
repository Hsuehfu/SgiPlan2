from PySide6.QtCore import QSettings
from PySide6.QtGui import QAction
from PySide6.QtCore import QSettings
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
from views.region_list_widget import RegionListWidget
from viewmodels.region_list_viewmodel import RegionListViewModel


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
        self.member_list_viewmodel = MemberListViewModel()
        self.member_list_widget = MemberListWidget(self.member_list_viewmodel)
        self.member_list_viewmodel.members_loaded.connect(self.member_list_widget.display_members)
        self.member_list_viewmodel.load_members()
        self.tab_widget.addTab(self.member_list_widget, "會員列表")

        # Create Region List Tab
        self.region_list_viewmodel = RegionListViewModel()
        self.region_list_widget = RegionListWidget(self.region_list_viewmodel)
        self.region_list_viewmodel.regions_loaded.connect(self.region_list_widget.display_regions)
        self.region_list_viewmodel.load_regions()
        self.tab_widget.addTab(self.region_list_widget, "地區管理")

        # Create a second placeholder tab
        self.placeholder_tab = QWidget()
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

        # Help Menu
        help_menu = menu_bar.addMenu("說明")
        about_action = QAction("關於", self)
        # You can connect this to a function that shows an about dialog
        # about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

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
        """)
