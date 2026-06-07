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
    QInputDialog,
    QLineEdit,
    QFrame,
    QHeaderView,
    QAbstractItemView,
    QSplitter,
)
from PySide6.QtCore import Qt
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
        layout.setContentsMargins(18, 18, 18, 14)
        layout.setSpacing(14)

        # Title
        title = QLabel("Restore Backup")
        title.setObjectName("PageTitle")
        layout.addWidget(title)

        splitter = QSplitter(Qt.Vertical)

        history_panel = QFrame()
        history_panel.setObjectName("Panel")
        history_layout = QVBoxLayout(history_panel)
        history_layout.setContentsMargins(14, 14, 14, 14)
        history_layout.setSpacing(10)

        history_header = QHBoxLayout()
        history_label = QLabel("Backup History")
        history_label.setObjectName("SectionTitle")
        history_header.addWidget(history_label)
        history_header.addStretch()
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_backups)
        history_header.addWidget(refresh_btn)
        history_layout.addLayout(history_header)

        # Backup history tree
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["Backup Date", "Job", "Status", "Size"])
        self.tree_widget.setAlternatingRowColors(True)
        self.tree_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tree_widget.itemSelectionChanged.connect(self.load_selected_snapshot)
        self.tree_widget.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tree_widget.header().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tree_widget.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.tree_widget.header().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        history_layout.addWidget(self.tree_widget)

        self.history_empty_label = QLabel("No completed backups found yet.")
        self.history_empty_label.setObjectName("MutedText")
        self.history_empty_label.setAlignment(Qt.AlignCenter)
        history_layout.addWidget(self.history_empty_label)

        files_panel = QFrame()
        files_panel.setObjectName("Panel")
        files_layout = QVBoxLayout(files_panel)
        files_layout.setContentsMargins(14, 14, 14, 14)
        files_layout.setSpacing(10)

        files_header = QHBoxLayout()
        files_label = QLabel("Files in Selected Backup")
        files_label.setObjectName("SectionTitle")
        files_header.addWidget(files_label)
        files_header.addStretch()
        files_layout.addLayout(files_header)

        # Files in backup
        self.files_tree = QTreeWidget()
        self.files_tree.setHeaderLabels(["File Name", "Size", "Modified"])
        self.files_tree.setAlternatingRowColors(True)
        self.files_tree.setSelectionMode(QTreeWidget.ExtendedSelection)
        self.files_tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.files_tree.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.files_tree.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        files_layout.addWidget(self.files_tree)

        self.files_empty_label = QLabel("Select a backup above to preview its files.")
        self.files_empty_label.setObjectName("MutedText")
        self.files_empty_label.setAlignment(Qt.AlignCenter)
        files_layout.addWidget(self.files_empty_label)

        splitter.addWidget(history_panel)
        splitter.addWidget(files_panel)
        splitter.setSizes([260, 260])
        layout.addWidget(splitter, 1)

        # Action buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        restore_btn = QPushButton("Restore Selected")
        restore_btn.setObjectName("PrimaryButton")
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
            self.history_empty_label.setVisible(True)
            self.tree_widget.setVisible(False)
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
                        "encryption_password": job.get("encryption_password"),
                        "history": history,
                    },
                )
                self.tree_widget.addTopLevelItem(item)

        has_backups = self.tree_widget.topLevelItemCount() > 0
        self.history_empty_label.setVisible(not has_backups)
        self.tree_widget.setVisible(has_backups)
        self.files_empty_label.setText("Select a backup above to preview its files.")
        self.files_empty_label.setVisible(True)
        self.files_tree.setVisible(False)
        if has_backups:
            self.tree_widget.setCurrentItem(self.tree_widget.topLevelItem(0))

    def _discover_snapshot_paths(self, job: dict) -> list:
        """Find snapshot folders for older history rows without stored paths."""
        job_dir = os.path.join(job["destination_path"], f'job_{job["id"]}')
        if not os.path.isdir(job_dir):
            return []

        paths = []
        for name in os.listdir(job_dir):
            snapshot_path = os.path.join(job_dir, name)
            if os.path.isdir(snapshot_path) or name.endswith((".zip", ".zip.encrypted")):
                paths.append(snapshot_path)

        def sort_key(path):
            name = os.path.basename(path)
            name = name.replace(".zip.encrypted", "").replace(".zip", "")
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
            self.files_empty_label.setText("Select a backup above to preview its files.")
            self.files_empty_label.setVisible(True)
            self.files_tree.setVisible(False)
            return

        snapshot = selected[0].data(0, Qt.UserRole)
        backup_path = snapshot.get("backup_path") if snapshot else None
        if not backup_path or not os.path.exists(backup_path):
            QMessageBox.warning(
                self,
                "Backup Not Found",
                "The selected backup folder could not be found on disk.",
            )
            self.files_empty_label.setText("The selected backup folder could not be found on disk.")
            self.files_empty_label.setVisible(True)
            self.files_tree.setVisible(False)
            return

        effective_path = backup_path
        if backup_path.endswith(".encrypted"):
            password = snapshot.get("encryption_password")
            if not password:
                password, ok = QInputDialog.getText(
                    self,
                    "Encryption Password",
                    "Enter the password for this encrypted backup:",
                    QLineEdit.Password,
                )
                if not ok or not password:
                    self.files_empty_label.setText(
                        "Password is required to preview this encrypted backup."
                    )
                    self.files_empty_label.setVisible(True)
                    self.files_tree.setVisible(False)
                    return

            effective_path = self.restore_manager.decrypt_snapshot(backup_path, password)
            if not effective_path:
                QMessageBox.warning(
                    self,
                    "Decrypt Failed",
                    "The encrypted backup could not be opened with that password.",
                )
                self.files_empty_label.setText("The encrypted backup could not be opened.")
                self.files_empty_label.setVisible(True)
                self.files_tree.setVisible(False)
                return

        snapshot["effective_backup_path"] = effective_path
        self.current_snapshot = snapshot
        for file_info in self.restore_manager.list_backup_contents(effective_path):
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

        has_files = self.files_tree.topLevelItemCount() > 0
        self.files_empty_label.setText("This backup does not contain any files.")
        self.files_empty_label.setVisible(not has_files)
        self.files_tree.setVisible(has_files)

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
                    if file_info.get("archive_path"):
                        restored_ok = self.restore_manager.restore_archive_member(
                            file_info["archive_path"],
                            file_info["archive_member"],
                            target,
                            overwrite=True,
                        )
                    else:
                        restored_ok = self.restore_manager.restore_file(
                            file_info["full_path"], target, overwrite=True
                        )

                    if restored_ok:
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

        backup_path = self.current_snapshot.get(
            "effective_backup_path"
        ) or self.current_snapshot.get("backup_path")
        if not backup_path or not os.path.exists(backup_path):
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
