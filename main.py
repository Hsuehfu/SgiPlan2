
import sys
from PySide6.QtWidgets import QApplication
from views.main_window import MainWindow
from viewmodels.main_viewmodel import MainViewModel
from models import database
from models.database import Base, engine, Session
from models.member_model import Member

if __name__ == "__main__":
    # Create all tables in the database
    Base.metadata.create_all(bind=engine)

    # Add sample data if the database is empty
    session = Session()
    if session.query(Member).count() == 0:
        sample_members = [
            Member(name="張三"),
            Member(name="李四"),
            Member(name="王五"),
        ]
        session.add_all(sample_members)
        session.commit()
    session.close()

    app = QApplication(sys.argv)

    # Create the ViewModel
    viewmodel = MainViewModel()

    # Create the View and pass the ViewModel to it
    view = MainWindow(viewmodel)
    view.show()

    sys.exit(app.exec())
