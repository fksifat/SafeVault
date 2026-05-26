"""Restore Manager for SafeVault"""

import os
import shutil
from pathlib import Path
from app.logs import get_logger
from app.database import DatabaseManager

logger = get_logger()


class RestoreManager:
    """Manages restore operations"""

    def __init__(self, db_manager: DatabaseManager):
        """Initialize restore manager"""
        self.db = db_manager

    def get_backup_snapshots(self, job_id: int) -> list:
        """Get all backup snapshots for a job"""
        history = self.db.get_backup_history(job_id)
        return [
            h for h in history if h["status"] in ["completed", "completed_with_errors"]
        ]

    def get_files_in_snapshot(self, job_id: int, backup_time: str) -> list:
        """Get files in a specific backup snapshot"""
        metadata = self.db.get_file_metadata(job_id)
        return [m for m in metadata if m["backup_version"]]

    def restore_file(
        self, source_file: str, destination: str, overwrite: bool = False
    ) -> bool:
        """Restore a single file"""
        try:
            if os.path.exists(destination) and not overwrite:
                logger.warning(f"File already exists: {destination}")
                return False

            # Create destination directory if needed
            os.makedirs(os.path.dirname(destination), exist_ok=True)

            # Copy file
            shutil.copy2(source_file, destination)
            logger.info(f"File restored: {source_file} -> {destination}")
            return True

        except Exception as e:
            logger.error(f"File restore failed: {e}")
            return False

    def restore_folder(
        self, source_folder: str, destination: str, overwrite: bool = False
    ) -> dict:
        """Restore a folder from backup"""
        results = {"files_restored": 0, "failed": 0, "errors": []}

        try:
            if not os.path.exists(source_folder):
                logger.error(f"Source folder not found: {source_folder}")
                results["errors"].append(f"Source folder not found: {source_folder}")
                return results

            # Create destination directory
            os.makedirs(destination, exist_ok=True)

            # Restore files
            for root, dirs, files in os.walk(source_folder):
                rel_path = os.path.relpath(root, source_folder)
                if rel_path == ".":
                    target_dir = destination
                else:
                    target_dir = os.path.join(destination, rel_path)

                os.makedirs(target_dir, exist_ok=True)

                for file in files:
                    src = os.path.join(root, file)
                    dst = os.path.join(target_dir, file)

                    try:
                        if os.path.exists(dst) and not overwrite:
                            logger.warning(f"File skipped (exists): {dst}")
                            continue

                        shutil.copy2(src, dst)
                        results["files_restored"] += 1
                    except Exception as e:
                        logger.error(f"Failed to restore {file}: {e}")
                        results["failed"] += 1
                        results["errors"].append(str(e))

            logger.info(
                f'Folder restore completed: {results["files_restored"]} files restored'
            )
            return results

        except Exception as e:
            logger.error(f"Folder restore failed: {e}")
            results["errors"].append(str(e))
            return results

    def restore_snapshot(
        self, backup_path: str, destination: str, overwrite: bool = False
    ) -> dict:
        """Restore entire backup snapshot"""
        logger.info(f"Starting snapshot restore from {backup_path}")
        return self.restore_folder(backup_path, destination, overwrite)

    def list_backup_contents(self, backup_path: str) -> list:
        """List contents of a backup"""
        contents = []
        try:
            for root, dirs, files in os.walk(backup_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, backup_path)
                    size = os.path.getsize(file_path)
                    contents.append(
                        {"path": rel_path, "full_path": file_path, "size": size}
                    )
        except Exception as e:
            logger.error(f"Failed to list backup contents: {e}")

        return contents
