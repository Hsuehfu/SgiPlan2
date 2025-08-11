
import sys
from PySide6.QtWidgets import QApplication
from views.main_window import MainWindow
from viewmodels.main_viewmodel import MainViewModel
from models import database, Base, engine

if __name__ == "__main__":
    # Create all tables in the database
    Base.metadata.create_all(bind=engine)

    app = QApplication(sys.argv)

    # Create the ViewModel
    viewmodel = MainViewModel()

    # Create the View and pass the ViewModel to it
    view = MainWindow(viewmodel)
    view.show()

    sys.exit(app.exec())
