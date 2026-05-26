"""File Monitor for SafeVault"""

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from app.logs import get_logger

logger = get_logger()


class FileMonitor(FileSystemEventHandler):
    """Monitor file changes in directories"""

    def __init__(self, callback=None):
        """Initialize file monitor"""
        self.callback = callback
        self.observer = Observer()
        self.watch_paths = {}

    def on_created(self, event):
        """Handle file creation"""
        if not event.is_directory:
            logger.debug(f"File created: {event.src_path}")
            if self.callback:
                self.callback("created", event.src_path)

    def on_modified(self, event):
        """Handle file modification"""
        if not event.is_directory:
            logger.debug(f"File modified: {event.src_path}")
            if self.callback:
                self.callback("modified", event.src_path)

    def on_deleted(self, event):
        """Handle file deletion"""
        if not event.is_directory:
            logger.debug(f"File deleted: {event.src_path}")
            if self.callback:
                self.callback("deleted", event.src_path)

    def watch_directory(self, path: str) -> bool:
        """Watch a directory for changes"""
        try:
            watch = self.observer.schedule(self, path, recursive=True)
            self.watch_paths[path] = watch
            logger.info(f"Watching directory: {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to watch directory {path}: {e}")
            return False

    def start(self):
        """Start monitoring"""
        if not self.observer.is_alive():
            self.observer.start()
            logger.info("File monitor started")

    def stop(self):
        """Stop monitoring"""
        if self.observer.is_alive():
            self.observer.stop()
            self.observer.join()
            logger.info("File monitor stopped")
