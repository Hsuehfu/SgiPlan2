import sqlite3
import csv

# --- 設定 ---
DB_NAME = 'gakkai_members.db'
SENIORS_CSV = '指導與御書-1.xlsx - 指導前輩資料.csv'
LECTURERS_CSV = '指導與御書-1.xlsx - 御書講師資料.csv'

def create_connection(db_file):
    """ 建立到 SQLite 資料庫的連線 """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"成功連線到 SQLite 版本 {sqlite3.version}")
    except sqlite3.Error as e:
        print(e)
    return conn

def create_tables(conn):
    """ 建立資料表 """
    try:
        cursor = conn.cursor()
        
        # 建立指導前輩資料表
        # 注意：原始 CSV 有5個欄位，但第4、5欄位看似為空，這裡仍為其建立欄位以保持結構完整
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS senior_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            title TEXT,
            phone TEXT,
            notes1 TEXT,
            notes2 TEXT
        );
        """)
        print("資料表 'senior_members' 已建立或已存在。")

        # 建立御書講師資料表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS lecturers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            branch_title TEXT,
            phone TEXT,
            qualification TEXT,
            availability TEXT,
            remarks TEXT
        );
        """)
        print("資料表 'lecturers' 已建立或已存在。")
        
    except sqlite3.Error as e:
        print(f"建立資料表時發生錯誤: {e}")

def import_csv_data(conn, csv_file, table_name):
    """ 從 CSV 檔案匯入資料到指定的資料表 """
    cursor = conn.cursor()
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            header = next(csv_reader, None) # 略過標頭行

            # 根據資料表名稱決定插入語句
            if table_name == 'senior_members':
                # 假設CSV有5欄
                insert_sql = "INSERT INTO senior_members (name, title, phone, notes1, notes2) VALUES (?, ?, ?, ?, ?)"
                data_to_insert = [tuple(row) for row in csv_reader if any(field.strip() for field in row)]
            elif table_name == 'lecturers':
                # 假設CSV有6欄
                insert_sql = "INSERT INTO lecturers (name, branch_title, phone, qualification, availability, remarks) VALUES (?, ?, ?, ?, ?, ?)"
                # 過濾掉可能是支部名稱或完全為空的行
                data_to_insert = [tuple(row) for row in csv_reader if len(row) == 6 and row[0].strip()]
            else:
                print(f"未知的資料表: {table_name}")
                return

            if data_to_insert:
                cursor.executemany(insert_sql, data_to_insert)
                conn.commit()
                print(f"成功將 {len(data_to_insert)} 筆資料匯入到 '{table_name}' 資料表。")
            else:
                print(f"在 {csv_file} 中沒有找到可匯入的資料。")

    except FileNotFoundError:
        print(f"錯誤：找不到檔案 {csv_file}。請確認檔案名稱和路徑是否正確。")
    except Exception as e:
        print(f"匯入 {csv_file} 時發生錯誤: {e}")


def main():
    """ 主執行函式 """
    # 建立資料庫連線
    conn = create_connection(DB_NAME)

    if conn is not None:
        # 建立資料表
        create_tables(conn)

        # 匯入指導前輩資料
        # 由於此CSV沒有標頭，我們直接匯入
        print("\n--- 開始匯入指導前輩資料 ---")
        try:
            with open(SENIORS_CSV, 'r', encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                # 過濾掉完全為空的行
                data_to_insert = [tuple(row) for row in csv_reader if any(field.strip() for field in row)]
                if data_to_insert:
                    cursor = conn.cursor()
                    cursor.executemany(
                        "INSERT INTO senior_members (name, title, phone, notes1, notes2) VALUES (?, ?, ?, ?, ?)",
                        data_to_insert
                    )
                    conn.commit()
                    print(f"成功將 {len(data_to_insert)} 筆資料匯入到 'senior_members' 資料表。")
        except FileNotFoundError:
             print(f"錯誤：找不到檔案 {SENIORS_CSV}。")
        except Exception as e:
            print(f"匯入 {SENIORS_CSV} 時發生錯誤: {e}")


        # 匯入御書講師資料 (有標頭)
        print("\n--- 開始匯入御書講師資料 ---")
        import_csv_data(conn, LECTURERS_CSV, 'lecturers')

        # 關閉連線
        conn.close()
        print(f"\n處理完成，資料庫連線已關閉。資料已存入 {DB_NAME}。")
    else:
        print("錯誤！無法建立資料庫連線。")

if __name__ == '__main__':
    main()