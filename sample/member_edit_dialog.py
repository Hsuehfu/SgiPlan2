import sys
from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QLineEdit, QFormLayout, QGroupBox,
    QHBoxLayout, QComboBox, QPushButton, QTableWidget, QTableWidgetItem,
    QRadioButton, QButtonGroup, QDialogButtonBox, QHeaderView, QWidget, QMessageBox
)
from PySide6.QtCore import Qt

# --- 模擬從資料庫讀取的資料 ---
# 在您的真實應用中，這些資料應該從 DatabaseManager 類別獲取
ALL_POSITIONS = ["資深教練", "初階教練", "櫃台行政", "活動企劃", "社群小編"]
EXISTING_MEMBER_DATA = {
    "id": 2,
    "name": "陳美麗",
    "phone": "0922-456789",
    "positions": [
        {"name": "櫃台行政", "is_primary": True},
        {"name": "初階教練", "is_primary": False},
    ]
}
# --- 模擬結束 ---


class MemberEditDialog(QDialog):
    """
    一個用於新增或修改會員資料的對話方塊，
    特別包含了管理多個職位的功能。
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("編輯會員資料")
        self.setMinimumWidth(450)

        # --- 資料 ---
        # 用於儲存從外部載入的所有可選職位
        self.all_positions_list = []

        # --- UI 元件 ---
        self.name_edit = QLineEdit()
        self.phone_edit = QLineEdit()
        self.pos_combobox = QComboBox()
        self.add_pos_button = QPushButton("新增職位")
        self.positions_table = QTableWidget()
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        
        # 專門管理表格中的 RadioButton，確保單選
        self.primary_button_group = QButtonGroup()

        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        """初始化並佈局所有 UI 元件"""
        main_layout = QVBoxLayout(self)

        # -------------------- 基本資料區 --------------------
        form_layout = QFormLayout()
        form_layout.addRow("姓名:", self.name_edit)
        form_layout.addRow("電話:", self.phone_edit)
        main_layout.addLayout(form_layout)

        # -------------------- 職位管理區 --------------------
        pos_groupbox = QGroupBox("職位管理")
        pos_layout = QVBoxLayout()

        # 新增職位的水平佈局
        add_pos_layout = QHBoxLayout()
        add_pos_layout.addWidget(self.pos_combobox)
        add_pos_layout.addWidget(self.add_pos_button)
        pos_layout.addLayout(add_pos_layout)

        # 已指派職位的表格
        self.positions_table.setColumnCount(3)
        self.positions_table.setHorizontalHeaderLabels(["職務名稱", "主要職位", "操作"])
        self.positions_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.positions_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.positions_table.verticalHeader().hide()
        pos_layout.addWidget(self.positions_table)
        
        pos_groupbox.setLayout(pos_layout)
        main_layout.addWidget(pos_groupbox)

        # -------------------- 對話方塊按鈕 --------------------
        main_layout.addWidget(self.button_box)

    def setup_connections(self):
        """設定所有訊號與槽的連接"""
        self.add_pos_button.clicked.connect(self.add_position_to_table)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

    def _add_row_to_table(self, position_name, is_primary=False):
        """私有輔助方法，用於向表格中新增一行並設定好元件"""
        row_count = self.positions_table.rowCount()
        self.positions_table.insertRow(row_count)

        # 第一欄：職務名稱 (文字)
        self.positions_table.setItem(row_count, 0, QTableWidgetItem(position_name))

        # 第二欄：主要職位 (RadioButton)
        radio_button = QRadioButton()
        if is_primary:
            radio_button.setChecked(True)
        # 將 RadioButton 放入 QButtonGroup 進行管理
        self.primary_button_group.addButton(radio_button)
        # 為了讓 RadioButton 在儲存格中置中，需要一個容器 Widget
        cell_widget = QWidget()
        h_layout = QHBoxLayout(cell_widget)
        h_layout.addWidget(radio_button)
        h_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        h_layout.setContentsMargins(0, 0, 0, 0)
        self.positions_table.setCellWidget(row_count, 1, cell_widget)

        # 第三欄：操作 (移除按鈕)
        remove_button = QPushButton("移除")
        # 使用 lambda 傳遞參數，讓槽函式知道要刪除哪一列
        remove_button.clicked.connect(lambda: self.remove_position_from_table(position_name))
        self.positions_table.setCellWidget(row_count, 2, remove_button)

    # --- 公開方法 (Public Methods) ---

    def load_data(self, member_data, all_positions):
        """
        從外部載入資料來填充整個對話方塊。
        
        Args:
            member_data (dict): 包含會員基本資料和其職位列表的字典。
            all_positions (list): 包含所有可選職位名稱的字串列表。
        """
        self.all_positions_list = all_positions
        
        # 載入基本資料
        self.name_edit.setText(member_data.get("name", ""))
        self.phone_edit.setText(member_data.get("phone", ""))

        # 填充下拉選單
        self.pos_combobox.addItems(self.all_positions_list)

        # 清空並填充職位表格
        self.positions_table.setRowCount(0)
        member_positions = member_data.get("positions", [])
        for pos in member_positions:
            self._add_row_to_table(pos.get('name'), pos.get('is_primary', False))
            
        # 如果載入後沒有任何職位，或沒有主要職位，則自動將第一個設為主要
        if self.positions_table.rowCount() > 0 and not self.primary_button_group.checkedButton():
            self.positions_table.cellWidget(0, 1).findChild(QRadioButton).setChecked(True)

    def get_form_data(self):
        """
        從 UI 介面讀取使用者修改後的資料，並以字典格式返回。
        這是按下 "OK" 按鈕後，主程式應該呼叫的方法。
        """
        positions = []
        # 檢查是否有主要職位被選中
        if self.positions_table.rowCount() > 0 and not self.primary_button_group.checkedButton():
            QMessageBox.warning(self, "資料錯誤", "請為會員指派一個主要職位！")
            return None # 返回 None 表示資料驗證失敗

        for row in range(self.positions_table.rowCount()):
            pos_name = self.positions_table.item(row, 0).text()
            radio_button = self.positions_table.cellWidget(row, 1).findChild(QRadioButton)
            is_primary = radio_button.isChecked()
            positions.append({"name": pos_name, "is_primary": is_primary})
        
        return {
            "name": self.name_edit.text(),
            "phone": self.phone_edit.text(),
            "positions": positions
        }

    # --- 槽函式 (Slots) ---

    def add_position_to_table(self):
        """槽函式：處理 '新增職位' 按鈕的點擊事件"""
        selected_pos = self.pos_combobox.currentText()
        if not selected_pos:
            return

        # 檢查是否已存在於表格中
        current_positions = [self.positions_table.item(row, 0).text() 
                             for row in range(self.positions_table.rowCount())]
        if selected_pos in current_positions:
            QMessageBox.information(self, "提示", f"職位 '{selected_pos}' 已經指派。")
            return

        # 如果是新增的第一個職位，自動將其設為主要職位
        is_first = self.positions_table.rowCount() == 0
        self._add_row_to_table(selected_pos, is_primary=is_first)

    def remove_position_from_table(self, position_to_remove):
        """槽函式：處理 '移除' 按鈕的點擊事件"""
        for row in range(self.positions_table.rowCount()):
            if self.positions_table.item(row, 0).text() == position_to_remove:
                # 從 QButtonGroup 中移除，這非常重要！
                radio_button = self.positions_table.cellWidget(row, 1).findChild(QRadioButton)
                self.primary_button_group.removeButton(radio_button)
                
                was_primary = radio_button.isChecked()
                self.positions_table.removeRow(row)

                # 如果移除的是主要職位，且表格中還有其他職位，則自動將第一個設為新的主要職位
                if was_primary and self.positions_table.rowCount() > 0:
                    new_primary_radio = self.positions_table.cellWidget(0, 1).findChild(QRadioButton)
                    new_primary_radio.setChecked(True)
                break


if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # 建立一個對話方塊實例
    dialog = MemberEditDialog()
    
    # 使用模擬資料來填充它
    dialog.load_data(EXISTING_MEMBER_DATA, ALL_POSITIONS)
    
    # 顯示對話方塊，並根據使用者的操作決定後續動作
    if dialog.exec() == QDialog.DialogCode.Accepted:
        # 如果使用者按下 "OK"，就獲取並印出表單資料
        final_data = dialog.get_form_data()
        if final_data:
            print("--- 表單儲存成功 ---")
            print("基本資料:")
            print(f"  姓名: {final_data['name']}")
            print(f"  電話: {final_data['phone']}")
            print("職位資料:")
            for pos in final_data['positions']:
                primary_str = " (主要)" if pos['is_primary'] else ""
                print(f"  - {pos['name']}{primary_str}")
    else:
        print("--- 使用者取消操作 ---")
        
    sys.exit(app.exec())
