import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout
)
from PySide6.QtGui import QAction, QIcon  # QIcon 是用來加圖示的，可以先備著
from PySide6.QtCore import Qt

class MainWindow(QMainWindow):
    """主視窗類別，繼承自 QMainWindow"""

    def __init__(self):
        super().__init__()
        
        # 1. 主視窗基本設定
        self.setWindowTitle("智慧排班管理系統")
        self.setGeometry(200, 200, 800, 600)  # (x, y, width, height)

        # 2. 建立主選單
        self._create_menu_bar()

        # 3. 建立狀態列 (視窗最下方的小長條)
        self.statusBar().showMessage("系統準備就緒")

        # 4. 建立中心元件 (未來顯示主要內容的地方)
        # 這裡先用一個簡單的標籤當作示意
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        welcome_label = QLabel("歡迎使用智慧排班系統！請從上方選單開始操作。")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setStyleSheet("font-size: 20px;")
        layout.addWidget(welcome_label)


    def _create_menu_bar(self):
        """建立主選單列"""
        menu_bar = self.menuBar()

        # --- 檔案管理選單 ---
        file_menu = menu_bar.addMenu("&檔案管理") # '&' 符號可以讓使用者用 Alt+F 開啟

        # 建立選項 (Action)
        import_action = QAction("從 Excel 匯入...", self)
        import_action.setStatusTip("從 Excel 檔案匯入員工與班別資料")
        import_action.triggered.connect(self.import_from_excel)

        save_action = QAction("儲存排班專案...", self)
        save_action.setStatusTip("將目前的排班狀態儲存成專案檔")
        save_action.triggered.connect(self.save_project)

        export_action = QAction("匯出排班結果為 Excel...", self)
        export_action.setStatusTip("將目前的排班結果匯出成 Excel 檔案")
        export_action.triggered.connect(self.export_to_excel)

        exit_action = QAction("離開", self)
        exit_action.setStatusTip("關閉應用程式")
        exit_action.triggered.connect(self.close) # close 是 QMainWindow 內建的關閉函式

        # 將選項加入選單
        file_menu.addAction(import_action)
        file_menu.addAction(save_action)
        file_menu.addSeparator() # 加入分隔線
        file_menu.addAction(export_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        # --- 資料管理選單 ---
        data_menu = menu_bar.addMenu("&資料管理")

        employee_action = QAction("員工資料管理", self)
        employee_action.triggered.connect(self.manage_employees)
        data_menu.addAction(employee_action)

        shift_action = QAction("班別設定", self)
        shift_action.triggered.connect(self.manage_shifts)
        data_menu.addAction(shift_action)
        
        rules_action = QAction("排班規則設定", self)
        rules_action.triggered.connect(self.manage_rules)
        data_menu.addAction(rules_action)


        # --- 排班作業選單 ---
        scheduling_menu = menu_bar.addMenu("&排班作業")

        run_scheduler_action = QAction("執行自動排班", self)
        run_scheduler_action.triggered.connect(self.run_scheduler)
        scheduling_menu.addAction(run_scheduler_action)

        manual_adjust_action = QAction("進入手動微調模式", self)
        manual_adjust_action.triggered.connect(self.manual_adjust)
        scheduling_menu.addAction(manual_adjust_action)


        # --- 說明選單 ---
        help_menu = menu_bar.addMenu("&說明")

        about_action = QAction("關於本程式", self)
        about_action.triggered.connect(self.about_dialog)
        help_menu.addAction(about_action)

    # --- 以下是選單選項觸發後要執行的函式 (目前僅為示意) ---
    # --- 未來您需要將實際功能寫在這些函式裡面 ---

    def import_from_excel(self):
        self.statusBar().showMessage("觸發功能：從 Excel 匯入...", 3000) # 訊息顯示 3 秒
        print("準備開啟檔案對話框以匯入 Excel...")
        # 在這裡加入開啟檔案對話框、讀取 pandas 的邏輯

    def save_project(self):
        self.statusBar().showMessage("觸發功能：儲存專案...", 3000)
        print("儲存專案...")

    def export_to_excel(self):
        self.statusBar().showMessage("觸發功能：匯出為 Excel...", 3000)
        print("準備開啟另存新檔對話框以匯出 Excel...")
        # 在這裡加入 pandas 寫入 Excel 的邏輯

    def manage_employees(self):
        self.statusBar().showMessage("開啟員工資料管理視窗...", 3000)
        print("開啟員工資料管理...")
        # 在這裡可以建立一個新的對話框(QDialog)或切換中央元件來顯示員工資料表

    def manage_shifts(self):
        self.statusBar().showMessage("開啟班別設定視窗...", 3000)
        print("開啟班別設定...")

    def manage_rules(self):
        self.statusBar().showMessage("開啟排班規則設定視窗...", 3000)
        print("開啟排班規則設定...")

    def run_scheduler(self):
        self.statusBar().showMessage("正在執行自動排班，請稍候...", 5000)
        print("執行排班演算法...")
        # 這裡會是您系統的核心，呼叫排班演算法
        self.statusBar().showMessage("排班完成！", 3000)

    def manual_adjust(self):
        self.statusBar().showMessage("進入手動微調模式...", 3000)
        print("切換到手動微調介面...")
        # 在這裡可以將中央元件切換成一個可以拖拉、修改的排班表介面

    def about_dialog(self):
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.about(
            self,
            "關於智慧排班管理系統",
            "<p>這是一個使用 Python 與 PySide6 開發的排班系統。</p>"
            "<p>版本: 1.0.0</p>"
            "<p>時間: 2025</p>"
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())