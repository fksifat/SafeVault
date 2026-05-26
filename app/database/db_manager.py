"""Database Manager for SafeVault"""

import sqlite3
import os
from datetime import datetime
from pathlib import Path


class DatabaseManager:
    """Manages SQLite database operations for backup jobs and history"""

    def __init__(self, db_path: str = None):
        """Initialize database manager"""
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(__file__), "../../database/safevault.db"
            )

        self.db_path = db_path
        Path(os.path.dirname(db_path)).mkdir(parents=True, exist_ok=True)
        self.init_database()

    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Backup Jobs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS backup_jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                source_path TEXT NOT NULL,
                destination_path TEXT NOT NULL,
                schedule_type TEXT DEFAULT 'manual',
                compression_enabled INTEGER DEFAULT 0,
                encryption_enabled INTEGER DEFAULT 0,
                encryption_password TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Backup History table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS backup_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER NOT NULL,
                backup_time TIMESTAMP,
                status TEXT,
                files_copied INTEGER DEFAULT 0,
                backup_size INTEGER DEFAULT 0,
                duration INTEGER DEFAULT 0,
                backup_path TEXT,
                error_message TEXT,
                FOREIGN KEY (job_id) REFERENCES backup_jobs(id)
            )
        """)
        cursor.execute("PRAGMA table_info(backup_history)")
        history_columns = {row[1] for row in cursor.fetchall()}
        if "backup_path" not in history_columns:
            cursor.execute("ALTER TABLE backup_history ADD COLUMN backup_path TEXT")

        # File Metadata table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS file_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER NOT NULL,
                file_path TEXT,
                file_hash TEXT,
                modified_time TIMESTAMP,
                backup_version TEXT,
                file_size INTEGER,
                FOREIGN KEY (job_id) REFERENCES backup_jobs(id)
            )
        """)

        # Settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    def create_backup_job(
        self,
        name: str,
        source_path: str,
        destination_path: str,
        schedule_type: str = "manual",
        compression_enabled: bool = False,
        encryption_enabled: bool = False,
        encryption_password: str = None,
    ) -> int:
        """Create a new backup job"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO backup_jobs 
                (name, source_path, destination_path, schedule_type, compression_enabled, 
                 encryption_enabled, encryption_password, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
            """,
                (
                    name,
                    source_path,
                    destination_path,
                    schedule_type,
                    int(compression_enabled),
                    int(encryption_enabled),
                    encryption_password,
                ),
            )
            conn.commit()
            job_id = cursor.lastrowid
            return job_id
        finally:
            conn.close()

    def get_all_backup_jobs(self):
        """Get all backup jobs"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM backup_jobs ORDER BY created_at DESC")
        jobs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jobs

    def get_backup_job(self, job_id: int):
        """Get a specific backup job"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM backup_jobs WHERE id = ?", (job_id,))
        job = cursor.fetchone()
        conn.close()
        return dict(job) if job else None

    def update_backup_job(self, job_id: int, **kwargs):
        """Update a backup job"""
        conn = self.get_connection()
        cursor = conn.cursor()

        allowed_fields = {
            "name",
            "source_path",
            "destination_path",
            "schedule_type",
            "compression_enabled",
            "encryption_enabled",
            "encryption_password",
        }
        update_fields = {k: v for k, v in kwargs.items() if k in allowed_fields}

        if not update_fields:
            conn.close()
            return

        update_fields["updated_at"] = datetime.now()
        set_clause = ", ".join([f"{k} = ?" for k in update_fields.keys()])
        values = list(update_fields.values()) + [job_id]

        cursor.execute(f"UPDATE backup_jobs SET {set_clause} WHERE id = ?", values)
        conn.commit()
        conn.close()

    def delete_backup_job(self, job_id: int):
        """Delete a backup job"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM backup_jobs WHERE id = ?", (job_id,))
        cursor.execute("DELETE FROM backup_history WHERE job_id = ?", (job_id,))
        cursor.execute("DELETE FROM file_metadata WHERE job_id = ?", (job_id,))
        conn.commit()
        conn.close()

    def record_backup_history(
        self,
        job_id: int,
        status: str,
        files_copied: int = 0,
        backup_size: int = 0,
        duration: int = 0,
        backup_path: str = None,
        error_message: str = None,
    ):
        """Record backup history"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO backup_history 
            (job_id, backup_time, status, files_copied, backup_size, duration, backup_path, error_message)
            VALUES (?, datetime('now'), ?, ?, ?, ?, ?, ?)
        """,
            (
                job_id,
                status,
                files_copied,
                backup_size,
                duration,
                backup_path,
                error_message,
            ),
        )
        conn.commit()
        conn.close()

    def get_backup_history(self, job_id: int):
        """Get backup history for a job"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM backup_history WHERE job_id = ? ORDER BY backup_time DESC",
            (job_id,),
        )
        history = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return history

    def save_file_metadata(
        self,
        job_id: int,
        file_path: str,
        file_hash: str,
        modified_time: str,
        backup_version: str,
        file_size: int,
    ):
        """Save file metadata"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO file_metadata 
            (job_id, file_path, file_hash, modified_time, backup_version, file_size)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (job_id, file_path, file_hash, modified_time, backup_version, file_size),
        )
        conn.commit()
        conn.close()

    def get_file_metadata(self, job_id: int, file_path: str = None):
        """Get file metadata"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if file_path:
            cursor.execute(
                "SELECT * FROM file_metadata WHERE job_id = ? AND file_path = ?",
                (job_id, file_path),
            )
            metadata = cursor.fetchone()
        else:
            cursor.execute("SELECT * FROM file_metadata WHERE job_id = ?", (job_id,))
            metadata = cursor.fetchall()

        conn.close()
        if isinstance(metadata, list):
            return [dict(row) for row in metadata]
        return dict(metadata) if metadata else None

    def set_setting(self, key: str, value: str):
        """Save an application setting."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO settings (key, value, updated_at)
            VALUES (?, ?, datetime('now'))
            ON CONFLICT(key) DO UPDATE SET
                value = excluded.value,
                updated_at = datetime('now')
        """,
            (key, value),
        )
        conn.commit()
        conn.close()

    def get_setting(self, key: str, default: str = None):
        """Get an application setting."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        conn.close()
        return row["value"] if row else default
