"""Dashboard UI Widget"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QFrame,
    QHeaderView,
    QAbstractItemView,
    QInputDialog,
    QLineEdit,
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont
from app.utils import format_file_size


class BackupWorker(QThread):
    """Run a backup without blocking the Qt UI thread."""

    backup_finished = Signal(int, str, dict)
    backup_failed = Signal(int, str, str)

    def __init__(self, backup_manager, job: dict):
        super().__init__()
        self.backup_manager = backup_manager
        self.job = job

    def run(self):
        try:
            history = self.backup_manager.db.get_backup_history(self.job["id"])
            if history:
                result = self.backup_manager.perform_incremental_backup(
                    self.job["id"],
                    self.job["source_path"],
                    self.job["destination_path"],
                    self.job,
                )
            else:
                result = self.backup_manager.perform_full_backup(
                    self.job["id"],
                    self.job["source_path"],
                    self.job["destination_path"],
                    self.job,
                )
            self.backup_finished.emit(self.job["id"], self.job["name"], result)
        except Exception as e:
            self.backup_failed.emit(self.job["id"], self.job["name"], str(e))


class DashboardWidget(QWidget):
    """Dashboard showing backup status and statistics"""

    def __init__(self, parent=None, db_manager=None, backup_manager=None):
        super().__init__(parent)
        self.db = db_manager
        self.backup_manager = backup_manager
        self.backup_workers = {}
        self.init_ui()

    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(18, 18, 18, 14)
        layout.setSpacing(14)

        # Title
        title = QLabel("Backup Dashboard")
        title.setObjectName("PageTitle")
        layout.addWidget(title)

        # Stats section
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(12)

        # Active backups
        self.active_label = QLabel("0")
        active_box = self._create_stat_box(
            "Active Jobs", self.active_label, "Jobs configured for local backup"
        )
        stats_layout.addWidget(active_box)

        # Last backup
        self.last_backup_label = QLabel("Never")
        last_backup_box = self._create_stat_box(
            "Last Backup", self.last_backup_label, "Most recent completed run"
        )
        stats_layout.addWidget(last_backup_box)

        # Total backed up
        self.total_label = QLabel("0 GB")
        total_box = self._create_stat_box(
            "Total Backed Up", self.total_label, "Total size recorded in history"
        )
        stats_layout.addWidget(total_box)

        layout.addLayout(stats_layout)

        # Backup jobs table
        table_panel = QFrame()
        table_panel.setObjectName("Panel")
        table_layout = QVBoxLayout(table_panel)
        table_layout.setContentsMargins(14, 14, 14, 14)
        table_layout.setSpacing(10)

        table_header = QHBoxLayout()
        job_label = QLabel("Backup Jobs")
        job_label.setObjectName("SectionTitle")
        table_header.addWidget(job_label)
        table_header.addStretch()

        new_job_btn = QPushButton("New Backup Job")
        new_job_btn.setObjectName("PrimaryButton")
        new_job_btn.clicked.connect(self.on_new_job)
        table_header.addWidget(new_job_btn)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_jobs)
        table_header.addWidget(refresh_btn)
        table_layout.addLayout(table_header)

        self.jobs_table = QTableWidget()
        self.jobs_table.setColumnCount(5)
        self.jobs_table.setHorizontalHeaderLabels(
            ["Job Name", "Status", "Last Run", "Next Run", "Actions"]
        )
        self.jobs_table.setAlternatingRowColors(True)
        self.jobs_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.jobs_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.jobs_table.verticalHeader().setVisible(False)
        self.jobs_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.jobs_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.jobs_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.jobs_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.jobs_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        self.jobs_table.setColumnWidth(4, 132)
        table_layout.addWidget(self.jobs_table)

        self.empty_label = QLabel("No backup jobs yet. Create one to start protecting a folder.")
        self.empty_label.setObjectName("MutedText")
        self.empty_label.setAlignment(Qt.AlignCenter)
        table_layout.addWidget(self.empty_label)

        layout.addWidget(table_panel, 1)
        self.setLayout(layout)

        # Refresh on load
        self.refresh_jobs()

    def _create_stat_box(self, label: str, value_widget, caption: str) -> QWidget:
        """Create a stat box widget"""
        box = QFrame()
        box.setObjectName("StatCard")
        box_layout = QVBoxLayout()
        box_layout.setContentsMargins(16, 14, 16, 14)
        box_layout.setSpacing(4)

        label_widget = QLabel(label)
        label_widget.setObjectName("MutedText")

        if isinstance(value_widget, str):
            value_label = QLabel(value_widget)
        else:
            value_label = value_widget

        value_label.setObjectName("StatValue")

        caption_label = QLabel(caption)
        caption_label.setObjectName("MutedText")

        box_layout.addWidget(label_widget)
        box_layout.addWidget(value_label)
        box_layout.addWidget(caption_label)
        box.setLayout(box_layout)

        return box

    def refresh_jobs(self):
        """Refresh the jobs table with data from database"""
        try:
            if not self.db:
                return

            # Clear table
            self.jobs_table.setRowCount(0)

            # Get all jobs
            jobs = self.db.get_all_backup_jobs()
            total_size = 0
            last_backup = None

            # Update stats
            self.active_label.setText(str(len(jobs)))

            # Add jobs to table
            for job in jobs:
                row = self.jobs_table.rowCount()
                self.jobs_table.insertRow(row)

                # Job name
                self.jobs_table.setItem(row, 0, QTableWidgetItem(job["name"]))

                # Status
                history = self.db.get_backup_history(job["id"])
                if history:
                    status = history[0]["status"]
                    last_run = history[0]["backup_time"]
                    if last_backup is None or str(last_run) > str(last_backup):
                        last_backup = last_run
                    total_size += sum(h.get("backup_size") or 0 for h in history)
                else:
                    status = "Never"
                    last_run = "-"

                self.jobs_table.setItem(row, 1, QTableWidgetItem(status))
                self.jobs_table.setItem(
                    row,
                    2,
                    QTableWidgetItem(str(last_run)[:19] if last_run != "-" else "-"),
                )
                self.jobs_table.setItem(
                    row, 3, QTableWidgetItem(job["schedule_type"].capitalize())
                )

                # Actions button
                run_btn = QPushButton("Run Now")
                run_btn.setObjectName("PrimaryButton")
                run_btn.setMinimumWidth(96)
                run_btn.clicked.connect(
                    lambda checked, jid=job["id"], jname=job["name"]: self.run_backup(
                        jid, jname
                    )
                )
                self.jobs_table.setCellWidget(row, 4, run_btn)
                self.jobs_table.setRowHeight(row, 46)

            self.last_backup_label.setText(str(last_backup)[:10] if last_backup else "Never")
            self.total_label.setText(format_file_size(total_size))
            self.empty_label.setVisible(len(jobs) == 0)
            self.jobs_table.setVisible(len(jobs) > 0)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to refresh jobs: {str(e)}")

    def run_backup(self, job_id: int, job_name: str):
        """Run a backup job"""
        try:
            if not self.db or not self.backup_manager:
                QMessageBox.critical(self, "Error", "Backup manager not initialized")
                return

            job = self.db.get_backup_job(job_id)
            if not job:
                QMessageBox.critical(self, "Error", "Job not found")
                return

            if job.get("encryption_enabled") and not job.get("encryption_password"):
                password, ok = QInputDialog.getText(
                    self,
                    "Encryption Password",
                    f'Enter the encryption password for "{job_name}":',
                    QLineEdit.Password,
                )
                if not ok:
                    return
                if not password:
                    QMessageBox.warning(
                        self,
                        "Encryption Password Required",
                        "This job cannot run encrypted without a password.",
                    )
                    return
                self.db.update_backup_job(job_id, encryption_password=password)
                job["encryption_password"] = password

            worker = BackupWorker(self.backup_manager, job)
            worker.backup_finished.connect(self.on_backup_finished)
            worker.backup_failed.connect(self.on_backup_failed)
            worker.finished.connect(lambda jid=job_id: self.backup_workers.pop(jid, None))
            self.backup_workers[job_id] = worker

            sender = self.sender()
            if sender:
                sender.setEnabled(False)
                sender.setText("Running...")
            worker.finished.connect(self.refresh_jobs)
            worker.start()

        except Exception as e:
            QMessageBox.critical(self, "Backup Error", f"Backup failed: {str(e)}")

    def on_backup_finished(self, job_id: int, job_name: str, result: dict):
        """Record and report a completed worker backup."""
        errors = result.get("errors") or []
        error_message = result.get("error") or "\n".join(errors) or None
        self.db.record_backup_history(
            job_id,
            result.get("status", "failed"),
            result.get("files_copied", 0),
            result.get("total_size", 0),
            backup_path=result.get("backup_path"),
            error_message=error_message,
        )

        message = (
            f'Backup "{job_name}" finished.\n\n'
            f'Files copied: {result.get("files_copied", 0)}\n'
            f'Size: {format_file_size(result.get("total_size", 0))}'
        )
        if errors:
            message += "\n\n" + "\n".join(errors)
            QMessageBox.warning(self, "Backup Completed With Errors", message)
        else:
            QMessageBox.information(self, "Backup Complete", message)

    def on_backup_failed(self, job_id: int, job_name: str, error: str):
        """Record and report a worker failure."""
        self.db.record_backup_history(job_id, "failed", error_message=error)
        QMessageBox.critical(
            self, "Backup Error", f'Backup "{job_name}" failed:\n\n{error}'
        )

    def on_new_job(self):
        """Handle new job button click"""
        QMessageBox.information(
            self, "Info", "Go to Backup Jobs tab to create a new job"
        )
