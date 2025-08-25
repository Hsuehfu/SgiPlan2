import pandas as pd
from sqlalchemy.orm import sessionmaker
from models.member_model import Member
from models.member_position_model import MemberPosition
from collections import namedtuple

from repositories.region_repository import RegionRepository
from repositories.position_repository import PositionRepository
from repositories.member_repository import MemberRepository
from repositories.member_position_repository import MemberPositionRepository

RowResult = namedtuple('RowResult', ['row_index', 'status', 'message'])

class MemberImporter:
    """
    負責從 Excel 檔案匯入會員資料到資料庫的核心服務。
    """
    def __init__(self, session_factory: sessionmaker):
        self.Session = session_factory

    def preview_excel(self, file_path: str) -> pd.DataFrame:
        """僅讀取 Excel 檔案並返回 DataFrame 以供預覽。"""
        try:
            df = pd.read_excel(file_path)
            df.columns = [col.strip() for col in df.columns]
            return df.astype(str).fillna('')
        except Exception as e:
            raise ValueError(f"讀取或解析 Excel 檔案失敗: {e}")

    def run_import(self, dataframe: pd.DataFrame):
        """
        執行匯入程序，這是一個 generator，會逐筆回報進度。
        """
        with self.Session() as session:
            # Repositories
            region_repo = RegionRepository(session)
            position_repo = PositionRepository(session)
            member_repo = MemberRepository(session)
            member_position_repo = MemberPositionRepository(session)

            # Pre-caching
            existing_regions = {r.name: r.id for r in region_repo.get_all()}
            existing_positions = {p.name: p.id for p in position_repo.get_all()}
            existing_members = {m.name: m for m in member_repo.get_all()}

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
                        member_repo.add(member)
                        session.flush() # Flush to get ID for new member
                        existing_members[name] = member

                    existing_assignment = member_position_repo.find_by_member_and_position(
                        member_id=member.id, position_id=position_id)

                    if not existing_assignment:
                        has_primary = member_position_repo.has_primary_position(member.id)
                        new_assignment = MemberPosition(
                            member_id=member.id,
                            position_id=position_id,
                            is_primary=not has_primary
                        )
                        member_position_repo.add(new_assignment)
                    
                    session.commit()
                    yield RowResult(index, "success", "匯入成功")

                except Exception as e:
                    session.rollback()
                    yield RowResult(index, "failure", str(e))


