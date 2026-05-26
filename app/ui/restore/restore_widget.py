"""Restore UI Widget"""

import os
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QTreeWidget,
    QTreeWidgetItem,
    QFileDialog,
    QMessageBox,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from app.utils import format_file_size


class RestoreWidget(QWidget):
    """Widget for restoring backups"""

    def __init__(self, parent=None, db_manager=None, restore_manager=None):
        super().__init__(parent)
        self.db = db_manager
        self.restore_manager = restore_manager
        self.current_snapshot = None
        self.init_ui()

    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()

        # Title
        title = QLabel("Restore Backup")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Backup history tree
        history_label = QLabel("Backup History:")
        layout.addWidget(history_label)

        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["Backup Date", "Job", "Status", "Size"])
        self.tree_widget.itemSelectionChanged.connect(self.load_selected_snapshot)
        layout.addWidget(self.tree_widget)

        # Files in backup
        files_label = QLabel("Files in Backup:")
        layout.addWidget(files_label)

        self.files_tree = QTreeWidget()
        self.files_tree.setHeaderLabels(["File Name", "Size", "Modified"])
        self.files_tree.setSelectionMode(QTreeWidget.ExtendedSelection)
        layout.addWidget(self.files_tree)

        # Action buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_backups)
        btn_layout.addWidget(refresh_btn)

        restore_btn = QPushButton("Restore Selected")
        restore_btn.clicked.connect(self.restore_selected)
        btn_layout.addWidget(restore_btn)

        restore_all_btn = QPushButton("Restore All")
        restore_all_btn.clicked.connect(self.restore_all)
        btn_layout.addWidget(restore_all_btn)

        layout.addLayout(btn_layout)

        self.setLayout(layout)
        self.refresh_backups()

    def add_backup_entry(self, backup_date: str, status: str, size: str):
        """Add backup entry to tree"""
        item = QTreeWidgetItem()
        item.setText(0, backup_date)
        item.setText(1, status)
        item.setText(2, size)
        self.tree_widget.addTopLevelItem(item)

    def refresh_backups(self):
        """Load backup snapshots from database history."""
        self.tree_widget.clear()
        self.files_tree.clear()
        self.current_snapshot = None

        if not self.db:
            return

        for job in self.db.get_all_backup_jobs():
            histories = self.db.get_backup_history(job["id"])
            inferred_paths = self._discover_snapshot_paths(job)

            for index, history in enumerate(histories):
                if history["status"] not in ["completed", "completed_with_errors"]:
                    continue

                backup_path = history.get("backup_path")
                if not backup_path and index < len(inferred_paths):
                    backup_path = inferred_paths[index]

                item = QTreeWidgetItem()
                item.setText(0, str(history["backup_time"])[:19])
                item.setText(1, job["name"])
                item.setText(2, history["status"])
                item.setText(3, format_file_size(history.get("backup_size") or 0))
                item.setData(
                    0,
                    Qt.UserRole,
                    {
                        "job_id": job["id"],
                        "job_name": job["name"],
                        "backup_path": backup_path,
                        "history": history,
                    },
                )
                self.tree_widget.addTopLevelItem(item)

        self.tree_widget.resizeColumnToContents(0)
        self.tree_widget.resizeColumnToContents(1)

    def _discover_snapshot_paths(self, job: dict) -> list:
        """Find snapshot folders for older history rows without stored paths."""
        job_dir = os.path.join(job["destination_path"], f'job_{job["id"]}')
        if not os.path.isdir(job_dir):
            return []

        paths = []
        for name in os.listdir(job_dir):
            snapshot_path = os.path.join(job_dir, name)
            if os.path.isdir(snapshot_path):
                paths.append(snapshot_path)

        def sort_key(path):
            name = os.path.basename(path)
            try:
                return datetime.strptime(name, "%Y-%m-%d_%H-%M-%S")
            except ValueError:
                return datetime.fromtimestamp(os.path.getmtime(path))

        return sorted(paths, key=sort_key, reverse=True)

    def load_selected_snapshot(self):
        """Load files for the selected backup snapshot."""
        selected = self.tree_widget.selectedItems()
        self.files_tree.clear()
        self.current_snapshot = None

        if not selected:
            return

        snapshot = selected[0].data(0, Qt.UserRole)
        backup_path = snapshot.get("backup_path") if snapshot else None
        if not backup_path or not os.path.isdir(backup_path):
            QMessageBox.warning(
                self,
                "Backup Not Found",
                "The selected backup folder could not be found on disk.",
            )
            return

        self.current_snapshot = snapshot
        for file_info in self.restore_manager.list_backup_contents(backup_path):
            item = QTreeWidgetItem()
            item.setText(0, file_info["path"])
            item.setText(1, format_file_size(file_info["size"]))
            item.setText(
                2,
                datetime.fromtimestamp(os.path.getmtime(file_info["full_path"])).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            )
            item.setData(0, Qt.UserRole, file_info)
            self.files_tree.addTopLevelItem(item)

        self.files_tree.resizeColumnToContents(0)

    def restore_selected(self):
        """Restore selected files"""
        if not self.current_snapshot:
            QMessageBox.warning(self, "No Backup Selected", "Select a backup first.")
            return

        selected_files = self.files_tree.selectedItems()
        if not selected_files:
            QMessageBox.warning(
                self, "No Files Selected", "Select one or more files to restore."
            )
            return

        destination = QFileDialog.getExistingDirectory(
            self, "Select Restore Destination"
        )
        if destination:
            try:
                restored = 0
                failed = 0
                for item in selected_files:
                    file_info = item.data(0, Qt.UserRole)
                    target = os.path.join(destination, file_info["path"])
                    if self.restore_manager.restore_file(
                        file_info["full_path"], target, overwrite=True
                    ):
                        restored += 1
                    else:
                        failed += 1

                if failed:
                    QMessageBox.warning(
                        self,
                        "Restore Completed With Errors",
                        f"Restored {restored} file(s). Failed: {failed}.",
                    )
                    return

                QMessageBox.information(
                    self, "Success", f"Restored {restored} file(s) to {destination}"
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Restore failed: {str(e)}")

    def restore_all(self):
        """Restore all files"""
        if not self.current_snapshot:
            QMessageBox.warning(self, "No Backup Selected", "Select a backup first.")
            return

        backup_path = self.current_snapshot.get("backup_path")
        if not backup_path or not os.path.isdir(backup_path):
            QMessageBox.warning(
                self,
                "Backup Not Found",
                "The selected backup folder could not be found on disk.",
            )
            return

        destination = QFileDialog.getExistingDirectory(
            self, "Select Restore Destination"
        )
        if destination:
            try:
                results = self.restore_manager.restore_snapshot(
                    backup_path, destination, overwrite=True
                )
                if results["errors"]:
                    QMessageBox.warning(
                        self,
                        "Restore Completed With Errors",
                        f'Restored {results["files_restored"]} file(s). '
                        f'Failed: {results["failed"]}.',
                    )
                    return

                QMessageBox.information(
                    self,
                    "Success",
                    f'Restored {results["files_restored"]} file(s) to {destination}',
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Restore failed: {str(e)}")
