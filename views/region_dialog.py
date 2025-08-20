from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox

class RegionDialog(QDialog):

    def __init__(self, viewmodel, parent=None):
        super().__init__(parent)
        self.viewmodel = viewmodel
        self.init_ui()
        self.viewmodel.error_occurred.connect(self._show_error_message) 
        self.viewmodel.region_saved.connect(self.accept)

        # Populate fields if editing
        if self.viewmodel.is_editing():
            self.setWindowTitle("編輯地區")
            self.name_input.setText(self.viewmodel.name)
        else:
            self.setWindowTitle("新增地區")

    def init_ui(self):
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

    def _save_region(self):
        # Update the viewmodel's state from the UI
        self.viewmodel.name = self.name_input.text().strip()
        # Tell the viewmodel to save
        self.viewmodel.save()

    def _show_error_message(self, message):
        QMessageBox.critical(self, "錯誤", message)    

    def load_initial_data(self):
        pass
