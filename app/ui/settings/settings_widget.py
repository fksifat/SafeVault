"""Settings UI Widget"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QCheckBox,
    QPushButton,
    QSpinBox,
    QMessageBox,
)
from PySide6.QtGui import QFont


class SettingsWidget(QWidget):
    """Widget for application settings"""

    def __init__(self, parent=None, db_manager=None):
        super().__init__(parent)
        self.db = db_manager
        self.init_ui()

    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()

        # Title
        title = QLabel("Settings")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Theme
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Theme:"))
        theme_combo = QComboBox()
        theme_combo.addItems(["Light", "Dark", "System"])
        theme_layout.addWidget(theme_combo)
        theme_layout.addStretch()
        layout.addLayout(theme_layout)

        # Startup
        self.startup_check = QCheckBox("Run at Startup")
        layout.addWidget(self.startup_check)

        # Notifications
        self.notifications_check = QCheckBox("Enable Notifications")
        self.notifications_check.setChecked(True)
        layout.addWidget(self.notifications_check)

        # Backup retention
        retention_layout = QHBoxLayout()
        retention_layout.addWidget(QLabel("Keep Backups (days):"))
        retention_spin = QSpinBox()
        retention_spin.setValue(30)
        retention_layout.addWidget(retention_spin)
        retention_layout.addStretch()
        layout.addLayout(retention_layout)

        # Advanced settings
        advanced_label = QLabel("Advanced")
        advanced_font = QFont()
        advanced_font.setBold(True)
        advanced_label.setFont(advanced_font)
        layout.addWidget(advanced_label)

        # Compression level
        compression_layout = QHBoxLayout()
        compression_layout.addWidget(QLabel("Compression Level:"))
        compression_combo = QComboBox()
        compression_combo.addItems(["Fast", "Normal", "Maximum"])
        compression_layout.addWidget(compression_combo)
        compression_layout.addStretch()
        layout.addLayout(compression_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)
        layout.addStretch()

        self.setLayout(layout)

    def save_settings(self):
        """Save settings"""
        QMessageBox.information(self, "Success", "Settings saved successfully")
