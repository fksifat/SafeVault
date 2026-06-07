"""Restore Manager for SafeVault"""

import os
import shutil
import tempfile
import zipfile
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

    def decrypt_snapshot(self, encrypted_path: str, password: str) -> str:
        """Decrypt an encrypted snapshot to a temporary ZIP file."""
        temp_dir = tempfile.mkdtemp(prefix="safevault_restore_")
        output_path = os.path.join(
            temp_dir, os.path.basename(encrypted_path).replace(".encrypted", "")
        )
        from app.encryption import EncryptionManager

        if EncryptionManager.decrypt_file(encrypted_path, password, output_path):
            return output_path

        shutil.rmtree(temp_dir, ignore_errors=True)
        return None

    def restore_archive_member(
        self,
        archive_path: str,
        member_name: str,
        destination: str,
        overwrite: bool = False,
    ) -> bool:
        """Restore a single file from a ZIP snapshot."""
        try:
            normalized_member = member_name.replace("\\", "/")
            if normalized_member.startswith("/") or ".." in normalized_member.split("/"):
                logger.error(f"Unsafe archive path: {member_name}")
                return False

            if os.path.exists(destination) and not overwrite:
                logger.warning(f"File already exists: {destination}")
                return False

            os.makedirs(os.path.dirname(destination), exist_ok=True)
            with zipfile.ZipFile(archive_path, "r") as zipf:
                with zipf.open(member_name) as src, open(destination, "wb") as dst:
                    shutil.copyfileobj(src, dst)

            logger.info(
                f"Archive file restored: {archive_path}:{member_name} -> {destination}"
            )
            return True
        except Exception as e:
            logger.error(f"Archive file restore failed: {e}")
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
        if zipfile.is_zipfile(backup_path):
            return self.restore_zip_snapshot(backup_path, destination, overwrite)
        return self.restore_folder(backup_path, destination, overwrite)

    def restore_zip_snapshot(
        self, archive_path: str, destination: str, overwrite: bool = False
    ) -> dict:
        """Restore every file from a ZIP snapshot."""
        results = {"files_restored": 0, "failed": 0, "errors": []}
        os.makedirs(destination, exist_ok=True)

        try:
            with zipfile.ZipFile(archive_path, "r") as zipf:
                for info in zipf.infolist():
                    if info.is_dir():
                        continue

                    normalized_name = info.filename.replace("\\", "/")
                    if normalized_name.startswith("/") or ".." in normalized_name.split("/"):
                        results["failed"] += 1
                        results["errors"].append(f"Unsafe archive path: {info.filename}")
                        continue

                    target = os.path.abspath(os.path.join(destination, normalized_name))
                    dest_root = os.path.abspath(destination)
                    if not target.startswith(dest_root + os.sep):
                        results["failed"] += 1
                        results["errors"].append(f"Unsafe archive path: {info.filename}")
                        continue

                    if os.path.exists(target) and not overwrite:
                        logger.warning(f"File skipped (exists): {target}")
                        continue

                    os.makedirs(os.path.dirname(target), exist_ok=True)
                    with zipf.open(info.filename) as src, open(target, "wb") as dst:
                        shutil.copyfileobj(src, dst)
                    results["files_restored"] += 1

            return results
        except Exception as e:
            logger.error(f"ZIP snapshot restore failed: {e}")
            results["errors"].append(str(e))
            return results

    def list_backup_contents(self, backup_path: str) -> list:
        """List contents of a backup"""
        contents = []
        try:
            if zipfile.is_zipfile(backup_path):
                with zipfile.ZipFile(backup_path, "r") as zipf:
                    for info in zipf.infolist():
                        if info.is_dir():
                            continue
                        contents.append(
                            {
                                "path": info.filename,
                                "full_path": backup_path,
                                "archive_path": backup_path,
                                "archive_member": info.filename,
                                "size": info.file_size,
                            }
                        )
                return contents

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
