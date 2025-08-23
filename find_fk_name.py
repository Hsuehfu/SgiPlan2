import sqlalchemy
from sqlalchemy import create_engine, inspect

# 資料庫檔案路徑
DATABASE_URL = "sqlite:///./data/app.db"

def find_foreign_key_constraint_name(table_name, column_name, referenced_table_name, referenced_column_name):
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)

    fk_constraints = inspector.get_foreign_keys(table_name)

    for fk in fk_constraints:
        # 檢查是否是我們要找的外鍵
        if (fk['constrained_columns'] == [column_name] and
            fk['referred_table'] == referenced_table_name and
            fk['referred_columns'] == [referenced_column_name]):
            print(f"找到外鍵約束名稱: {fk['name']}")
            return fk['name']
    print(f"未找到 {table_name}.{column_name} 指向 {referenced_table_name}.{referenced_column_name} 的外鍵約束名稱。")
    return None

if __name__ == "__main__":
    print("正在查詢 regions 表的外鍵約束名稱...")
    find_foreign_key_constraint_name('regions', 'parent_id', 'regions', 'id')