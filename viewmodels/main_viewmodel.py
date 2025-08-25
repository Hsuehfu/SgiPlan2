from PySide6.QtCore import QObject, Signal, Property, QAbstractListModel, Qt
from repositories.item_repository import ItemRepository

class ItemListModel(QAbstractListModel):
    def __init__(self, items=None):
        super().__init__()
        self.items = items or []

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self.items[index.row()].name

    def rowCount(self, index):
        return len(self.items)

class MainViewModel(QObject):
    def __init__(self, db_session):
        super().__init__()
        self.session = db_session
        self.item_repo = ItemRepository(db_session)
        self._items = []
        self._item_list_model = ItemListModel(self._items)
        self.load_items()

    @Signal
    def items_changed(self):
        pass

    def get_items(self):
        return self._item_list_model

    items = Property(QObject, fget=get_items, notify=items_changed)

    def load_items(self):
        self._items.clear()
        db_items = self.item_repo.get_all()
        for item in db_items:
            self._items.append(item)
        
        self._item_list_model.beginResetModel()
        self._item_list_model.endResetModel()
        self.items_changed.emit()