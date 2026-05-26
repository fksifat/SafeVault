"""Example test for backup manager"""

import pytest
import tempfile
import os
from app.database import DatabaseManager
from app.backup_engine import BackupManager


def test_backup_manager_creation():
    """Test backup manager initialization"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        db = DatabaseManager(db_path)
        backup_mgr = BackupManager(db)
        assert backup_mgr.db is not None


def test_create_backup_job():
    """Test creating a backup job"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        db = DatabaseManager(db_path)

        job_id = db.create_backup_job(
            name="Test Backup", source_path="/tmp/source", destination_path="/tmp/dest"
        )

        assert job_id > 0
        job = db.get_backup_job(job_id)
        assert job["name"] == "Test Backup"


def test_get_all_jobs():
    """Test retrieving all jobs"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        db = DatabaseManager(db_path)

        db.create_backup_job("Job 1", "/tmp/src1", "/tmp/dst1")
        db.create_backup_job("Job 2", "/tmp/src2", "/tmp/dst2")

        jobs = db.get_all_backup_jobs()
        assert len(jobs) == 2
