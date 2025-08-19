import sys
import logging
from PySide6.QtWidgets import QApplication

import logging_config
from views.main_window import MainWindow
from viewmodels.main_viewmodel import MainViewModel
from models.database import Base, engine, Session
from models.member_model import Member

if __name__ == "__main__":    
    logging_config.setup_logging()
    logger = logging.getLogger(__name__)

    # Initialize the database
    logging.info("Application started.")
    logging.debug("Initializing database.")

    # Create all tables in the database
    logging.info("Creating database tables if they don't exist.")
    Base.metadata.create_all(bind=engine)

    # Create a single session for the application lifetime
    db_session = Session()

    try:
        # Add sample data if the database is empty
        if db_session.query(Member).count() == 0:
            logging.info("No members found, adding sample data.")
            sample_members = [
                Member(name="張三"),
                Member(name="李四"),
                Member(name="王五"),
            ]
            db_session.add_all(sample_members)
            db_session.commit()

        app = QApplication(sys.argv)

        # Create the ViewModel and pass the shared session
        logging.info("Initializing ViewModel.")
        viewmodel = MainViewModel(db_session)

        # Create the View and pass the ViewModel to it
        logging.info("Initializing View.")
        view = MainWindow(viewmodel)
        view.show()

        logging.info("Starting application event loop.")
        exit_code = app.exec()
        logging.info(f"Application finished with exit code {exit_code}.")
        sys.exit(exit_code)
    finally:
        # Ensure the session is closed when the application exits
        db_session.close()