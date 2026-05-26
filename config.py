"""Configuration file for SafeVault"""

# Database
DATABASE_PATH = "database/safevault.db"

# Logging
LOG_DIR = "logs"
LOG_LEVEL = "DEBUG"

# Backup
BACKUP_DIR = "backups"
MAX_BACKUP_HISTORY = 10
RETENTION_DAYS = 30

# Scheduler
SCHEDULER_ENABLED = True
SCHEDULER_THREAD_POOL_SIZE = 5

# UI
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700
THEME = "light"

# Compression
COMPRESSION_ENABLED = False
COMPRESSION_FORMAT = "zip"  # 'zip' or 'tar.gz'
COMPRESSION_LEVEL = 6  # 1-9, higher = slower but better compression

# Encryption
ENCRYPTION_ENABLED = False
ENCRYPTION_ALGORITHM = "AES-256"
ENCRYPTION_KEY_ITERATIONS = 100000
