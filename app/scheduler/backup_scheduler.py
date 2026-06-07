"""Backup Scheduler for SafeVault"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.logs import get_logger
from app.database import DatabaseManager
from app.backup_engine import BackupManager

logger = get_logger()


class BackupScheduler:
    """Manages backup scheduling"""

    def __init__(self, db_manager: DatabaseManager, backup_manager: BackupManager):
        """Initialize scheduler"""
        self.db = db_manager
        self.backup_manager = backup_manager
        self.scheduler = BackgroundScheduler()
        self.job_ids = {}

    def start(self):
        """Start the scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            self.load_scheduled_jobs()
            logger.info("Backup scheduler started")

    def load_scheduled_jobs(self):
        """Load saved non-manual jobs from the database."""
        for job in self.db.get_all_backup_jobs():
            schedule_type = job.get("schedule_type")
            if schedule_type and schedule_type != "manual":
                self.schedule_job(job["id"], job["name"], schedule_type)

    def stop(self):
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Backup scheduler stopped")

    def schedule_job(self, job_id: int, job_name: str, schedule_type: str):
        """Schedule a backup job"""
        try:
            # Remove existing job if present
            if job_id in self.job_ids:
                self.scheduler.remove_job(self.job_ids[job_id])

            schedule_id = f"backup_job_{job_id}"

            # Schedule based on type
            if schedule_type == "daily":
                trigger = CronTrigger(hour=0, minute=0)
            elif schedule_type == "weekly":
                trigger = CronTrigger(day_of_week=0, hour=0, minute=0)  # Monday
            elif schedule_type == "monthly":
                trigger = CronTrigger(day=1, hour=0, minute=0)
            else:
                logger.warning(f"Unknown schedule type: {schedule_type}")
                return

            self.scheduler.add_job(
                func=self._run_backup,
                args=(job_id,),
                trigger=trigger,
                id=schedule_id,
                replace_existing=True,
            )

            self.job_ids[job_id] = schedule_id
            logger.info(f"Job {job_name} scheduled: {schedule_type}")

        except Exception as e:
            logger.error(f"Failed to schedule job {job_name}: {e}")

    def unschedule_job(self, job_id: int):
        """Unschedule a backup job"""
        if job_id in self.job_ids:
            schedule_id = self.job_ids[job_id]
            try:
                self.scheduler.remove_job(schedule_id)
                del self.job_ids[job_id]
                logger.info(f"Job {job_id} unscheduled")
            except Exception as e:
                logger.error(f"Failed to unschedule job {job_id}: {e}")

    def _run_backup(self, job_id: int):
        """Execute backup job"""
        try:
            job = self.db.get_backup_job(job_id)
            if not job:
                logger.warning(f"Job {job_id} not found")
                return

            logger.info(f'Running scheduled backup: {job["name"]}')

            # Determine if full or incremental
            history = self.db.get_backup_history(job_id)
            is_incremental = len(history) > 0

            # Perform backup
            if is_incremental:
                result = self.backup_manager.perform_incremental_backup(
                    job_id, job["source_path"], job["destination_path"], job
                )
            else:
                result = self.backup_manager.perform_full_backup(
                    job_id, job["source_path"], job["destination_path"], job
                )

            # Record in database
            self.db.record_backup_history(
                job_id,
                result.get("status", "failed"),
                result.get("files_copied", 0),
                result.get("total_size", 0),
                duration=0,
                backup_path=result.get("backup_path"),
                error_message=result.get("error"),
            )

            logger.info(f"Backup completed for job {job_id}: {result}")

        except Exception as e:
            logger.error(f"Backup execution failed for job {job_id}: {e}")
            self.db.record_backup_history(job_id, "failed", error_message=str(e))

    def get_scheduled_jobs(self):
        """Get all scheduled jobs"""
        return self.scheduler.get_jobs()
