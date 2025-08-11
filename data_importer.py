import csv
import json
import os
from typing import List, Dict, Any, Optional

class DataImporter:
    """
    一個通用的資料匯入類別，可以根據檔案的副檔名自動解析資料。
    目前支援 .csv 和 .json 檔案。
    """

    def __init__(self, file_path: str):
        """
        初始化 DataImporter。

        :param file_path: 要匯入的資料檔案路徑。
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"錯誤：找不到檔案 '{file_path}'")
        self.file_path = file_path
        self.file_extension = os.path.splitext(file_path)[1].lower()

    def _load_csv(self) -> List[Dict[str, Any]]:
        """從 CSV 檔案載入資料，並將每一行轉換為字典。"""
        with open(self.file_path, mode='r', encoding='utf-8-sig') as file:
            # 使用 DictReader 可以方便地將每一行轉為字典
            reader = csv.DictReader(file)
            return list(reader)

    def _load_json(self) -> Any:
        """從 JSON 檔案載入資料。"""
        with open(self.file_path, mode='r', encoding='utf-8') as file:
            return json.load(file)

    def load_data(self) -> Optional[Any]:
        """
        根據檔案副檔名載入資料。

        :return: 載入的資料，如果檔案類型不支援或發生錯誤則返回 None。
        """
        try:
            if self.file_extension == '.csv':
                print(f"正在從 CSV 檔案載入資料: {self.file_path}")
                return self._load_csv()
            elif self.file_extension == '.json':
                print(f"正在從 JSON 檔案載入資料: {self.file_path}")
                return self._load_json()
            else:
                print(f"錯誤：不支援的檔案類型 '{self.file_extension}'")
                return None
        except FileNotFoundError:
            # 這個錯誤理論上在 __init__ 就會被捕捉，但為了穩健性再次檢查
            print(f"錯誤：檔案不存在 {self.file_path}")
            return None
        except json.JSONDecodeError:
            print(f"錯誤：解析 JSON 檔案失敗 {self.file_path}。請檢查檔案格式是否正確。")
            return None
        except Exception as e:
            print(f"載入檔案時發生未預期的錯誤: {e}")
            return None
