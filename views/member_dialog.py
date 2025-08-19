"""負責顯示新增或編輯會員資料的對話框。

此對話框遵循 MVVM 架構，與 MemberDialogViewModel 互動，
處理使用者輸入並顯示會員資料。
"""
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QComboBox, QDialogButtonBox, QFormLayout, QCheckBox
from PySide6.QtCore import Qt

from viewmodels.member_dialog_viewmodel import MemberDialogViewModel


class MemberDialog(QDialog):
    """一個用於新增或編輯會員資料的對話框。

    Attributes:
        viewmodel (MemberDialogViewModel): 與此視圖對應的視圖模型。
        name_input (QLineEdit): 用於輸入會員姓名的文字方塊。
        phone_number_input (QLineEdit): 用於輸入會員電話的文字方塊。
        is_schedulable_checkbox (QCheckBox): 用於設定會員是否可排班的核取方塊。
        region_combo (QComboBox): 用於選擇會員所屬地區的下拉式選單。
        button_box (QDialogButtonBox): 包含確定和取消按鈕的按鈕盒。
    """

    def __init__(self, viewmodel: MemberDialogViewModel, parent=None):
        """初始化 MemberDialog。

        Args:
            viewmodel (MemberDialogViewModel): 此對話框對應的視圖模型。
            parent (QWidget, optional): 父元件。預設為 None。
        """
        super().__init__(parent)
        self.viewmodel = viewmodel

        self._setup_ui()
        self._connect_signals()

        # 連接 ViewModel 的訊號
        self.viewmodel.regions_loaded.connect(self.populate_regions)

        # 如果是編輯模式，從 ViewModel 載入資料
        if self.viewmodel.is_editing():  # <--- 呼叫公開方法，而不是存取私有屬性
            self._populate_fields_from_viewmodel()
            self.setWindowTitle("編輯會員")

    def _populate_fields_from_viewmodel(self):
        """根據 ViewModel 中的會員資料填充對話框欄位。"""
        self.name_input.setText(self.viewmodel.name)
        self.phone_number_input.setText(self.viewmodel.phone_number)
        self.is_schedulable_checkbox.setChecked(bool(self.viewmodel.is_schedulable))
        # populate_regions 會在 regions_loaded 訊號發出時處理選擇正確的地區

    def _setup_ui(self):
        """設定 UI 元件和版面配置。"""
        self.setWindowTitle("新增會員")
        self.setMinimumWidth(300)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        self._create_widgets()
        form_layout = self._create_layout()

        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.button_box)

        self.setLayout(main_layout)

    def _create_widgets(self):
        """建立所有 UI 元件。"""
        self.name_input = QLineEdit()
        self.phone_number_input = QLineEdit()
        self.is_schedulable_checkbox = QCheckBox("可排班")
        self.region_combo = QComboBox()
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)

    def _create_layout(self) -> QFormLayout:
        """建立並返回表單版面配置。"""
        form_layout = QFormLayout()
        form_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form_layout.addRow("姓名:", self.name_input)
        form_layout.addRow("電話:", self.phone_number_input)
        form_layout.addRow("是否可排班:", self.is_schedulable_checkbox)
        form_layout.addRow("地區:", self.region_combo)
        return form_layout

    def _connect_signals(self):
        """連接所有訊號與槽。"""
        self.button_box.accepted.connect(self._on_accept_clicked)
        self.button_box.rejected.connect(self.reject)

    def _on_accept_clicked(self):
        """處理確定按鈕點擊事件，將資料保存到 ViewModel。"""
        self.viewmodel.name = self.name_input.text()
        self.viewmodel.phone_number = self.phone_number_input.text()
        self.viewmodel.is_schedulable = self.is_schedulable_checkbox.isChecked()
        self.viewmodel.region_id = self.region_combo.currentData()
        self.viewmodel.save()
        self.accept()

    def populate_regions(self, regions: list[tuple[int, str]]):
        """當 ViewModel 載入地區後，填充下拉選單。"""
        self.region_combo.clear()
        for region_id, region_name in regions:
          self.region_combo.addItem(region_name, userData=region_id)

       # 唯一的真相來源：永遠以 ViewModel 的 region_id 為準
        index = -1 # Initialize index
        if self.viewmodel.region_id is not None:
          index = self.region_combo.findData(self.viewmodel.region_id)
          if index != -1:
            self.region_combo.setCurrentIndex(index)

    def load_initial_data(self):
        """載入對話框的初始資料，例如地區列表。"""
        self.viewmodel.load_regions()

