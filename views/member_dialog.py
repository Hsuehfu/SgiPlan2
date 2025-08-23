"""負責顯示新增或編輯會員資料的對話框。

此對話框遵循 MVVM 架構，與 MemberDialogViewModel 互動，
處理使用者輸入並顯示會員資料。
"""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLineEdit, QComboBox, 
                               QDialogButtonBox, QFormLayout, QCheckBox, 
                               QMessageBox, QGroupBox, QHBoxLayout, 
                               QListWidget, QPushButton, QListWidgetItem)
from PySide6.QtCore import Qt, QSize

from viewmodels.member_dialog_viewmodel import MemberDialogViewModel


class MemberDialog(QDialog):
    """一個用於新增或編輯會員資料的對話框。

    Attributes:
        viewmodel (MemberDialogViewModel): 與此視圖對應的視圖模型。
        # ... 其他 UI 元件
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
        self.viewmodel.saved_successfully.connect(self.accept)
        self.viewmodel.save_failed.connect(self._on_save_failed)
        self.viewmodel.positions_loaded.connect(self._update_positions_view)
        self.viewmodel.assigned_positions_changed.connect(self._update_positions_view)
        self.viewmodel.departments_loaded.connect(self.populate_departments)

        # 如果是編輯模式，從 ViewModel 載入資料
        if self.viewmodel.is_editing():
            self._populate_fields_from_viewmodel()
            self.setWindowTitle("編輯會員")
        else:
            self.setWindowTitle("新增會員")


    def _populate_fields_from_viewmodel(self):
        """根據 ViewModel 中的會員資料填充對話框欄位。"""
        self.name_input.setText(self.viewmodel.name)
        self.phone_number_input.setText(self.viewmodel.phone_number)
        self.is_schedulable_checkbox.setChecked(bool(self.viewmodel.is_schedulable))
        # populate_regions 會在 regions_loaded 訊號發出時處理選擇正確的地區
        # _update_positions_view 會在 assigned_positions_changed 訊號發出時處理
        
    def _setup_ui(self):
        """設定 UI 元件和版面配置。"""
        self.setMinimumWidth(500) # 增加寬度以容納職位管理

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        self._create_widgets()
        
        form_layout = QFormLayout()
        form_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form_layout.addRow("姓名:", self.name_input)
        form_layout.addRow("電話:", self.phone_number_input)
        form_layout.addRow("是否可排班:", self.is_schedulable_checkbox)
        form_layout.addRow("地區:", self.region_combo)
        form_layout.addRow("部別:", self.department_combobox) 

        main_layout.addLayout(form_layout)
        
        positions_group_box = self._create_positions_group_box()
        main_layout.addWidget(positions_group_box)

        main_layout.addWidget(self.button_box)
        self.setLayout(main_layout)

    def _create_widgets(self):
        """建立所有 UI 元件。"""
        self.name_input = QLineEdit()
        self.phone_number_input = QLineEdit()
        self.is_schedulable_checkbox = QCheckBox("可排班")
        self.region_combo = QComboBox()
        self.department_combobox = QComboBox()

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)

        # 職位相關元件
        self.available_positions_list = QListWidget()
        self.assigned_positions_list = QListWidget()
        self.add_position_button = QPushButton(">>")
        self.remove_position_button = QPushButton("<<")


    def _create_positions_group_box(self) -> QGroupBox:
        """建立並返回職位管理的 GroupBox。"""
        positions_group_box = QGroupBox("職位管理 (雙擊已分配職位可設為主要)")
        positions_layout = QHBoxLayout()

        # 按鈕佈局
        button_layout = QVBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.add_position_button)
        button_layout.addWidget(self.remove_position_button)
        button_layout.addStretch()

        positions_layout.addWidget(self.available_positions_list)
        positions_layout.addLayout(button_layout)
        positions_layout.addWidget(self.assigned_positions_list)
        
        positions_group_box.setLayout(positions_layout)
        return positions_group_box

    def _connect_signals(self):
        """連接所有訊號與槽。"""
        self.button_box.accepted.connect(self._on_accept_clicked)
        self.button_box.rejected.connect(self.reject)

        self.add_position_button.clicked.connect(self._on_add_position)
        self.remove_position_button.clicked.connect(self._on_remove_position)
        self.assigned_positions_list.itemDoubleClicked.connect(self._on_set_primary_position)

    def _on_accept_clicked(self):
        """處理確定按鈕點擊事件，將資料保存到 ViewModel。"""
        self.viewmodel.name = self.name_input.text()
        self.viewmodel.phone_number = self.phone_number_input.text()
        self.viewmodel.is_schedulable = self.is_schedulable_checkbox.isChecked()
        self.viewmodel.region_id = self.region_combo.currentData()
        self.viewmodel.department_id = self.department_combobox.currentData()
        # 職位分配的變更已經在 ViewModel 中處理，只需呼叫 save
        self.viewmodel.save()

    def _on_save_failed(self, message: str):
        """顯示一個錯誤訊息對話框。"""
        QMessageBox.warning(self, "儲存失敗", message)

    def populate_regions(self, regions: list[tuple[int, str]]):
        """當 ViewModel 載入地區後，填充下拉選單。"""
        self.region_combo.clear()
        for region_id, region_name in regions:
            self.region_combo.addItem(region_name, userData=region_id)

        if self.viewmodel.region_id is not None:
            index = self.region_combo.findData(self.viewmodel.region_id)
            if index != -1:
                self.region_combo.setCurrentIndex(index)

    def populate_departments(self, departments: list[tuple[int, str]]):
        """當 ViewModel 載入部別後，填充下拉選單。"""
        self.department_combobox.clear()
        for department_id, department_name in departments:
            self.department_combobox.addItem(department_name, userData=department_id)

        if self.viewmodel.department_id is not None:
            index = self.department_combobox.findData(self.viewmodel.department_id)
            if index != -1:
                self.department_combobox.setCurrentIndex(index)

    def _update_positions_view(self):
        """更新可用和已分配的職位列表。"""
        # 獲取當前已分配職位的 ID 集合
        assigned_ids = {p["id"] for p in self.viewmodel.get_assigned_positions_for_view()}

        # 更新可用職位列表
        self.available_positions_list.clear()
        for pos in self.viewmodel.all_positions:
            if pos.id not in assigned_ids:
                item = QListWidgetItem(pos.name)
                item.setData(Qt.ItemDataRole.UserRole, pos.id)
                self.available_positions_list.addItem(item)

        # 更新已分配職位列表
        self.assigned_positions_list.clear()
        for pos_data in self.viewmodel.get_assigned_positions_for_view():
            display_text = f"{pos_data['name']}{' (主要)' if pos_data['is_primary'] else ''}"
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, pos_data['id'])
            self.assigned_positions_list.addItem(item)


    def _on_add_position(self):
        """處理新增職位按鈕點擊事件。"""
        selected_item = self.available_positions_list.currentItem()
        if selected_item:
            position_id = selected_item.data(Qt.ItemDataRole.UserRole)
            self.viewmodel.add_position(position_id)

    def _on_remove_position(self):
        """處理移除職位按鈕點擊事件。"""
        selected_item = self.assigned_positions_list.currentItem()
        if selected_item:
            position_id = selected_item.data(Qt.ItemDataRole.UserRole)
            self.viewmodel.remove_position(position_id)

    def _on_set_primary_position(self, item: QListWidgetItem):
        """處理設定主要職位的雙擊事件。"""
        position_id = item.data(Qt.ItemDataRole.UserRole)
        self.viewmodel.set_primary_position(position_id)

    def load_initial_data(self):
        """載入對話框的初始資料。"""
        self.viewmodel.load_regions()
        self.viewmodel.load_positions()
        self.viewmodel.load_departments()

