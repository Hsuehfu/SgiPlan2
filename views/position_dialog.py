from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QComboBox
from viewmodels.position_dialog_viewmodel import PositionDialogViewModel

class PositionDialog(QDialog):
    def __init__(self, viewmodel: PositionDialogViewModel, parent=None):
        super().__init__(parent)
        self.viewmodel = viewmodel
        self.init_ui()
        self.viewmodel.position_saved.connect(self.accept)
        self.viewmodel.error_occurred.connect(self._show_error_message)
        self.viewmodel.parents_loaded.connect(self.populate_parents)
        self.viewmodel.load_failed.connect(self._on_load_failed)

        if self.viewmodel.is_editing():
            self.setWindowTitle("編輯職務")
            self.name_input.setText(self.viewmodel.name)
        else:
            self.setWindowTitle("新增職務")
        
        self.load_initial_data() # <--- Add this line

    def init_ui(self):
        self.setFixedSize(300, 200) # Adjusted size to accommodate new field
        main_layout = QVBoxLayout(self)

        # Name input
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("職務名稱:"))
        self.name_input = QLineEdit()
        name_layout.addWidget(self.name_input)
        main_layout.addLayout(name_layout)

        # Parent Position
        parent_layout = QHBoxLayout()
        parent_label = QLabel("上層職務:")
        self.parent_combo = QComboBox()
        parent_layout.addWidget(parent_label)
        parent_layout.addWidget(self.parent_combo)
        main_layout.addLayout(parent_layout)

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
        self.viewmodel.name = self.name_input.text().strip()
        self.viewmodel.parent_id = self.parent_combo.currentData()
        self.viewmodel.save()

    def _show_error_message(self, message):
        QMessageBox.critical(self, "錯誤", message)
   
    def populate_parents(self, parents):
        self.parent_combo.clear()
        self.parent_combo.addItem("無 (設為頂層職務)", None)
        for parent in parents:
            self.parent_combo.addItem(parent.name, parent.id)
        
        if self.viewmodel.parent_id:
            index = self.parent_combo.findData(self.viewmodel.parent_id)
            if index != -1:
                self.parent_combo.setCurrentIndex(index)

    def load_initial_data(self):
        self.viewmodel.load_possible_parents()

    def _on_load_failed(self, message):
        QMessageBox.critical(self, "載入錯誤", message)
