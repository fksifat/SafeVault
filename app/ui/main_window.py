"""Main Window for SafeVault"""

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QSystemTrayIcon,
    QMenu,
    QLabel,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QAction, QPixmap, QImage
from pathlib import Path
from app.ui.dashboard import DashboardWidget
from app.ui.backup_jobs import BackupJobsWidget
from app.ui.restore import RestoreWidget
from app.ui.settings import SettingsWidget
from app.ui.style import get_app_stylesheet
from app.logs import get_logger

logger = get_logger()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOGO_PNG = PROJECT_ROOT / "logo" / "logo.png"
LOGO_ICO = PROJECT_ROOT / "logo" / "logo.ico"


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
        self.app_icon = self._load_app_icon()
        if not self.app_icon.isNull():
            self.setWindowIcon(self.app_icon)
        theme = self.db.get_setting("theme", "Dark") if self.db else "Dark"
        self.setStyleSheet(get_app_stylesheet(theme))

        # Create central widget
        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(14, 12, 14, 14)
        layout.setSpacing(12)

        header = self.create_header()
        layout.addLayout(header)

        # Create tabs with manager references
        tabs = QTabWidget()
        tabs.setDocumentMode(True)
        tabs.addTab(
            DashboardWidget(db_manager=db_manager, backup_manager=backup_manager),
            "Dashboard",
        )
        tabs.addTab(
            BackupJobsWidget(
                db_manager=db_manager,
                backup_manager=backup_manager,
                scheduler=scheduler,
            ),
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

    def _load_app_icon(self):
        """Load the application icon from the logo folder."""
        if LOGO_ICO.exists():
            return QIcon(str(LOGO_ICO))
        if LOGO_PNG.exists():
            return QIcon(str(LOGO_PNG))
        return QIcon()

    def create_header(self):
        """Create the branded application header."""
        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(10)

        logo_label = QLabel()
        logo_label.setObjectName("AppLogo")
        logo_label.setFixedSize(40, 40)
        if LOGO_PNG.exists():
            pixmap = QPixmap(str(LOGO_PNG))
            pixmap = self._crop_transparent_padding(pixmap)
            logo_label.setPixmap(
                pixmap.scaled(
                    40,
                    40,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
            )
        header.addWidget(logo_label)

        title_group = QVBoxLayout()
        title_group.setContentsMargins(0, 0, 0, 0)
        title_group.setSpacing(1)

        app_name = QLabel("SafeVault")
        app_name.setObjectName("AppName")
        subtitle = QLabel("Storage Backup System")
        subtitle.setObjectName("MutedText")
        title_group.addWidget(app_name)
        title_group.addWidget(subtitle)
        header.addLayout(title_group)
        header.addStretch()

        return header

    def _crop_transparent_padding(self, pixmap):
        """Crop transparent padding so logo assets scale visually."""
        image = pixmap.toImage().convertToFormat(QImage.Format_ARGB32)
        bounds = None

        for y in range(image.height()):
            for x in range(image.width()):
                if image.pixelColor(x, y).alpha() > 0:
                    if bounds is None:
                        bounds = [x, y, x, y]
                    else:
                        bounds[0] = min(bounds[0], x)
                        bounds[1] = min(bounds[1], y)
                        bounds[2] = max(bounds[2], x)
                        bounds[3] = max(bounds[3], y)

        if bounds is None:
            return pixmap

        x1, y1, x2, y2 = bounds
        return pixmap.copy(x1, y1, x2 - x1 + 1, y2 - y1 + 1)

    def create_tray_icon(self):
        """Create system tray icon"""
        self.tray_icon = QSystemTrayIcon(self)
        if not self.app_icon.isNull():
            self.tray_icon.setIcon(self.app_icon)

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
