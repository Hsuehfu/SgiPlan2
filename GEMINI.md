# Gemini 專案說明：SgiPlan2

本檔案為 SgiPlan2 專案提供相關背景資訊與操作說明。

## 專案概觀

SgiPlan2 是一款使用 Python 和 PySide6 開發的桌面應用程式 **[優化]**，旨在協助國際創價學會（SGI）的使用者高效地管理會員資料、規劃活動與整理指導內容。

**[新增] 核心功能與使用者情境**
* **會員管理**: 新增、查詢、修改會員的基本資料與組織歸屬。
* **活動規劃**: 建立新的活動，並指派參與者。
* **資料匯入**: 從外部 Excel 檔案批次匯入會員或活動資料。

## 技術棧

* **語言:** Python 3.13
* **UI 框架:** PySide6
* **資料庫:** SQLite
* **ORM:** SQLAlchemy
* **架構:** Model-View-ViewModel (MVVM)

## 專案結構

本專案遵循 MVVM 架構以分離關注點：

* `main.py`: 應用程式的主要進入點。
* `data/app.db`: SQLite 資料庫檔案。
* `models/`: 包含定義資料庫結構的 SQLAlchemy ORM 模型。 **[新增]** (例如：`member.py`, `activity.py`)
    * `database.py`: 設定資料庫連線和會話。
* `views/`: 包含使用 PySide6 建立的 UI 元件（視窗和元件）。
    * `main_window.py`: 應用程式的主視窗。
* `viewmodels/`: 包含視圖模型，用於處理應用程式邏輯。
    * `main_viewmodel.py`: 主視窗的視圖模型。
* `data_importer.py`: 用於將資料從 Excel 檔案匯入的腳本。
* `resouce/import/`: 包含待匯入資料檔案的目錄。

## 開始使用

### 先決條件

* Python 3.13
* 虛擬環境工具

### 設定與執行應用程式

1.  **啟用虛擬環境:**
    ```shell
    .\venv\Scripts\activate
    ```

2.  **安裝依賴套件:**
    ```shell
    pip install -r requirements.txt
    ```
3.  **[新增] 初始化資料庫:**
    首次執行時，應用程式會自動檢查 `data/app.db` 是否存在。若不存在，將根據 `models/` 中的定義自動建立資料庫和資料表。

4.  **執行應用程式:**
    ```shell
    python main.py
    ```

## 開發指南

* **程式碼風格:** 請遵循 PEP 8 Python 程式碼風格指南。
* **MVVM 架構:** **[新增]** 請嚴格遵守 MVVM 模式。UI 相關操作應在 `views` 中，業務邏輯和狀態管理在 `viewmodels` 中，資料庫操作則透過 `models` 進行。避免在 View 中直接呼叫 Model。
* **PySide6 版本注意事項:** PySide6 在 6.7 版後有重大變更，如 `QAction` 已移至 `QtGui` 模組。開發時請參考官方文件。
* **UI 開發:** 在 `views` 目錄中建立和修改 UI 元件。若需使用 Qt Designer，其執行檔位於 `venv/Scripts/designer.exe`。
* **依賴管理:** 新的依賴套件請務必新增到 `requirements.txt` 檔案中。

## 給 Gemini 的具體指令

**[新增] 你的角色**
你是一位資深的 Python 桌面應用程式開發專家，熟悉 PySide6 和 SQLAlchemy，並注重程式碼的可讀性、效能與安全性。

### 程式碼生成
* 當我新增一個函式後，請為我生成符合 Google 風格的 Docstring。**[新增]** 範例如下：
    ```python
    """Fetches rows from a Smalltable.

    Retrieves rows pertaining to the given keys from the Table instance
    represented by table_handle.  String keys will be UTF-8 encoded.

    Args:
        table_handle: An open smalltable.Table instance.
        keys: A sequence of strings representing the key of each table row
            to fetch.
        require_all_keys: If True only rows with values set for all keys will be
            returned.

    Returns:
        A dict mapping keys to the corresponding table row data
        fetched. Each row is represented as a tuple of strings. For
        example:

        {b'Serak': ('Rigel VII', 'Preparer'),
         b'Zim': ('Irk', 'Invader'),
         b'Lrrr': ('Omicron Persei 8', 'Emperor')}

        Returned keys are always bytes.  If a key from the keys argument is
        missing from the dictionary, then that row was not found in the
        table (and require_all_keys must have been False).
    """
    ```

### 程式碼審查
* **安全性:** 檢查所有資料庫查詢是否透過 SQLAlchemy ORM 進行，避免使用原始 SQL 字串拼接，以防止 SQL 注入。
* **效能:** 提醒我注意是否有不必要的迴圈或可能導致延遲的 I/O 操作。
* **可讀性:** 如果函式超過 50 行，或邏輯複雜度太高，請建議我進行重構 (Refactor)。
* **[新增] 架構:** 確保程式碼遵循 MVVM 架構。例如，View 不應包含業務邏輯。

### **[新增] 測試**
* 當我完成一個 ViewModel 中的方法時，請協助我使用 Python 內建的 `unittest.mock` 來為其編寫單元測試。

### **[優化] 回應與產出語言**
* 所有與我的互動、程式碼註解、Docstring 以及任何產出的文字，請**務必**使用**繁體中文 (Traditional Chinese)**。