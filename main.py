import sys
import logging
from PySide6.QtWidgets import QApplication

import logging_config
from views.main_window import MainWindow
from viewmodels.main_viewmodel import MainViewModel
from models import Base, engine, Session, Member, Department

if __name__ == "__main__":    
    logging_config.setup_logging()
    logger = logging.getLogger(__name__)

    # Initialize the database
    logger.info("Application started.")
    logger.debug("Initializing database.")

    # Create all tables in the database
    logger.info("Creating database tables if they don't exist.")
    Base.metadata.create_all(bind=engine)

    # Create a single session for the application lifetime
    db_session = Session()

    try:
        # Seed departments if they don't exist
        if db_session.query(Department).count() == 0:
            logger.info("No departments found, seeding initial data.")
            departments = [
                Department(name="壯年部"),
                Department(name="婦人部"),
                Department(name="男子部"),
                Department(name="女子部"),
            ]
            db_session.add_all(departments)
            db_session.flush() # Explicitly flush before commit
            db_session.commit()
            logger.info("Departments seeded successfully.")
        else:
            logger.info("Departments already exist, skipping seeding.")

        # Add sample data if the database is empty
        if db_session.query(Member).count() == 0:
            logger.info("No members found, adding sample data.")
            sample_members = [
                Member(name="張三"),
                Member(name="李四"),
                Member(name="王五"),
            ]
            db_session.add_all(sample_members)
            db_session.flush() # Explicitly flush before commit
            db_session.commit()
            logger.info("Sample members seeded successfully.")
        else:
            logger.info("Members already exist, skipping seeding.")

        app = QApplication(sys.argv)

        # Create the ViewModel and pass the shared session
        logger.info("Initializing ViewModel.")
        viewmodel = MainViewModel(db_session)

        # Create the View and pass the ViewModel to it
        logger.info("Initializing View.")
        view = MainWindow(viewmodel)
        view.show()

        logger.info("Starting application event loop.")
        exit_code = app.exec()
        logger.info(f"Application finished with exit code {exit_code}.")
        sys.exit(exit_code)
    finally:
        # Ensure the session is closed when the application exits
        db_session.close()