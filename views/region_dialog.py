from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from PySide6.QtCore import Signal

class RegionDialog(QDialog):
    region_added = Signal()
    region_updated = Signal()

    def __init__(self, viewmodel, parent=None):
        super().__init__(parent)
        self.viewmodel = viewmodel
        self.region_id = None
        self.init_ui()

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

        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def _get_item_data(self):
        return {
            'name': self.name_input.text(),
        }

    def _set_item_data(self, region):
        self.region_id = region.id
        self.name_input.setText(region.name)