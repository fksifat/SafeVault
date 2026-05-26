# SafeVault - Cross-platform Backup Application

A lightweight, reliable backup tool that runs in the background and allows users to schedule, execute, and manage backups with ease.

## Features

- **Backup Job Management**: Create and manage backup jobs with custom settings
- **Scheduled Backups**: Automatic backup scheduling (Manual, Daily, Weekly, Monthly)
- **Incremental Backups**: Only backup changed files to save time and storage
- **Restore System**: Browse and restore from backup snapshots
- **Background Service**: Run as a system tray application
- **Compression**: Optional ZIP compression for backup files
- **Encryption**: Optional AES-256 encryption for sensitive backups
- **Cross-Platform**: Works on Windows and Linux

## Project Structure

```
SafeVault/
├── app/
│   ├── ui/                  # User Interface (PySide6)
│   │   ├── dashboard/       # Dashboard widget
│   │   ├── backup_jobs/     # Backup job management
│   │   ├── restore/         # Restore functionality
│   │   └── settings/        # Settings page
│   ├── backup_engine/       # Backup operations
│   ├── scheduler/           # Job scheduling (APScheduler)
│   ├── restore_engine/      # Restore operations
│   ├── compression/         # Compression utilities
│   ├── encryption/          # Encryption utilities
│   ├── monitoring/          # File monitoring (watchdog)
│   ├── database/            # SQLite database management
│   ├── logs/                # Logging utilities
│   └── utils/               # Helper functions
├── database/                # SQLite database files
├── logs/                    # Application logs
├── backups/                 # Backup storage
├── tests/                   # Unit tests
├── requirements.txt         # Python dependencies
├── main.py                  # Entry point
└── README.md               # This file
```

## Technology Stack

| Component       | Technology        |
| --------------- | ----------------- |
| Language        | Python 3.9+       |
| UI Framework    | PySide6           |
| Database        | SQLite            |
| Scheduler       | APScheduler       |
| File Monitoring | watchdog          |
| Encryption      | PyCryptodome      |
| Compression     | zipfile / tarfile |
| Packaging       | PyInstaller       |

## Installation

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Setup

1. **Clone or navigate to the project directory**

   ```bash
   cd SafeVault
   ```

2. **Create a virtual environment** (recommended)

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

```bash
python main.py
```

The application will:

1. Initialize the database
2. Start the backup scheduler
3. Display the main window with system tray icon

## Usage

### Creating a Backup Job

1. Open the **Backup Jobs** tab
2. Enter job details:
   - Job name (unique identifier)
   - Source folder(s) to backup
   - Destination folder for backups
   - Schedule type (Manual, Daily, Weekly, Monthly)
   - Enable compression and/or encryption (optional)
3. Click **Save Job**

### Running a Backup

- **Manual**: Click "Run Now" on the Dashboard
- **Scheduled**: Backups run automatically at configured times
- Monitor progress on the Dashboard

### Restoring Backups

1. Open the **Restore** tab
2. Select backup snapshot from the history
3. Choose files/folders to restore
4. Select restore destination (original or custom location)
5. Click **Restore**

### Settings

Configure in the **Settings** tab:

- Run at startup
- Enable notifications
- Backup retention period
- Compression level
- Theme preference

## Database Schema

### backup_jobs

- id: Job ID (primary key)
- name: Unique job name
- source_path: Path to files to backup
- destination_path: Backup destination
- schedule_type: Manual/Daily/Weekly/Monthly
- compression_enabled: Enable ZIP compression
- encryption_enabled: Enable AES-256 encryption
- created_at: Creation timestamp
- updated_at: Last update timestamp

### backup_history

- id: History record ID
- job_id: Reference to backup job
- backup_time: When backup was performed
- status: Success/Failed/In Progress
- files_copied: Number of files backed up
- backup_size: Total backup size
- duration: Backup duration in seconds
- error_message: Error details if failed

### file_metadata

- id: Metadata record ID
- job_id: Reference to backup job
- file_path: Full path to file
- file_hash: SHA256 hash for change detection
- modified_time: File modification time
- backup_version: Full/Incremental version
- file_size: File size in bytes

## Development

### Running Tests

```bash
python -m pytest tests/
```

### Code Structure

Core modules are organized by functionality:

- **Database**: `app/database/db_manager.py` - All database operations
- **Backup Engine**: `app/backup_engine/backup_manager.py` - Backup logic
- **Scheduler**: `app/scheduler/backup_scheduler.py` - Job scheduling
- **Restore**: `app/restore_engine/restore_manager.py` - Restore operations
- **Encryption**: `app/encryption/encryption_manager.py` - AES-256 encryption
- **Compression**: `app/compression/compression_manager.py` - ZIP/TAR compression
- **UI**: `app/ui/` - PySide6 interface components

## Building Executables

### Windows (EXE)

```bash
pyinstaller --onefile --windowed --icon=icon.ico main.py
```

### Linux (AppImage)

```bash
pip install appimage-builder
appimage-builder --recipe appimage-recipe.yml
```

## Roadmap

### MVP (Current)

- ✅ Backup job management
- ✅ Scheduled backups
- ✅ Incremental backup logic
- ✅ Restore system
- ✅ Compression and encryption
- ✅ Cross-platform support

### Phase 2

- Cloud backup integration
- NAS support
- Deduplication
- System image backup
- Ransomware protection

### Phase 3

- Remote monitoring
- Multi-device dashboard
- AI-powered scheduling
- Mobile companion app

## Troubleshooting

### Database locked errors

- Close other instances of the application
- Delete `database/safevault.db` and restart (will recreate)

### Permission denied errors

- Run with elevated privileges (sudo on Linux)
- Check folder permissions

### Backup fails to start

- Check logs: `logs/safevault.log`
- Verify source/destination paths exist
- Ensure disk space available

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Support

For issues, questions, or suggestions:

- Check the documentation
- Review existing issues
- Create a new issue with detailed information

## Author

SafeVault Development Team

---

**Version**: 1.0.0-MVP  
**Last Updated**: 2026-05-25
