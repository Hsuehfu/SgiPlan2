
from PySide6.QtCore import QSettings
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QMainWindow,
    QListView,
    QVBoxLayout,
    QWidget,
    QTabWidget,
)


class MainWindow(QMainWindow):
    def __init__(self, viewmodel):
        super().__init__()
        self.setWindowTitle("SGI企劃管理系統")
        self.viewmodel = viewmodel

        self._load_settings()

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
