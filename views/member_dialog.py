from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QComboBox, QDialogButtonBox, QFormLayout

class MemberDialog(QDialog):
    def __init__(self, viewmodel, parent=None):
        super().__init__(parent)
        self.viewmodel = viewmodel
        self.setWindowTitle("新增會員")
        self.init_ui()
        self.apply_stylesheet()

        self.viewmodel.regions_loaded.connect(self.populate_regions)
        self.viewmodel.load_regions()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.form_layout = QFormLayout()

        self.name_input = QLineEdit()
        self.region_combo = QComboBox()

        self.form_layout.addRow("姓名:", self.name_input)
        self.form_layout.addRow("地區:", self.region_combo)

        self.layout.addLayout(self.form_layout)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.layout.addWidget(self.button_box)

        self.setLayout(self.layout)

    def populate_regions(self, regions):
        for region in regions:
            self.region_combo.addItem(region.name, region.id)

    def get_member_data(self):
        return {
            "name": self.name_input.text(),
            "region_id": self.region_combo.currentData()
        }

    def set_member_data(self, member):
        self.setWindowTitle("編輯會員")
        self.name_input.setText(member.name)
        if member.region:
            self.region_combo.setCurrentIndex(self.region_combo.findData(member.region.id))

    def apply_stylesheet(self):
        self.setStyleSheet("""
            QDialog {
                font-size: 14px;
            }
            QLineEdit, QComboBox {
                padding: 5px;
                border: 1px solid #cccccc;
                border-radius: 4px;
            }
            QDialogButtonBox QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                text-align: center;
                text-decoration: none;
                font-size: 14px;
                margin: 4px 2px;
                border-radius: 4px;
            }
            QDialogButtonBox QPushButton:hover {
                background-color: #45a049;
            }
        """)