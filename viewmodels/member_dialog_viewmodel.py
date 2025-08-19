# viewmodels/member_dialog_viewmodel.py

from PySide6.QtCore import QObject, Signal
from models.region_model import Region
from models.member_model import Member
# [移除] 不再需要從這裡匯入 Session，因為它將被傳入

# viewmodels/member_dialog_viewmodel.py

from PySide6.QtCore import QObject, Signal
from models.region_model import Region
from models.member_model import Member
# [移除] 不再需要從這裡匯入 Session，因為它將被傳入

class MemberDialogViewModel(QObject):
    regions_loaded = Signal(list)
    # [新增] 增加一個儲存成功後發射的訊號，通知主視窗更新
    saved_successfully = Signal()

    # [修改] __init__ 方法，接收 db_session
    def __init__(self, db_session, member_data=None, parent=None):
        super().__init__(parent)
        self.session = db_session  # 持有傳入的共享 Session
        self._member_data = member_data  # 僅用於判斷是新增還是編輯

        # [新增] ViewModel 的內部狀態變數，解決 setter 問題
        if self._member_data: # 編輯模式：從傳入的物件初始化狀態
            self._name = self._member_data.name
            self._phone_number = self._member_data.phone_number
            self._is_schedulable = bool(self._member_data.is_schedulable)
            self._region_id = self._member_data.region_id
        else: # 新增模式：初始化為空狀態
            self._name = ""
            self._phone_number = ""
            self._is_schedulable = True
            self._region_id = None

    # [修改] property 的 getter 和 setter，改為操作內部狀態變數
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value # 無論新增或編輯，都直接更新內部狀態

    @property
    def phone_number(self):
        return self._phone_number

    @phone_number.setter
    def phone_number(self, value):
        self._phone_number = value

    @property
    def is_schedulable(self):
        return self._is_schedulable

    @is_schedulable.setter
    def is_schedulable(self, value):
        self._is_schedulable = value

    @property
    def region_id(self):
        return self._region_id

    @region_id.setter
    def region_id(self, value):
        self._region_id = value

    def load_regions(self):
        """使用共享的 session 載入地區資料。"""
        print("MemberDialogViewModel: load_regions called.")
        try:
            # [修改] 使用 self.session，不再自己建立和關閉
            regions = self.session.query(Region).order_by(Region.id).all()
            region_data = [(region.id, region.name) for region in regions]
            print(f"MemberDialogViewModel: Loaded {len(region_data)} regions.")
            self.regions_loaded.emit(region_data)
        except Exception as e:
            print(f"MemberDialogViewModel: Error loading regions: {e}")
            self.regions_loaded.emit([])
        # [修改] 不再需要 finally 和 session.close()，由外部統一管理

    def save(self):
        """使用共享的 session 和內部狀態來儲存資料。"""
        try:
            if self.is_editing():  # 編輯模式
                # 直接使用 self._member_data 物件，因為它已經附加在共享 session 中
                self._member_data.name = self._name
                self._member_data.phone_number = self._phone_number
                self._member_data.is_schedulable = self._is_schedulable
                self._member_data.region_id = self._region_id
            else:  # 新增模式
                new_member = Member(
                    name=self._name,
                    phone_number=self._phone_number,
                    is_schedulable=self._is_schedulable,
                    region_id=self._region_id
                )
                self.session.add(new_member)
            
            self.session.commit()
            print("MemberDialogViewModel: Data saved successfully.")
            self.saved_successfully.emit() # [新增] 發射成功訊號
            
        except Exception as e:
            print(f"Error saving member data: {e}")
            self.session.rollback()
        # [修改] 不再需要 finally 和 session.close()，由外部統一管理

    def is_editing(self) -> bool:
        """判斷當前是否為編輯模式。"""
        return self._member_data is not None