from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from viewmodels.position_dialog_viewmodel import PositionDialogViewModel

class PositionDialog(QDialog):
    def __init__(self, viewmodel: PositionDialogViewModel, parent=None):
        super().__init__(parent)
        self.viewmodel = viewmodel
        self.setWindowTitle("職務編輯")
        self.init_ui()
        self.viewmodel.position_saved.connect(self.accept)
        self.viewmodel.error_occurred.connect(self._show_error_message)

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # Name input
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("職務名稱:"))
        self.name_input = QLineEdit()
        name_layout.addWidget(self.name_input)
        main_layout.addLayout(name_layout)

        # Buttons
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("儲存")
        self.cancel_button = QPushButton("取消")
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        main_layout.addLayout(button_layout)

        self.save_button.clicked.connect(self._save_position)
        self.cancel_button.clicked.connect(self.reject)

    def _save_position(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "輸入錯誤", "職務名稱不能為空。")
            return
        self.viewmodel.save_position(name)

    def _set_item_data(self, position):
        self.viewmodel.set_position(position)
        self.name_input.setText(self.viewmodel.get_position_name())
        self.setWindowTitle("編輯職務")

    def _get_item_data(self):
        return {'name': self.name_input.text().strip()}

    def _show_error_message(self, message):
        QMessageBox.critical(self, "錯誤", message)
