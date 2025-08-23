from PySide6.QtWidgets import (
    QHBoxLayout, QPushButton, QFileDialog, QTableWidget,
    QTableWidgetItem, QProgressBar, QLabel, QHeaderView, QMessageBox
)
from PySide6.QtGui import QColor
from PySide6.QtCore import Slot
from viewmodels.import_viewmodel import ImportViewModel
import pandas as pd
from views.base_management_widget import BaseManagementWidget

class ImportWidget(BaseManagementWidget):
    """會員匯入功能的 UI 分頁。"""
    def __init__(self, viewmodel: ImportViewModel, parent=None):
        super().__init__(viewmodel, parent)
        self._init_base_ui() # Call BaseManagementWidget's UI setup
        self.init_import_ui() # New method for import-specific UI
        self.setup_connections()

    def init_import_ui(self):
        # --- 頂部控制列 ---
        top_layout = QHBoxLayout()
        self.select_file_button = QPushButton("選擇 Excel 檔案")
        self.file_path_label = QLabel("尚未選擇檔案")
        self.import_button = QPushButton("開始匯入")
        self.import_button.setEnabled(False) # 預設禁用
        
        top_layout.addWidget(self.select_file_button)
        top_layout.addWidget(self.file_path_label, 1) # 讓標籤佔用更多空間
        top_layout.addWidget(self.import_button)
        self.main_layout.addLayout(top_layout)

        # --- 預覽表格 ---
        self.preview_table = QTableWidget()
        self.main_layout.addWidget(self.preview_table)

        # --- 進度條 ---
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False) # 預設隱藏
        self.main_layout.addWidget(self.progress_bar)

        # 隱藏 BaseManagementWidget 的 CRUD 按鈕，因為 ImportWidget 不使用它們
        self.add_button.setVisible(False)
        self.edit_button.setVisible(False)
        self.delete_button.setVisible(False)

    def _get_window_title(self):
        return "資料匯入"

    def _get_search_placeholder(self):
        return "搜尋檔案路徑或狀態..."

    def _add_specific_filters(self, layout):
        pass # ImportWidget 沒有額外的篩選器

    def _clear_search(self):
        self.file_path_label.setText("尚未選擇檔案")
        self.import_button.setEnabled(False)
        self.preview_table.clearContents()
        self.preview_table.setRowCount(0)
        self.preview_table.setColumnCount(0)

    def _get_status_bar_message(self):
        return "請選擇要匯入的Excel 檔"

    def setup_connections(self):
        self.select_file_button.clicked.connect(self.open_file_dialog)
        self.import_button.clicked.connect(self.viewmodel.start_import)

        self.viewmodel.preview_data_loaded.connect(self.display_preview)
        self.viewmodel.import_progress.connect(self.update_progress)
        self.viewmodel.import_finished.connect(self.on_import_finished)
        self.viewmodel.is_importing_changed.connect(self.on_import_state_changed)

    @Slot()
    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "選取要匯入的會員 Excel 檔案", "", "Excel 檔案 (*.xlsx *.xls)"
        )
        if file_path:
            self.file_path_label.setText(file_path)
            self.viewmodel.load_file_for_preview(file_path)

    @Slot(pd.DataFrame)
    def display_preview(self, df):
        self.preview_table.clear()
        self.preview_table.setRowCount(df.shape[0])
        self.preview_table.setColumnCount(df.shape[1] + 1) # 增加一欄用於狀態
        
        headers = df.columns.tolist() + ["匯入狀態"]
        self.preview_table.setHorizontalHeaderLabels(headers)

        for row_idx, row_data in enumerate(df.itertuples(index=False)):
            for col_idx, cell_data in enumerate(row_data):
                self.preview_table.setItem(row_idx, col_idx, QTableWidgetItem(str(cell_data)))
        
        self.preview_table.resizeColumnsToContents()
        self.preview_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.import_button.setEnabled(True)

    @Slot(int, str, str)
    def update_progress(self, row_index, status, message):
        total_rows = self.preview_table.rowCount()
        self.progress_bar.setValue(int(((row_index + 1) / total_rows) * 100))

        status_item = QTableWidgetItem(message)
        color = QColor("red") if status == "failure" else QColor("green")
        
        # 設定整列的背景顏色
        for col in range(self.preview_table.columnCount()):
            item = self.preview_table.item(row_index, col)
            if item:
                item.setBackground(color)
        
        status_column_index = self.preview_table.columnCount() - 1
        self.preview_table.setItem(row_index, status_column_index, status_item)

    @Slot(str)
    def on_import_finished(self, summary_text):
        QMessageBox.information(self, "匯入完成", summary_text)
        self.progress_bar.setVisible(False)

    @Slot(bool)
    def on_import_state_changed(self, is_importing):
        self.import_button.setEnabled(not is_importing)
        self.select_file_button.setEnabled(not is_importing)
        self.progress_bar.setVisible(is_importing)
        if is_importing:
            self.progress_bar.setValue(0)

