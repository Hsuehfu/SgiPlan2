import pandas as pd
from PySide6.QtCore import QObject, Signal, Slot, QThread, Property

from services.member_importer import MemberImporter, RowResult

class ImportWorker(QObject):
    """
    在背景執行緒中執行匯入任務的 Worker。
    """
    progress = Signal(RowResult)
    finished = Signal(dict)

    def __init__(self, importer: MemberImporter, dataframe: pd.DataFrame):
        super().__init__()
        self.importer = importer
        self.dataframe = dataframe
        self.is_running = True

    def run(self):
        """執行匯入並發出訊號。"""
        success_count = 0
        failure_count = 0
        for result in self.importer.run_import(self.dataframe):
            if not self.is_running:
                break
            self.progress.emit(result)
            if result.status == 'success':
                success_count += 1
            else:
                failure_count += 1
        
        summary = {'success': success_count, 'failure': failure_count}
        self.finished.emit(summary)

    def stop(self):
        self.is_running = False

class ImportViewModel(QObject):
    """匯入分頁的 ViewModel。"""
    preview_data_loaded = Signal(pd.DataFrame)
    import_progress = Signal(int, str, str) # row_index, status, message
    import_finished = Signal(str)
    is_importing_changed = Signal(bool)

    def __init__(self, session_factory, parent=None):
        super().__init__(parent)
        self.session_factory = session_factory
        self.importer = MemberImporter(self.session_factory)
        self.dataframe = None
        self._is_importing = False
        self.worker_thread = None

    @Property(bool, notify=is_importing_changed)
    def is_importing(self):
        return self._is_importing

    def _set_is_importing(self, value):
        if self._is_importing != value:
            self._is_importing = value
            self.is_importing_changed.emit(value)

    @Slot(str)
    def load_file_for_preview(self, file_path):
        """載入 Excel 檔案以供預覽。"""
        try:
            self.dataframe = self.importer.preview_excel(file_path)
            self.preview_data_loaded.emit(self.dataframe)
        except Exception as e:
            # 可以在這裡發出一個錯誤訊號
            print(f"Error loading file: {e}")

    @Slot()
    def start_import(self):
        """開始執行匯入程序。"""
        if self.dataframe is None or self.is_importing:
            return

        self._set_is_importing(True)
        self.worker = ImportWorker(self.importer, self.dataframe)
        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)

        self.worker.progress.connect(self._on_progress_update)
        self.worker.finished.connect(self._on_import_finished)
        self.worker_thread.started.connect(self.worker.run)
        
        self.worker_thread.start()

    def _on_progress_update(self, result: RowResult):
        self.import_progress.emit(result.row_index, result.status, result.message)

    def _on_import_finished(self, summary):
        self._set_is_importing(False)
        self.worker_thread.quit()
        self.worker_thread.wait()
        
        summary_text = f"匯入完成！成功: {summary['success']} 筆, 失敗: {summary['failure']} 筆。"
        self.import_finished.emit(summary_text)

