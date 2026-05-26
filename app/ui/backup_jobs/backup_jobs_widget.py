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
    QDialog,
    QFileDialog,
    QSpinBox,
    QMessageBox,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


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

        # Title
        title = QLabel("Backup Jobs")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Job name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Job Name:"))
        self.name_input = QLineEdit()
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)

        # Source path
        source_layout = QHBoxLayout()
        source_layout.addWidget(QLabel("Source Path:"))
        self.source_input = QLineEdit()
        self.source_input.setReadOnly(True)
        source_layout.addWidget(self.source_input)
        source_btn = QPushButton("Browse")
        source_btn.clicked.connect(self.browse_source)
        source_layout.addWidget(source_btn)
        layout.addLayout(source_layout)

        # Destination path
        dest_layout = QHBoxLayout()
        dest_layout.addWidget(QLabel("Destination Path:"))
        self.dest_input = QLineEdit()
        self.dest_input.setReadOnly(True)
        dest_layout.addWidget(self.dest_input)
        dest_btn = QPushButton("Browse")
        dest_btn.clicked.connect(self.browse_destination)
        dest_layout.addWidget(dest_btn)
        layout.addLayout(dest_layout)

        # Schedule type
        schedule_layout = QHBoxLayout()
        schedule_layout.addWidget(QLabel("Schedule:"))
        self.schedule_combo = QComboBox()
        self.schedule_combo.addItems(["Manual", "Daily", "Weekly", "Monthly"])
        schedule_layout.addWidget(self.schedule_combo)
        layout.addLayout(schedule_layout)

        # Compression
        self.compression_check = QCheckBox("Enable Compression")
        layout.addWidget(self.compression_check)

        # Encryption
        self.encryption_check = QCheckBox("Enable Encryption")
        layout.addWidget(self.encryption_check)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        save_btn = QPushButton("Save Job")
        save_btn.clicked.connect(self.save_job)
        btn_layout.addWidget(save_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.cancel)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)
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
