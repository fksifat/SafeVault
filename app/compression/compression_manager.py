"""Compression Manager for SafeVault"""

import os
import zipfile
import tarfile
from pathlib import Path
from app.logs import get_logger

logger = get_logger()


class CompressionManager:
    """Manages compression/decompression operations"""

    @staticmethod
    def compress_directory_zip(
        source_dir: str, output_file: str, compression_level: int = 6
    ) -> bool:
        """Compress directory to ZIP file"""
        try:
            with zipfile.ZipFile(
                output_file, "w", zipfile.ZIP_DEFLATED, compresslevel=compression_level
            ) as zipf:
                for root, dirs, files in os.walk(source_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, source_dir)
                        zipf.write(file_path, arcname)

            logger.info(f"Directory compressed to ZIP: {source_dir} -> {output_file}")
            return True

        except Exception as e:
            logger.error(f"ZIP compression failed: {e}")
            return False

    @staticmethod
    def compress_directory_tar_gz(source_dir: str, output_file: str) -> bool:
        """Compress directory to TAR.GZ file"""
        try:
            with tarfile.open(output_file, "w:gz") as tar:
                tar.add(source_dir, arcname=os.path.basename(source_dir))

            logger.info(
                f"Directory compressed to TAR.GZ: {source_dir} -> {output_file}"
            )
            return True

        except Exception as e:
            logger.error(f"TAR.GZ compression failed: {e}")
            return False

    @staticmethod
    def decompress_zip(zip_file: str, output_dir: str) -> bool:
        """Decompress ZIP file"""
        try:
            os.makedirs(output_dir, exist_ok=True)
            with zipfile.ZipFile(zip_file, "r") as zipf:
                zipf.extractall(output_dir)

            logger.info(f"ZIP decompressed: {zip_file} -> {output_dir}")
            return True

        except Exception as e:
            logger.error(f"ZIP decompression failed: {e}")
            return False

    @staticmethod
    def decompress_tar_gz(tar_file: str, output_dir: str) -> bool:
        """Decompress TAR.GZ file"""
        try:
            os.makedirs(output_dir, exist_ok=True)
            with tarfile.open(tar_file, "r:gz") as tar:
                tar.extractall(output_dir)

            logger.info(f"TAR.GZ decompressed: {tar_file} -> {output_dir}")
            return True

        except Exception as e:
            logger.error(f"TAR.GZ decompression failed: {e}")
            return False

    @staticmethod
    def compress_file(file_path: str, output_file: str, format: str = "zip") -> bool:
        """Compress a single file"""
        try:
            if format.lower() == "zip":
                with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zipf:
                    zipf.write(file_path, arcname=os.path.basename(file_path))
            elif format.lower() == "tar.gz":
                with tarfile.open(output_file, "w:gz") as tar:
                    tar.add(file_path, arcname=os.path.basename(file_path))

            logger.info(f"File compressed: {file_path} -> {output_file}")
            return True

        except Exception as e:
            logger.error(f"File compression failed: {e}")
            return False
