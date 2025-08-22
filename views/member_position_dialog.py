from PySide6.QtWidgets import QDialog, QVBoxLayout, QComboBox, QCheckBox, QDialogButtonBox, QFormLayout

class MemberPositionDialog(QDialog):
    def __init__(self, viewmodel, parent=None):
        super().__init__(parent)
        self.viewmodel = viewmodel
        self.setWindowTitle("指派職位")
        self.init_ui()
        self.viewmodel.positions_loaded.connect(self.populate_positions)
        self.viewmodel.load_positions()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.form_layout = QFormLayout()

        self.position_combo = QComboBox()
        self.is_primary_checkbox = QCheckBox("主要職位")

        self.form_layout.addRow("職位:", self.position_combo)
        self.form_layout.addRow("是否主要職位:", self.is_primary_checkbox)

        self.layout.addLayout(self.form_layout)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.layout.addWidget(self.button_box)

        self.setLayout(self.layout)

    def populate_positions(self, positions):
        self.position_combo.clear()
        for position in positions:
            self.position_combo.addItem(position.name, position.id)

    def get_position_data(self):
        return {
            "position_id": self.position_combo.currentData(),
            "is_primary": 1 if self.is_primary_checkbox.isChecked() else 0
        }

    def set_position_data(self, member_position):
        self.setWindowTitle("編輯職位")
        self.position_combo.setCurrentIndex(self.position_combo.findData(member_position.position_id))
        self.is_primary_checkbox.setChecked(member_position.is_primary == 1)
