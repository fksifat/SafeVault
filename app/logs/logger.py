"""Logger setup for SafeVault"""

import logging
import os
from pathlib import Path


def setup_logger(name: str = "safevault", log_dir: str = None) -> logging.Logger:
    """Setup logger for SafeVault"""
    if log_dir is None:
        log_dir = os.path.join(os.path.dirname(__file__), "../../logs")

    Path(log_dir).mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # File handler
    log_file = os.path.join(log_dir, "safevault.log")
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def get_logger(name: str = "safevault") -> logging.Logger:
    """Get logger instance"""
    return logging.getLogger(name)
