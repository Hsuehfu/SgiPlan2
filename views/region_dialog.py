from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PySide6.QtCore import Signal

class RegionDialog(QDialog):
    region_added = Signal()
    region_updated = Signal()

    def __init__(self, viewmodel, parent=None):
        super().__init__(parent)
        self.viewmodel = viewmodel
        self.region_id = None
        self.init_ui()
        self.viewmodel.error_occurred.connect(self._show_error_message) 
        self.viewmodel.region_saved.connect(self.accept)       

    def init_ui(self):
        self.setWindowTitle("地區資料")
        self.setFixedSize(300, 150)

        layout = QVBoxLayout(self)

        # Region Name
        name_layout = QHBoxLayout()
        name_label = QLabel("地區名稱:")
        self.name_input = QLineEdit()
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)

        # Buttons
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("儲存")
        self.cancel_button = QPushButton("取消")
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.save_button.clicked.connect(self._save_region)
        self.cancel_button.clicked.connect(self.reject)

    def _get_item_data(self):
        return {
            'name': self.name_input.text(),
        }

    def _set_item_data(self, region):
        self.region_id = region.id
        self.name_input.setText(region.name)

    def _save_region(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "輸入錯誤", "地區名稱不能為空。")
            return

        region_data = {'name': name}

        if self.region_id:
            self.viewmodel.update_region(self.region_id, region_data)
        else:
            self.viewmodel.add_region(region_data)

    def _show_error_message(self, message):
        QMessageBox.critical(self, "錯誤", message)    