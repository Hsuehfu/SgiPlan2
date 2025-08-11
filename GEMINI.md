# Gemini 專案說明：SgiPlan2

本檔案為 SgiPlan2 專案提供相關背景資訊與操作說明。

## 專案概觀

SgiPlan2 是一個使用 Python 和 PySide6 開發的桌面應用程式。從檔案名稱和結構來看，它似乎是一個用於管理國際創價學會（SGI）相關數據的工具，可能用於規劃活動、管理會員和指導資料。該應用程式使用資料庫來儲存數據。

## 技術棧

*   **語言:** Python
*   **UI 框架:** PySide6
*   **資料庫:** SQLite
*   **ORM:** SQLAlchemy
*   **架構:** Model-View-ViewModel (MVVM)

## 專案結構

本專案遵循 MVVM 架構以分離關注點：

*   `main.py`: 應用程式的主要進入點。
*   `data/app.db`: SQLite 資料庫檔案。
*   `models/`: 包含定義資料庫結構的 SQLAlchemy ORM 模型。
    *   `database.py`: 設定資料庫連線和會話。
*   `views/`: 包含使用 PySide6 建立的 UI 元件（視窗和元件）。
    *   `main_window.py`: 應用程式的主視窗。
*   `viewmodels/`: 包含視圖模型，用於處理應用程式邏輯，並作為模型和視圖之間的橋樑。
    *   `main_viewmodel.py`: 主視窗的視圖模型。
*   `data_importer.py`: 用於將資料（可能來自 Excel 檔案）匯入應用程式的腳本。
*   `resouce/import/`: 包含待匯入資料檔案的目錄。
*   `sample/`: 包含範例程式碼和實驗。
*   `venv/`: Python 虛擬環境。

## 開始使用

### 先決條件

*   Python 3.11
*   虛擬環境工具

### 設定與執行應用程式

1.  **建立並啟用虛擬環境:**
    專案中已包含 `venv` 目錄。請啟用它以使用：
    ```shell
    .\venv\Scripts\activate
    ```

2.  **安裝依賴套件:**
    專案中沒有 `requirements.txt` 檔案。根據 `venv` 目錄，主要的依賴套件是 `PySide6` 和 `SQLAlchemy`。建議建立一個 `requirements.txt` 檔案以便管理。
    ```shell
    pip install PySide6 SQLAlchemy pandas openpyxl
    ```
    *(註：`data_importer.py` 可能需要 `pandas` 和 `openpyxl` 來讀取 `.xlsx` 檔案。)*

3.  **執行應用程式:**
    ```shell
    python main.py
    ```

## 開發指南

*   **程式碼風格:** 請遵循 PEP 8 Python 程式碼風格指南。
*   **UI:** 在 `views` 目錄中使用 PySide6 建立和修改 UI 元C件。如果專案慣例是使用 `.ui` 檔案，請使用 Qt Designer (`designer.exe` 位於 `venv/Scripts`)，儘管目前目錄中沒有看到 `.ui` 檔案。
*   **資料庫:** 所有資料庫互動都應透過 `models` 目錄中定義的 SQLAlchemy 模型進行。若要變更資料庫結構，請相應地更新模型。
*   **業務邏輯:** 在 `viewmodels` 中實現業務邏輯，以將其與 UI 分離。
*   **依賴管理:** 將新的依賴套件新增到 `requirements.txt` 檔案中。