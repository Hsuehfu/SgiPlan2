import pandas as pd
from sqlalchemy.orm import sessionmaker
from models.member_model import Member
from models.position_model import Position
from models.region_model import Region
from models.member_position_model import MemberPosition
from collections import namedtuple

# 定義一個簡單的資料結構來回傳每一列的處理結果
RowResult = namedtuple('RowResult', ['row_index', 'status', 'message'])

class MemberImporter:
    """
    負責從 Excel 檔案匯入會員資料到資料庫的核心服務。
    這個版本支援預覽和進度回報。
    """
    def __init__(self, session_factory: sessionmaker):
        self.Session = session_factory

    def preview_excel(self, file_path: str) -> pd.DataFrame:
        """僅讀取 Excel 檔案並返回 DataFrame 以供預覽。"""
        try:
            df = pd.read_excel(file_path)
            df.columns = [col.strip() for col in df.columns]
            # 將所有資料轉為字串以方便顯示，並填充 NaN
            return df.astype(str).fillna('')
        except Exception as e:
            raise ValueError(f"讀取或解析 Excel 檔案失敗: {e}")

    def run_import(self, dataframe: pd.DataFrame):
        """
        執行匯入程序，這是一個 generator，會逐筆回報進度。

        Args:
            dataframe (pd.DataFrame): 從預覽步驟得到的 DataFrame。

        Yields:
            RowResult: 每一列資料的處理結果。
        """
        with self.Session() as session:
            # 預先載入快取
            existing_regions = {r.name: r.id for r in session.query(Region).all()}
            existing_positions = {p.name: p.id for p in session.query(Position).all()}
            existing_members = {m.name: m for m in session.query(Member).all()}

            for index, row in dataframe.iterrows():
                try:
                    name = str(row.get('姓名', '')).strip()
                    region_name = str(row.get('地區', '')).strip()
                    position_name = str(row.get('職務', '')).strip()
                    phone = str(row.get('電話', '')).strip()

                    if not name or not region_name or not position_name:
                        raise ValueError("姓名、地區、職務為必填欄位。")

                    if region_name not in existing_regions:
                        raise ValueError(f"地區 '{region_name}' 不存在。")
                    region_id = existing_regions[region_name]

                    if position_name not in existing_positions:
                        raise ValueError(f"職務 '{position_name}' 不存在。")
                    position_id = existing_positions[position_name]

                    member = existing_members.get(name)
                    if member:
                        member.phone_number = phone if phone else member.phone_number
                        member.region_id = region_id
                    else:
                        member = Member(name=name, phone_number=phone, region_id=region_id)
                        session.add(member)
                        session.flush()
                        existing_members[name] = member

                    existing_assignment = session.query(MemberPosition).filter_by(
                        member_id=member.id, position_id=position_id).first()

                    if not existing_assignment:
                        has_primary = session.query(MemberPosition).filter_by(
                            member_id=member.id, is_primary=1).count() > 0
                        new_assignment = MemberPosition(
                            member_id=member.id,
                            position_id=position_id,
                            is_primary=0 if has_primary else 1
                        )
                        session.add(new_assignment)
                    
                    session.commit() # 逐筆提交
                    yield RowResult(index, "success", "匯入成功")

                except Exception as e:
                    session.rollback() # 單筆錯誤則回滾
                    yield RowResult(index, "failure", str(e))

