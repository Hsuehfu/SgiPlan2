import sqlite3
import os


def add_hierarchy_to_regions(db_path: str):
    """修改 'regions' 資料表以支援階層式結構。

    此函式會新增一個 'parent_id' 欄位，並建立一個自我參考的外鍵。
    為了避免重複執行時發生錯誤，它會先檢查該欄位是否已存在。
    由於 SQLite 的限制，此操作是透過在一個交易中重建資料表來完成的。

    Args:
        db_path (str): SQLite 資料庫檔案的路徑。
    """
    if not os.path.exists(db_path):
        print(f"錯誤：找不到資料庫檔案 '{db_path}'")
        return

    conn = None
    try:
        # 1. 連線到資料庫
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print(f"成功連線到資料庫: {db_path}")

        # 2. 檢查 'parent_id' 欄位是否已存在
        cursor.execute("PRAGMA table_info(regions)")
        columns = [row[1] for row in cursor.fetchall()]
        if 'parent_id' in columns:
            print("欄位 'parent_id' 已存在於 'regions' 資料表中，跳過修改。")
            return

        print("欄位 'parent_id' 不存在，開始進行資料表結構修改...")

        # --- SQLite 修改資料表並新增外鍵的標準流程 ---
        # SQLite 的 ALTER TABLE 不支援直接新增外鍵約束。
        # 因此，標準做法是：建立一個有新結構的暫存資料表 -> 複製資料 -> 刪除舊資料表 -> 將暫存資料表改名。
        # 整個過程會在一個交易 (Transaction) 中完成，確保資料的完整性。

        # 3. 開始交易
        cursor.execute('BEGIN TRANSACTION')

        # 4. 建立一個具備新結構的暫存資料表
        #    假設原始資料表至少有 id 和 name 欄位
        cursor.execute("""
        CREATE TABLE regions_new (
            id INTEGER NOT NULL PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            parent_id INTEGER,
            FOREIGN KEY(parent_id) REFERENCES regions(id) ON DELETE SET NULL
        )
        """)
        print("已建立具備新結構的暫存資料表 'regions_new'。")

        # 5. 將資料從舊資料表複製到新資料表
        cursor.execute("""
        INSERT INTO regions_new (id, name)
        SELECT id, name FROM regions
        """)
        print("已將資料從舊資料表複製到新資料表。")

        # 6. 刪除舊的資料表
        cursor.execute('DROP TABLE regions')
        print("已刪除舊的 'regions' 資料表。")

        # 7. 將新資料表更名為原始名稱
        cursor.execute('ALTER TABLE regions_new RENAME TO regions')
        print("已將新資料表更名為 'regions'。")

        # 8. 提交交易，完成變更
        conn.commit()
        print("資料庫結構修改成功並已提交。")

    except sqlite3.Error as e:
        print(f"發生資料庫錯誤: {e}")
        if conn:
            print("正在還原變更...")
            conn.rollback()
    except Exception as e:
        print(f"發生非預期的錯誤: {e}")
        if conn:
            print("正在還原變更...")
            conn.rollback()
    finally:
        if conn:
            conn.close()
            print("資料庫連線已關閉。")


if __name__ == '__main__':
    # --- 設定資料庫路徑 ---
    # 假設此腳本放在專案根目錄，與 data 資料夾同級
    DB_FILE_PATH = os.path.join('data', 'app.db')

    print("--- 開始執行資料庫遷移腳本 ---")
    add_hierarchy_to_regions(DB_FILE_PATH)
    print("--- 腳本執行完畢 ---")

