"""Utility helpers for SafeVault"""

import hashlib
import os
from pathlib import Path


def get_file_hash(
    file_path: str, algorithm: str = "sha256", chunk_size: int = 8192
) -> str:
    """Calculate file hash"""
    hash_obj = hashlib.new(algorithm)

    with open(file_path, "rb") as f:
        while chunk := f.read(chunk_size):
            hash_obj.update(chunk)

    return hash_obj.hexdigest()


def format_file_size(size_bytes: int) -> str:
    """Format file size to human readable format"""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def ensure_path_exists(path: str) -> bool:
    """Ensure path exists"""
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        print(f"Error creating path {path}: {e}")
        return False


def get_directory_size(path: str) -> int:
    """Get total size of directory"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if os.path.exists(filepath):
                total_size += os.path.getsize(filepath)
    return total_size


def get_file_count(path: str) -> int:
    """Get total file count in directory"""
    count = 0
    for dirpath, dirnames, filenames in os.walk(path):
        count += len(filenames)
    return count
