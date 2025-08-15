import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QTabWidget,
    QTableWidget, QTableWidgetItem, QLineEdit, QFormLayout
)
from PySide6.QtCore import Qt

class MainWindow(QMainWindow):
    """主視窗類別，使用 QTabWidget 作為中央元件"""

    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("智慧排班管理系統 (分頁版)")
        self.setGeometry(200, 200, 800, 600)
        
        # 建立主選單 (程式碼與前一版本相同，此處省略以保持簡潔)
        # 您可以將上一版本 _create_menu_bar 的程式碼貼到這裡
        # self._create_menu_bar() 
        
        # 1. 建立 QTabWidget 作為中央元件
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # 2. 建立各個分頁的內容
        self.create_dashboard_tab()
        self.create_employee_tab()
        self.create_shift_tab()

    def create_dashboard_tab(self):
        """建立儀表板分頁"""
        # 建立此分頁的主容器
        dashboard_page = QWidget()
        
        # 設定此分頁的佈局
        layout = QVBoxLayout(dashboard_page)
        
        # 在分頁中加入內容
        welcome_label = QLabel("系統儀表板")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        
        summary_label = QLabel("目前員工總數: 10\n已定義班別數: 3\n本月排班狀態: 未完成")
        summary_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        summary_label.setStyleSheet("font-size: 16px;")

        layout.addWidget(welcome_label)
        layout.addWidget(summary_label)
        
        # 將建立好的分頁加入到 TabWidget 中
        self.tab_widget.addTab(dashboard_page, "儀表板")

    def create_employee_tab(self):
        """建立員工資料管理分頁"""
        employee_page = QWidget()
        layout = QVBoxLayout(employee_page)

        # 建立一個表格元件 QTableWidget
        table = QTableWidget(4, 3) # 4 列, 3 欄
        table.setHorizontalHeaderLabels(["員工編號", "姓名", "職位"])

        # 填充一些假資料
        data = [
            ["EMP001", "王大明", "資深工程師"],
            ["EMP002", "陳小美", "專案經理"],
            ["EMP003", "李四", "實習生"],
            ["EMP004", "趙五", "設計師"]
        ]

        for row, row_data in enumerate(data):
            for col, item in enumerate(row_data):
                table.setItem(row, col, QTableWidgetItem(item))
        
        # 讓表格寬度自動填滿
        table.horizontalHeader().setStretchLastSection(True)

        layout.addWidget(table)
        self.tab_widget.addTab(employee_page, "員工資料管理")

    def create_shift_tab(self):
        """建立班別設定分頁"""
        shift_page = QWidget()
        
        # 使用 QFormLayout 可以方便地建立標籤+輸入框的表單
        layout = QFormLayout(shift_page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        layout.addRow(QLabel("<h3>新增/編輯班別</h3>")) # 簡單的 HTML 標籤
        layout.addRow("班別名稱:", QLineEdit())
        layout.addRow("開始時間:", QLineEdit("HH:MM"))
        layout.addRow("結束時間:", QLineEdit("HH:MM"))
        layout.addRow("備註:", QLineEdit())

        self.tab_widget.addTab(shift_page, "班別設定")

    # (此處省略 _create_menu_bar 和其他函式，您可以從前一版本複製過來)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())