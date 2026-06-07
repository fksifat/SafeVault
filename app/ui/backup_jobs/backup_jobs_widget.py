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

    def __init__(
        self, parent=None, db_manager=None, backup_manager=None, scheduler=None
    ):
        super().__init__(parent)
        self.db = db_manager
        self.backup_manager = backup_manager
        self.scheduler = scheduler
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

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Required when encryption is enabled")
        self.password_input.setEnabled(False)
        self.encryption_check.toggled.connect(self.password_input.setEnabled)
        form_layout.addRow("Encryption Password", self.password_input)

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
        # Manage existing jobs (delete / refresh)
        manage_frame = QFrame()
        manage_frame.setObjectName("Panel")
        manage_layout = QHBoxLayout(manage_frame)
        manage_layout.setContentsMargins(8, 8, 8, 8)
        manage_layout.setSpacing(12)

        self.job_select = QComboBox()
        self.job_select.setMinimumWidth(320)
        manage_layout.addWidget(self.job_select)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setObjectName("QuietButton")
        refresh_btn.clicked.connect(self.load_jobs)
        manage_layout.addWidget(refresh_btn)

        delete_btn = QPushButton("Delete Job")
        delete_btn.setObjectName("DangerButton")
        delete_btn.clicked.connect(self.delete_selected_job)
        manage_layout.addWidget(delete_btn)

        layout.addWidget(manage_frame)
        self.load_jobs()
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
            encryption_password = self.password_input.text()

            if encryption and not encryption_password:
                QMessageBox.warning(
                    self,
                    "Validation Error",
                    "Please enter an encryption password",
                )
                return

            # Create backup job
            if self.db:
                job_id = self.db.create_backup_job(
                    name=name,
                    source_path=source,
                    destination_path=destination,
                    schedule_type=schedule,
                    compression_enabled=compression,
                    encryption_enabled=encryption,
                    encryption_password=encryption_password if encryption else None,
                )
                if self.scheduler and schedule != "manual":
                    self.scheduler.schedule_job(job_id, name, schedule)
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
        self.password_input.clear()
        self.password_input.setEnabled(False)

    def load_jobs(self):
        """Load jobs into the job selector"""
        if not self.db:
            self.job_select.clear()
            self.job_select.addItem("Database not initialized")
            self.job_select.setEnabled(False)
            return

        try:
            jobs = self.db.get_all_backup_jobs()
            self.job_select.clear()
            for job in jobs:
                label = f"{job.get('id')} - {job.get('name')}"
                self.job_select.addItem(label, job.get("id"))
            self.job_select.setEnabled(len(jobs) > 0)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load jobs: {e}")

    def delete_selected_job(self):
        """Delete the selected backup job after confirmation"""
        if not self.db:
            QMessageBox.critical(self, "Error", "Database manager not initialized")
            return

        idx = self.job_select.currentIndex()
        if idx < 0:
            QMessageBox.information(self, "Info", "No job selected to delete")
            return

        job_id = self.job_select.itemData(idx)
        job_label = self.job_select.currentText()

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete backup job '{job_label}'? This will remove the job and its history.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        try:
            # Unschedule if scheduler available
            if self.scheduler:
                try:
                    self.scheduler.unschedule_job(job_id)
                except Exception:
                    # Non-fatal if unschedule fails
                    pass

            self.db.delete_backup_job(job_id)
            QMessageBox.information(
                self, "Deleted", f"Backup job '{job_label}' deleted"
            )
            self.load_jobs()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete job: {e}")
