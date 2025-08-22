from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QComboBox

class RegionDialog(QDialog):

    def __init__(self, viewmodel, parent=None):
        super().__init__(parent)
        self.viewmodel = viewmodel
        self.init_ui()
        self.viewmodel.save_failed.connect(self._on_save_failed)
        self.viewmodel.saved_successfully.connect(self.accept)
        self.viewmodel.parents_loaded.connect(self.populate_parents)
        self.viewmodel.load_failed.connect(self._on_load_failed)

        # Populate fields if editing
        if self.viewmodel.is_editing():
            self.setWindowTitle("編輯地區")
            self.name_input.setText(self.viewmodel.name)
        else:
            self.setWindowTitle("新增地區")

        self.load_initial_data()

    def init_ui(self):
        # self.setFixedSize(300, 150)
        self.setMinimumWidth(350)
        layout = QVBoxLayout(self)

        # Region Name
        name_layout = QHBoxLayout()
        name_label = QLabel("地區名稱:")
        self.name_input = QLineEdit()
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)

        # Parent Region
        parent_layout = QHBoxLayout()
        parent_label = QLabel("父級地區:")
        self.parent_combo = QComboBox()
        parent_layout.addWidget(parent_label)
        parent_layout.addWidget(self.parent_combo)
        layout.addLayout(parent_layout)

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
        self.viewmodel.parent_id = self.parent_combo.currentData()
        # Tell the viewmodel to save
        self.viewmodel.save()

    def _on_save_failed(self, message):
        QMessageBox.critical(self, "錯誤", message)    

    def populate_parents(self, parents):
        self.parent_combo.clear()
        self.parent_combo.addItem("無 (設為頂層地區)", None)
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
        # 或許直接關閉對話框
        # self.reject()