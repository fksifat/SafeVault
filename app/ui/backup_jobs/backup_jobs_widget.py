"""Backup Jobs UI Widget"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QComboBox,
    QCheckBox,
    QFileDialog,
    QMessageBox,
    QFrame,
    QFormLayout,
)
from PySide6.QtCore import Qt


class BackupJobsWidget(QWidget):
    """Widget for managing backup jobs"""

    def __init__(self, parent=None, db_manager=None, backup_manager=None):
        super().__init__(parent)
        self.db = db_manager
        self.backup_manager = backup_manager
        self.init_ui()

    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(18, 18, 18, 14)
        layout.setSpacing(14)

        # Title
        title = QLabel("Backup Jobs")
        title.setObjectName("PageTitle")
        layout.addWidget(title)

        panel = QFrame()
        panel.setObjectName("Panel")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(18, 16, 18, 18)
        panel_layout.setSpacing(14)

        section_title = QLabel("Create Backup Job")
        section_title.setObjectName("SectionTitle")
        panel_layout.addWidget(section_title)

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFormAlignment(Qt.AlignTop)
        form_layout.setHorizontalSpacing(12)
        form_layout.setVerticalSpacing(10)

        # Job name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Example: Documents archive")
        form_layout.addRow("Job Name", self.name_input)

        # Source path
        source_layout = QHBoxLayout()
        source_layout.setSpacing(8)
        self.source_input = QLineEdit()
        self.source_input.setReadOnly(True)
        self.source_input.setPlaceholderText("Choose the folder you want to back up")
        source_layout.addWidget(self.source_input)
        source_btn = QPushButton("Browse")
        source_btn.clicked.connect(self.browse_source)
        source_layout.addWidget(source_btn)
        form_layout.addRow("Source Path", source_layout)

        # Destination path
        dest_layout = QHBoxLayout()
        dest_layout.setSpacing(8)
        self.dest_input = QLineEdit()
        self.dest_input.setReadOnly(True)
        self.dest_input.setPlaceholderText("Choose where backups should be stored")
        dest_layout.addWidget(self.dest_input)
        dest_btn = QPushButton("Browse")
        dest_btn.clicked.connect(self.browse_destination)
        dest_layout.addWidget(dest_btn)
        form_layout.addRow("Destination Path", dest_layout)

        # Schedule type
        self.schedule_combo = QComboBox()
        self.schedule_combo.addItems(["Manual", "Daily", "Weekly", "Monthly"])
        form_layout.addRow("Schedule", self.schedule_combo)

        panel_layout.addLayout(form_layout)

        # Compression
        options_layout = QHBoxLayout()
        options_layout.setSpacing(18)
        self.compression_check = QCheckBox("Enable Compression")
        options_layout.addWidget(self.compression_check)

        # Encryption
        self.encryption_check = QCheckBox("Enable Encryption")
        options_layout.addWidget(self.encryption_check)
        options_layout.addStretch()
        panel_layout.addLayout(options_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        save_btn = QPushButton("Save Job")
        save_btn.setObjectName("PrimaryButton")
        save_btn.clicked.connect(self.save_job)
        btn_layout.addWidget(save_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("QuietButton")
        cancel_btn.clicked.connect(self.cancel)
        btn_layout.addWidget(cancel_btn)

        panel_layout.addLayout(btn_layout)
        layout.addWidget(panel)

        helper_text = QLabel(
            "Manual jobs run when you click Run Now. Scheduled jobs are saved for automatic runs."
        )
        helper_text.setObjectName("MutedText")
        layout.addWidget(helper_text)
        layout.addStretch()

        self.setLayout(layout)

    def browse_source(self):
        """Browse source directory"""
        path = QFileDialog.getExistingDirectory(self, "Select Source Directory")
        if path:
            self.source_input.setText(path)

    def browse_destination(self):
        """Browse destination directory"""
        path = QFileDialog.getExistingDirectory(self, "Select Destination Directory")
        if path:
            self.dest_input.setText(path)

    def save_job(self):
        """Save backup job"""
        try:
            # Validate inputs
            name = self.name_input.text().strip()
            source = self.source_input.text().strip()
            destination = self.dest_input.text().strip()

            if not name:
                QMessageBox.warning(self, "Validation Error", "Please enter a job name")
                return

            if not source:
                QMessageBox.warning(
                    self, "Validation Error", "Please select a source path"
                )
                return

            if not destination:
                QMessageBox.warning(
                    self, "Validation Error", "Please select a destination path"
                )
                return

            # Get schedule and options
            schedule = self.schedule_combo.currentText().lower()
            compression = self.compression_check.isChecked()
            encryption = self.encryption_check.isChecked()

            # Create backup job
            if self.db:
                job_id = self.db.create_backup_job(
                    name=name,
                    source_path=source,
                    destination_path=destination,
                    schedule_type=schedule,
                    compression_enabled=compression,
                    encryption_enabled=encryption,
                )
                QMessageBox.information(
                    self,
                    "Success",
                    f'Backup job "{name}" created successfully (ID: {job_id})',
                )
                self.cancel()
            else:
                QMessageBox.critical(self, "Error", "Database manager not initialized")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save job: {str(e)}")

    def cancel(self):
        """Cancel job creation"""
        self.name_input.clear()
        self.source_input.clear()
        self.dest_input.clear()
        self.schedule_combo.setCurrentIndex(0)
        self.compression_check.setChecked(False)
        self.encryption_check.setChecked(False)
