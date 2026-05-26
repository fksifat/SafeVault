"""Main Window for SafeVault"""

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QTabWidget,
    QSystemTrayIcon,
    QMenu,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon, QAction
from app.ui.dashboard import DashboardWidget
from app.ui.backup_jobs import BackupJobsWidget
from app.ui.restore import RestoreWidget
from app.ui.settings import SettingsWidget
from app.ui.style import get_app_stylesheet
from app.logs import get_logger

logger = get_logger()


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(
        self, db_manager=None, backup_manager=None, restore_manager=None, scheduler=None
    ):
        super().__init__()
        self.db = db_manager
        self.backup_manager = backup_manager
        self.restore_manager = restore_manager
        self.scheduler = scheduler

        self.setWindowTitle("SafeVault - Backup Tool")
        self.setGeometry(100, 100, 1200, 760)
        self.setMinimumSize(980, 640)
        theme = self.db.get_setting("theme", "Dark") if self.db else "Dark"
        self.setStyleSheet(get_app_stylesheet(theme))

        # Create central widget
        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(14, 12, 14, 14)
        layout.setSpacing(0)

        # Create tabs with manager references
        tabs = QTabWidget()
        tabs.setDocumentMode(True)
        tabs.addTab(
            DashboardWidget(db_manager=db_manager, backup_manager=backup_manager),
            "Dashboard",
        )
        tabs.addTab(
            BackupJobsWidget(db_manager=db_manager, backup_manager=backup_manager),
            "Backup Jobs",
        )
        tabs.addTab(
            RestoreWidget(db_manager=db_manager, restore_manager=restore_manager),
            "Restore",
        )
        tabs.addTab(SettingsWidget(db_manager=db_manager), "Settings")

        layout.addWidget(tabs)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Create system tray
        self.create_tray_icon()

        # Create menu bar
        self.create_menu_bar()

        logger.info("Main window initialized")

    def create_tray_icon(self):
        """Create system tray icon"""
        self.tray_icon = QSystemTrayIcon(self)

        # Create context menu
        tray_menu = QMenu(self)
        show_action = tray_menu.addAction("Show")
        show_action.triggered.connect(self.show)
        hide_action = tray_menu.addAction("Hide")
        hide_action.triggered.connect(self.hide)
        tray_menu.addSeparator()
        exit_action = tray_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        logger.info("System tray icon created")

    def create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        new_job = QAction("New Backup Job", self)
        new_job.triggered.connect(self.new_backup_job)
        file_menu.addAction(new_job)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Help menu
        help_menu = menubar.addMenu("Help")

        about = QAction("About SafeVault", self)
        about.triggered.connect(self.show_about)
        help_menu.addAction(about)

    def new_backup_job(self):
        """Create new backup job"""
        logger.info("New backup job requested")

    def show_about(self):
        """Show about dialog"""
        logger.info("About dialog requested")

    def changeEvent(self, event):
        """Handle window state change"""
        if event.type() == 105:  # WindowStateChange
            if self.windowState() & Qt.WindowMinimized:
                self.hide()
                event.ignore()
