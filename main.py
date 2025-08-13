import sys
import logging
from PySide6.QtWidgets import QApplication
from views.main_window import MainWindow
from viewmodels.main_viewmodel import MainViewModel
from models import database
from models.database import Base, engine, Session
from models.member_model import Member

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        filename='app.log',
                        filemode='w')

    logging.info("Application started.")

    # Create all tables in the database
    logging.info("Creating database tables if they don't exist.")
    Base.metadata.create_all(bind=engine)

    # Add sample data if the database is empty
    session = Session()
    if session.query(Member).count() == 0:
        logging.info("No members found, adding sample data.")
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
    logging.info("Initializing ViewModel.")
    viewmodel = MainViewModel()

    # Create the View and pass the ViewModel to it
    logging.info("Initializing View.")
    view = MainWindow(viewmodel)
    view.show()

    logging.info("Starting application event loop.")
    exit_code = app.exec()
    logging.info(f"Application finished with exit code {exit_code}.")
    sys.exit(exit_code)