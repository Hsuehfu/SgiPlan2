from PySide6.QtCore import QObject, Signal, Property, QAbstractListModel, Qt
from models import Session, Item

class ItemListModel(QAbstractListModel):
    def __init__(self, items=None):
        super().__init__()
        self.items = items or []

    def data(self, index, role):
        if role == Qt.DisplayRole:
            # Assuming the item object has a 'name' attribute
            return self.items[index.row()].name

    def rowCount(self, index):
        return len(self.items)

class MainViewModel(QObject):
    def __init__(self):
        super().__init__()
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
        db = Session()
        self._items.clear()
        # Query the database using SQLAlchemy
        db_items = db.query(Item).all()
        for item in db_items:
            self._items.append(item)
        db.close()
        
        self._item_list_model.beginResetModel()
        self._item_list_model.endResetModel()
        self.items_changed.emit()