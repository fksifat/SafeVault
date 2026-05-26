"""Dashboard UI Widget"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QProgressBar,
    QMessageBox,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class DashboardWidget(QWidget):
    """Dashboard showing backup status and statistics"""

    def __init__(self, parent=None, db_manager=None, backup_manager=None):
        super().__init__(parent)
        self.db = db_manager
        self.backup_manager = backup_manager
        self.init_ui()

    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()

        # Title
        title = QLabel("Backup Dashboard")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Stats section
        stats_layout = QHBoxLayout()

        # Active backups
        self.active_label = QLabel("0")
        active_box = self._create_stat_box("Active Backups", self.active_label)
        stats_layout.addWidget(active_box)

        # Last backup
        self.last_backup_label = QLabel("Never")
        last_backup_box = self._create_stat_box("Last Backup", self.last_backup_label)
        stats_layout.addWidget(last_backup_box)

        # Total backed up
        self.total_label = QLabel("0 GB")
        total_box = self._create_stat_box("Total Backed Up", self.total_label)
        stats_layout.addWidget(total_box)

        layout.addLayout(stats_layout)

        # Backup jobs table
        job_label = QLabel("Backup Jobs")
        job_font = QFont()
        job_font.setPointSize(12)
        job_font.setBold(True)
        job_label.setFont(job_font)
        layout.addWidget(job_label)

        self.jobs_table = QTableWidget()
        self.jobs_table.setColumnCount(5)
        self.jobs_table.setHorizontalHeaderLabels(
            ["Job Name", "Status", "Last Run", "Next Run", "Actions"]
        )
        layout.addWidget(self.jobs_table)

        # Action buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        new_job_btn = QPushButton("New Backup Job")
        new_job_btn.clicked.connect(self.on_new_job)
        btn_layout.addWidget(new_job_btn)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_jobs)
        btn_layout.addWidget(refresh_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

        # Refresh on load
        self.refresh_jobs()

    def _create_stat_box(self, label: str, value_widget) -> QWidget:
        """Create a stat box widget"""
        box = QWidget()
        box_layout = QVBoxLayout()

        label_widget = QLabel(label)
        label_widget.setFont(QFont("Arial", 10))

        if isinstance(value_widget, str):
            value_label = QLabel(value_widget)
        else:
            value_label = value_widget

        value_font = QFont("Arial", 14)
        value_font.setBold(True)
        value_label.setFont(value_font)

        box_layout.addWidget(label_widget)
        box_layout.addWidget(value_label)
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
                    self.last_backup_label.setText(str(last_run)[:10])
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
                run_btn.clicked.connect(
                    lambda checked, jid=job["id"], jname=job["name"]: self.run_backup(
                        jid, jname
                    )
                )
                self.jobs_table.setCellWidget(row, 4, run_btn)

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

            # Perform backup
            result = self.backup_manager.perform_full_backup(
                job_id, job["source_path"], job["destination_path"]
            )

            # Record in database
            self.db.record_backup_history(
                job_id,
                result["status"],
                result.get("files_copied", 0),
                result.get("total_size", 0),
                backup_path=result.get("backup_path"),
                error_message=result.get("error"),
            )

            QMessageBox.information(
                self,
                "Backup Complete",
                f'Backup "{job_name}" completed successfully!\n\n'
                f'Files copied: {result.get("files_copied", 0)}\n'
                f'Size: {result.get("total_size", 0)} bytes',
            )

            self.refresh_jobs()

        except Exception as e:
            QMessageBox.critical(self, "Backup Error", f"Backup failed: {str(e)}")

    def on_new_job(self):
        """Handle new job button click"""
        QMessageBox.information(
            self, "Info", "Go to Backup Jobs tab to create a new job"
        )
