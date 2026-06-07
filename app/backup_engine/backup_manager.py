"""Backup Manager for SafeVault"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from app.logs import get_logger
from app.utils import (
    get_file_hash,
    format_file_size,
    ensure_path_exists,
    get_directory_size,
)
from app.database import DatabaseManager
from app.compression import CompressionManager

logger = get_logger()


class BackupManager:
    """Manages backup operations"""

    def __init__(self, db_manager: DatabaseManager):
        """Initialize backup manager"""
        self.db = db_manager

    def get_backup_destination(self, job_id: int, base_destination: str) -> str:
        """Get backup destination directory with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        job_name = f"job_{job_id}"
        backup_path = os.path.join(base_destination, job_name, timestamp)
        ensure_path_exists(backup_path)
        return backup_path

    def scan_directory(self, path: str) -> list:
        """Scan directory and get list of all files"""
        files = []
        if not os.path.exists(path):
            logger.error(f"Source path does not exist: {path}")
            return files
        if not os.path.isdir(path):
            logger.error(f"Source path is not a directory: {path}")
            return files

        try:
            for root, dirs, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(root, filename)
                    try:
                        files.append(
                            {
                                "path": filepath,
                                "relative_path": os.path.relpath(filepath, path),
                                "size": os.path.getsize(filepath),
                                "mtime": os.path.getmtime(filepath),
                            }
                        )
                    except Exception as e:
                        logger.warning(f"Error scanning file {filepath}: {e}")
                        continue
        except Exception as e:
            logger.error(f"Error scanning directory {path}: {e}")

        return files

    def detect_changed_files(self, job_id: int, current_files: list) -> list:
        """Detect changed files for incremental backup"""
        changed_files = []
        existing_metadata = self.db.get_file_metadata(job_id)
        existing_files = {m["file_path"]: m for m in existing_metadata}

        for file_info in current_files:
            file_path = file_info["path"]
            file_hash = get_file_hash(file_path)

            if file_path not in existing_files:
                # New file
                changed_files.append(file_info)
            else:
                # Check if modified
                if existing_files[file_path]["file_hash"] != file_hash:
                    changed_files.append(file_info)

        return changed_files

    def copy_files(self, files: list, destination: str) -> tuple:
        """Copy files to destination"""
        files_copied = 0
        total_size = 0
        errors = []

        for file_info in files:
            try:
                src = file_info["path"]
                rel_path = file_info["relative_path"]
                dest = os.path.join(destination, rel_path)

                # Create destination directories
                dest_dir = os.path.dirname(dest)
                ensure_path_exists(dest_dir)

                # Copy file
                shutil.copy2(src, dest)
                files_copied += 1
                total_size += file_info["size"]

                logger.debug(f"Copied: {src} -> {dest}")
            except Exception as e:
                error_msg = f'Error copying {file_info["path"]}: {e}'
                logger.error(error_msg)
                errors.append(error_msg)
                continue

        return files_copied, total_size, errors

    def _get_compression_level(self) -> int:
        """Read the configured ZIP compression level."""
        setting = self.db.get_setting("compression_level", "Normal")
        return {"Fast": 1, "Normal": 6, "Maximum": 9}.get(setting, 6)

    def _finalize_snapshot(self, backup_dest: str, job: dict) -> tuple:
        """Apply optional compression/encryption and return final path, size, errors."""
        errors = []
        final_path = backup_dest
        compression_enabled = bool(job.get("compression_enabled"))
        encryption_enabled = bool(job.get("encryption_enabled"))

        logger.debug(
            f"Finalizing snapshot: dest={backup_dest}, compression={compression_enabled}, encryption={encryption_enabled}, job_id={job.get('id') if job else None}"
        )

        if not compression_enabled and not encryption_enabled:
            logger.debug("No compression or encryption requested; skipping finalize step")
            return final_path, get_directory_size(final_path), errors

        archive_path = f"{backup_dest}.zip"
        try:
            compressed = CompressionManager.compress_directory_zip(
                backup_dest, archive_path, self._get_compression_level()
            )
        except Exception as e:
            logger.error(f"Exception during compression: {e}")
            compressed = False

        if not compressed:
            logger.error("Compression step failed or returned False")
            errors.append("Compression failed")
            return final_path, get_directory_size(final_path), errors

        logger.info(f"Compression succeeded: {archive_path}")
        shutil.rmtree(backup_dest)
        final_path = archive_path

        if encryption_enabled:
            password = job.get("encryption_password")
            if not password:
                errors.append("Encryption is enabled but no password is configured")
                return final_path, os.path.getsize(final_path), errors

            encrypted_path = f"{archive_path}.encrypted"
            from app.encryption import EncryptionManager

            if EncryptionManager.encrypt_file(archive_path, password, encrypted_path):
                os.remove(archive_path)
                final_path = encrypted_path
            else:
                errors.append("Encryption failed")

        return final_path, os.path.getsize(final_path), errors

    def _build_job(self, job_id: int, source_path: str, destination_path: str) -> dict:
        """Build a plain job dict for legacy direct backup calls."""
        return {
            "id": job_id,
            "source_path": source_path,
            "destination_path": destination_path,
            "compression_enabled": False,
            "encryption_enabled": False,
            "encryption_password": None,
        }

    def perform_full_backup(
        self,
        job_id: int,
        source_path: str,
        destination_path: str,
        job_options: dict = None,
    ) -> dict:
        """Perform a full backup"""
        logger.info(f"Starting full backup for job {job_id}")

        try:
            job = job_options or self._build_job(job_id, source_path, destination_path)
            if job.get("encryption_enabled") and not job.get("encryption_password"):
                error_message = "Encryption is enabled but no password is configured"
                logger.error(error_message)
                return {
                    "status": "failed",
                    "error": error_message,
                    "files_copied": 0,
                    "total_size": 0,
                }

            # Scan source directory
            files = self.scan_directory(source_path)
            if not files:
                error_message = f"No files found in source path: {source_path}"
                logger.warning(error_message)
                return {
                    "status": "failed",
                    "error": error_message,
                    "files_copied": 0,
                    "total_size": 0,
                }

            # Get backup destination
            backup_dest = self.get_backup_destination(job_id, destination_path)

            # Copy files
            files_copied, total_size, errors = self.copy_files(files, backup_dest)

            # Update metadata
            for file_info in files:
                file_hash = get_file_hash(file_info["path"])
                self.db.save_file_metadata(
                    job_id,
                    file_info["path"],
                    file_hash,
                    datetime.now().isoformat(),
                    "full",
                    file_info["size"],
                )

            final_path, backup_size, finalize_errors = self._finalize_snapshot(
                backup_dest, job
            )
            errors.extend(finalize_errors)

            status = "completed" if not errors else "completed_with_errors"
            logger.info(
                f"Full backup completed: {files_copied} files, {format_file_size(backup_size)}"
            )

            return {
                "status": status,
                "files_copied": files_copied,
                "total_size": backup_size,
                "backup_path": final_path,
                "errors": errors,
            }

        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "files_copied": 0,
                "total_size": 0,
            }

    def perform_incremental_backup(
        self,
        job_id: int,
        source_path: str,
        destination_path: str,
        job_options: dict = None,
    ) -> dict:
        """Perform an incremental backup"""
        logger.info(f"Starting incremental backup for job {job_id}")

        try:
            job = job_options or self._build_job(job_id, source_path, destination_path)
            if job.get("encryption_enabled") and not job.get("encryption_password"):
                error_message = "Encryption is enabled but no password is configured"
                logger.error(error_message)
                return {
                    "status": "failed",
                    "error": error_message,
                    "files_copied": 0,
                    "total_size": 0,
                }

            # Scan source directory
            files = self.scan_directory(source_path)
            if not files:
                error_message = f"No files found in source path: {source_path}"
                logger.warning(error_message)
                return {
                    "status": "failed",
                    "error": error_message,
                    "files_copied": 0,
                    "total_size": 0,
                }

            # Detect changed files
            changed_files = self.detect_changed_files(job_id, files)

            if not changed_files:
                logger.info("No changes detected")
                return {
                    "status": "completed",
                    "files_copied": 0,
                    "total_size": 0,
                    "message": "No changes detected",
                }

            # Get backup destination
            backup_dest = self.get_backup_destination(job_id, destination_path)

            # Copy changed files
            files_copied, total_size, errors = self.copy_files(
                changed_files, backup_dest
            )

            # Update metadata
            for file_info in changed_files:
                file_hash = get_file_hash(file_info["path"])
                self.db.save_file_metadata(
                    job_id,
                    file_info["path"],
                    file_hash,
                    datetime.now().isoformat(),
                    "incremental",
                    file_info["size"],
                )

            final_path, backup_size, finalize_errors = self._finalize_snapshot(
                backup_dest, job
            )
            errors.extend(finalize_errors)

            status = "completed" if not errors else "completed_with_errors"
            logger.info(
                f"Incremental backup completed: {files_copied} files, {format_file_size(backup_size)}"
            )

            return {
                "status": status,
                "files_copied": files_copied,
                "total_size": backup_size,
                "backup_path": final_path,
                "errors": errors,
            }

        except Exception as e:
            logger.error(f"Incremental backup failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "files_copied": 0,
                "total_size": 0,
            }
