"""Encryption Manager for SafeVault"""

import os
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
from app.logs import get_logger

logger = get_logger()


class EncryptionManager:
    """Manages encryption/decryption operations"""

    @staticmethod
    def derive_key(
        password: str, salt: bytes = None, iterations: int = 100000
    ) -> tuple:
        """Derive encryption key from password"""
        if salt is None:
            salt = get_random_bytes(32)

        key = PBKDF2(password, salt, dkLen=32, count=iterations)
        return key, salt

    @staticmethod
    def encrypt_file(file_path: str, password: str, output_path: str = None) -> bool:
        """Encrypt a file"""
        try:
            if output_path is None:
                output_path = file_path + ".encrypted"

            # Derive key from password
            key, salt = EncryptionManager.derive_key(password)

            # Create cipher
            cipher = AES.new(key, AES.MODE_GCM)

            # Read file
            with open(file_path, "rb") as f:
                plaintext = f.read()

            # Encrypt
            ciphertext, tag = cipher.encrypt_and_digest(plaintext)

            # Write encrypted file
            with open(output_path, "wb") as f:
                f.write(salt)  # First 32 bytes: salt
                f.write(cipher.nonce)  # Next 16 bytes: nonce
                f.write(tag)  # Next 16 bytes: tag
                f.write(ciphertext)  # Rest: encrypted data

            logger.info(f"File encrypted: {file_path} -> {output_path}")
            return True

        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            return False

    @staticmethod
    def decrypt_file(
        encrypted_file_path: str, password: str, output_path: str = None
    ) -> bool:
        """Decrypt a file"""
        try:
            if output_path is None:
                output_path = encrypted_file_path.replace(".encrypted", "")

            # Read encrypted file
            with open(encrypted_file_path, "rb") as f:
                salt = f.read(32)
                nonce = f.read(16)
                tag = f.read(16)
                ciphertext = f.read()

            # Derive key from password
            key, _ = EncryptionManager.derive_key(password, salt)

            # Create cipher
            cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)

            # Decrypt
            plaintext = cipher.decrypt_and_verify(ciphertext, tag)

            # Write decrypted file
            with open(output_path, "wb") as f:
                f.write(plaintext)

            logger.info(f"File decrypted: {encrypted_file_path} -> {output_path}")
            return True

        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return False

    @staticmethod
    def encrypt_directory(dir_path: str, password: str, output_dir: str = None) -> dict:
        """Encrypt all files in a directory"""
        if output_dir is None:
            output_dir = dir_path + ".encrypted"

        results = {"success": 0, "failed": 0, "errors": []}

        for root, dirs, files in os.walk(dir_path):
            # Create corresponding directory structure
            rel_path = os.path.relpath(root, dir_path)
            if rel_path == ".":
                target_dir = output_dir
            else:
                target_dir = os.path.join(output_dir, rel_path)

            os.makedirs(target_dir, exist_ok=True)

            # Encrypt files
            for file in files:
                file_path = os.path.join(root, file)
                output_path = os.path.join(target_dir, file + ".encrypted")

                if EncryptionManager.encrypt_file(file_path, password, output_path):
                    results["success"] += 1
                else:
                    results["failed"] += 1
                    results["errors"].append(file_path)

        return results
