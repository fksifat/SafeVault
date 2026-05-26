"""SafeVault - Cross-platform Backup Application
Main entry point for the application
"""

import sys
from pathlib import Path

# Add app directory to path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir.parent))

from PySide6.QtWidgets import QApplication
from app.logs import setup_logger
from app.database import DatabaseManager
from app.backup_engine import BackupManager
from app.scheduler import BackupScheduler
from app.restore_engine import RestoreManager
from app.ui import MainWindow


def main():
    """Main entry point"""
    # Setup logger
    logger = setup_logger()
    logger.info("Starting SafeVault")

    # Create application
    app = QApplication(sys.argv)

    # Initialize core components
    db_manager = DatabaseManager()
    backup_manager = BackupManager(db_manager)
    scheduler = BackupScheduler(db_manager, backup_manager)
    restore_manager = RestoreManager(db_manager)

    # Start scheduler
    scheduler.start()

    # Create and show main window
    window = MainWindow(
        db_manager=db_manager,
        backup_manager=backup_manager,
        restore_manager=restore_manager,
        scheduler=scheduler,
    )
    window.show()

    logger.info("Application started successfully")

    try:
        sys.exit(app.exec())
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
        scheduler.stop()
        sys.exit(0)


if __name__ == "__main__":
    main()
