# -*- coding: utf-8 -*-
"""一個用於直接查詢資料庫以進行偵錯的暫時腳本。"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.region_model import Region

# 確保我們能找到 models 模組
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# --- 資料庫設定 ---
# 根據專案結構，資料庫位於專案根目錄下的 data/app.db
# 這個腳本在根目錄執行，所以路徑是正確的
DATABASE_URL = "sqlite:///data/app.db"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def check_regions():
    """查詢所有地區並將其列印到控制台。"""
    session = SessionLocal()
    print("--- 開始查詢地區資料 --- G-9823")
    try:
        regions = session.query(Region).all()
        if not regions:
            print("資料庫中未找到任何地區資料。")
        else:
            print(f"成功查詢到 {len(regions)} 筆地區資料：")
            for i, region in enumerate(regions):
                print(f"  {i+1}. ID: {region.id}, 名稱: {region.name}")
    except Exception as e:
        print(f"查詢時發生錯誤: {e}")
    finally:
        print("--- 查詢結束 ---")
        session.close()

if __name__ == "__main__":
    check_regions()
