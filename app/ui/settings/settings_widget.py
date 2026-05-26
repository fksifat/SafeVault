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
    QFrame,
    QFormLayout,
)
from PySide6.QtCore import Qt
from app.ui.style import get_app_stylesheet


class SettingsWidget(QWidget):
    """Widget for application settings"""

    def __init__(self, parent=None, db_manager=None):
        super().__init__(parent)
        self.db = db_manager
        self.init_ui()

    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(18, 18, 18, 14)
        layout.setSpacing(14)

        # Title
        title = QLabel("Settings")
        title.setObjectName("PageTitle")
        layout.addWidget(title)

        panel = QFrame()
        panel.setObjectName("Panel")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(18, 16, 18, 18)
        panel_layout.setSpacing(16)

        general_label = QLabel("General")
        general_label.setObjectName("SectionTitle")
        panel_layout.addWidget(general_label)

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setHorizontalSpacing(12)
        form_layout.setVerticalSpacing(10)

        # Theme
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light", "System"])
        self.theme_combo.setMaximumWidth(320)
        self.theme_combo.currentTextChanged.connect(self.apply_theme)
        form_layout.addRow("Theme", self.theme_combo)

        # Startup
        self.startup_check = QCheckBox("Run at Startup")
        form_layout.addRow("", self.startup_check)

        # Notifications
        self.notifications_check = QCheckBox("Enable Notifications")
        self.notifications_check.setChecked(True)
        form_layout.addRow("", self.notifications_check)

        # Backup retention
        retention_layout = QHBoxLayout()
        retention_layout.setSpacing(8)
        self.retention_spin = QSpinBox()
        self.retention_spin.setRange(1, 999)
        self.retention_spin.setValue(30)
        self.retention_spin.setMaximumWidth(160)
        retention_layout.addWidget(self.retention_spin)
        self.retention_unit_combo = QComboBox()
        self.retention_unit_combo.addItems(["Day", "Week", "Month", "Year"])
        self.retention_unit_combo.setMaximumWidth(160)
        retention_layout.addWidget(self.retention_unit_combo)
        retention_layout.addStretch()
        form_layout.addRow("Keep Backups", retention_layout)

        panel_layout.addLayout(form_layout)

        # Advanced settings
        advanced_label = QLabel("Advanced")
        advanced_label.setObjectName("SectionTitle")
        panel_layout.addWidget(advanced_label)

        # Compression level
        advanced_form = QFormLayout()
        advanced_form.setLabelAlignment(Qt.AlignRight)
        advanced_form.setHorizontalSpacing(12)
        advanced_form.setVerticalSpacing(10)
        self.compression_combo = QComboBox()
        self.compression_combo.addItems(["Fast", "Normal", "Maximum"])
        self.compression_combo.setMaximumWidth(320)
        advanced_form.addRow("Compression Level", self.compression_combo)
        panel_layout.addLayout(advanced_form)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        save_btn = QPushButton("Save Settings")
        save_btn.setObjectName("PrimaryButton")
        save_btn.clicked.connect(self.save_settings)
        btn_layout.addWidget(save_btn)

        panel_layout.addLayout(btn_layout)
        layout.addWidget(panel)

        helper = QLabel("Settings are stored locally for this backup workstation.")
        helper.setObjectName("MutedText")
        layout.addWidget(helper)
        layout.addStretch()

        self.setLayout(layout)
        self.load_settings()

    def load_settings(self):
        """Load saved settings into controls."""
        if not self.db:
            return

        theme = self.db.get_setting("theme", "Dark")
        theme_index = self.theme_combo.findText(theme)
        if theme_index >= 0:
            self.theme_combo.setCurrentIndex(theme_index)

        self.startup_check.setChecked(self.db.get_setting("run_at_startup", "false") == "true")
        self.notifications_check.setChecked(
            self.db.get_setting("enable_notifications", "true") == "true"
        )
        self.retention_spin.setValue(int(self.db.get_setting("retention_value", "30")))
        unit = self.db.get_setting("retention_unit", "Day")
        unit_index = self.retention_unit_combo.findText(unit)
        if unit_index >= 0:
            self.retention_unit_combo.setCurrentIndex(unit_index)

        compression = self.db.get_setting("compression_level", "Fast")
        compression_index = self.compression_combo.findText(compression)
        if compression_index >= 0:
            self.compression_combo.setCurrentIndex(compression_index)

    def apply_theme(self, theme: str):
        """Apply selected theme to the current window immediately."""
        window = self.window()
        if window:
            window.setStyleSheet(get_app_stylesheet(theme))

    def save_settings(self):
        """Save settings"""
        if self.db:
            self.db.set_setting("theme", self.theme_combo.currentText())
            self.db.set_setting(
                "run_at_startup", str(self.startup_check.isChecked()).lower()
            )
            self.db.set_setting(
                "enable_notifications",
                str(self.notifications_check.isChecked()).lower(),
            )
            self.db.set_setting("retention_value", str(self.retention_spin.value()))
            self.db.set_setting("retention_unit", self.retention_unit_combo.currentText())
            self.db.set_setting("compression_level", self.compression_combo.currentText())

        self.apply_theme(self.theme_combo.currentText())
        QMessageBox.information(self, "Success", "Settings saved successfully")
