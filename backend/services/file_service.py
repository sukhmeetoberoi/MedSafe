"""
File Service for handling file uploads, storage, and management
"""

import os
import uuid
import aiofiles
import hashlib
from typing import Dict, Any, Optional
from fastapi import UploadFile
from core.config import settings
from core.logging import logger
from models.report import Report

class FileService:
    """Service for managing file uploads and storage"""

    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        self.ensure_upload_directory()

    def ensure_upload_directory(self):
        """Ensure upload directory exists"""
        try:
            os.makedirs(self.upload_dir, exist_ok=True)
            # Create subdirectories for organization
            os.makedirs(os.path.join(self.upload_dir, "temp"), exist_ok=True)
            os.makedirs(os.path.join(self.upload_dir, "processed"), exist_ok=True)
            logger.info(f"Upload directory ensured: {self.upload_dir}")
        except Exception as e:
            logger.error(f"Error creating upload directory: {e}")
            raise

    async def save_uploaded_file(self, file: UploadFile) -> Dict[str, Any]:
        """
        Save uploaded file to storage

        Args:
            file: UploadFile object from FastAPI

        Returns:
            Dictionary with file information
        """
        try:
            # Generate unique filename
            file_ext = os.path.splitext(file.filename)[1].lower()
            unique_filename = f"{uuid.uuid4()}{file_ext}"
            file_path = os.path.join(self.upload_dir, unique_filename)

            # Calculate file hash for integrity checking
            file_hash = await self._calculate_file_hash(file)

            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)

            # Reset file position for any further processing
            await file.seek(0)

            file_info = {
                "filename": unique_filename,
                "original_filename": file.filename,
                "file_path": file_path,
                "file_size": len(content),
                "file_type": file_ext[1:],  # Remove the dot
                "content_type": file.content_type,
                "file_hash": file_hash,
                "upload_path": f"/uploads/{unique_filename}"
            }

            logger.info(f"File saved successfully: {file.filename} -> {unique_filename}")
            return file_info

        except Exception as e:
            logger.error(f"Error saving file {file.filename}: {e}")
            raise

    async def _calculate_file_hash(self, file: UploadFile) -> str:
        """Calculate SHA-256 hash of file for integrity verification"""
        try:
            # Read file in chunks to handle large files
            file.seek(0)
            hash_sha256 = hashlib.sha256()

            while chunk := await file.read(8192):
                hash_sha256.update(chunk)

            # Reset file position
            await file.seek(0)

            return hash_sha256.hexdigest()

        except Exception as e:
            logger.error(f"Error calculating file hash: {e}")
            return ""

    async def delete_file(self, file_path: str) -> bool:
        """
        Delete file from storage

        Args:
            file_path: Path to file to delete

        Returns:
            True if deletion successful, False otherwise
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"File deleted: {file_path}")
                return True
            else:
                logger.warning(f"File not found for deletion: {file_path}")
                return False

        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {e}")
            return False

    async def delete_report_files(self, report: Report) -> bool:
        """
        Delete all files associated with a report

        Args:
            report: Report model instance

        Returns:
            True if deletion successful, False otherwise
        """
        try:
            files_deleted = 0

            # Delete main report file
            if report.file_path and await self.delete_file(report.file_path):
                files_deleted += 1

            # Delete any processed files (if they exist)
            processed_dir = os.path.join(self.upload_dir, "processed")
            if os.path.exists(processed_dir):
                report_pattern = f"{report.filename.split('.')[0]}_*"
                for filename in os.listdir(processed_dir):
                    if filename.startswith(report.filename.split('.')[0]):
                        file_path = os.path.join(processed_dir, filename)
                        if await self.delete_file(file_path):
                            files_deleted += 1

            logger.info(f"Deleted {files_deleted} files for report {report.id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting files for report {report.id}: {e}")
            return False

    async def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a stored file

        Args:
            file_path: Path to file

        Returns:
            File information dictionary or None if file doesn't exist
        """
        try:
            if not os.path.exists(file_path):
                return None

            stat = os.stat(file_path)

            return {
                "file_path": file_path,
                "file_size": stat.st_size,
                "created_at": stat.st_ctime,
                "modified_at": stat.st_mtime,
                "is_accessible": os.access(file_path, os.R_OK)
            }

        except Exception as e:
            logger.error(f"Error getting file info for {file_path}: {e}")
            return None

    def generate_file_url(self, filename: str, expiry_hours: int = 24) -> str:
        """
        Generate a secure URL for file access

        Args:
            filename: Filename to generate URL for
            expiry_hours: URL expiry time in hours

        Returns:
            Secure file URL
        """
        # This is a simple implementation
        # In production, you'd want to use signed URLs with expiry
        return f"/api/files/{filename}"

    async def compress_file_if_needed(self, file_path: str, max_size_mb: int = 5) -> str:
        """
        Compress file if it's too large

        Args:
            file_path: Path to file
            max_size_mb: Maximum file size in MB

        Returns:
            Path to compressed file
        """
        try:
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)

            if file_size_mb <= max_size_mb:
                return file_path

            # Implementation would depend on file type
            # For PDFs, you could use pdf compression libraries
            # For images, you could reduce resolution or quality

            logger.info(f"File {file_path} is {file_size_mb:.2f}MB, compression needed")
            return file_path

        except Exception as e:
            logger.error(f"Error compressing file {file_path}: {e}")
            return file_path

    async def create_file_backup(self, file_path: str) -> Optional[str]:
        """
        Create a backup of the file

        Args:
            file_path: Path to original file

        Returns:
            Path to backup file or None if backup failed
        """
        try:
            backup_dir = os.path.join(self.upload_dir, "backups")
            os.makedirs(backup_dir, exist_ok=True)

            backup_filename = f"backup_{uuid.uuid4()}_{os.path.basename(file_path)}"
            backup_path = os.path.join(backup_dir, backup_filename)

            async with aiofiles.open(file_path, 'rb') as src:
                async with aiofiles.open(backup_path, 'wb') as dst:
                    while chunk := await src.read(8192):
                        await dst.write(chunk)

            logger.info(f"Backup created: {backup_path}")
            return backup_path

        except Exception as e:
            logger.error(f"Error creating backup for {file_path}: {e}")
            return None

    async def cleanup_temp_files(self, max_age_hours: int = 24):
        """
        Clean up temporary files older than specified age

        Args:
            max_age_hours: Maximum age in hours for temp files
        """
        try:
            temp_dir = os.path.join(self.upload_dir, "temp")
            if not os.path.exists(temp_dir):
                return

            import time
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600

            files_deleted = 0
            for filename in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, filename)
                file_age = current_time - os.path.getmtime(file_path)

                if file_age > max_age_seconds:
                    os.remove(file_path)
                    files_deleted += 1

            logger.info(f"Cleaned up {files_deleted} temporary files")

        except Exception as e:
            logger.error(f"Error cleaning up temp files: {e}")

# Singleton instance
file_service = FileService()