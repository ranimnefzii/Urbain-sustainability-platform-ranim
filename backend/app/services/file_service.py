"""
File Service - Urbain Sustainability System
Service de gestion de fichiers avec upload, validation et stockage
"""

import os
import uuid
import mimetypes
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path

import structlog
from PIL import Image
import io

from app.core.exceptions import (
    FileUploadError,
    ValidationError,
    NotFoundError,
    ExternalServiceError
)
from app.core.config import settings
from app.utils.constants import FileUploadDefaults
from app.utils.validators import validate_image_file
from app.services.base import BaseService

logger = structlog.get_logger()


class FileService(BaseService):
    """
    Service de gestion de fichiers avec support multi-stockage
    Gère l'upload, validation, thumbnail et stockage local/S3
    """

    ALLOWED_EXTENSIONS = {
        "images": {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"},
        "documents": {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".txt", ".csv"},
        "videos": {".mp4", ".webm", ".avi", ".mov"},
        "audio": {".mp3", ".wav", ".ogg", ".m4a"}
    }

    MAX_FILE_SIZES = {
        "image": FileUploadDefaults.MAX_IMAGE_SIZE_MB * 1024 * 1024,
        "document": FileUploadDefaults.MAX_DOCUMENT_SIZE_MB * 1024 * 1024,
        "video": 50 * 1024 * 1024,
        "audio": 20 * 1024 * 1024
    }

    def __init__(self, db):
        super().__init__(db)
        self._storage_type = "local"
        self._ensure_upload_dirs()

    def _ensure_upload_dirs(self) -> None:
        dirs = [
            settings.UPLOAD_DIR,
            os.path.join(settings.UPLOAD_DIR, "images"),
            os.path.join(settings.UPLOAD_DIR, "documents"),
            os.path.join(settings.UPLOAD_DIR, "videos"),
            os.path.join(settings.UPLOAD_DIR, "audio"),
            os.path.join(settings.UPLOAD_DIR, "thumbnails"),
            os.path.join(settings.UPLOAD_DIR, "temp")
        ]
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)

    def _generate_filename(self, original_filename: str) -> Tuple[str, str]:
        ext = Path(original_filename).suffix.lower() if Path(original_filename).suffix else ""
        unique_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime("%Y%m%d")
        filename = f"{timestamp}_{unique_id}{ext}"
        return filename, ext

    def _detect_file_type(self, filename: str, mime_type: Optional[str] = None) -> str:
        ext = Path(filename).suffix.lower()
        if ext in self.ALLOWED_EXTENSIONS["images"]:
            return "image"
        if ext in self.ALLOWED_EXTENSIONS["documents"]:
            return "document"
        if ext in self.ALLOWED_EXTENSIONS["videos"]:
            return "video"
        if ext in self.ALLOWED_EXTENSIONS["audio"]:
            return "audio"
        return "other"

    def _get_upload_subdir(self, file_type: str) -> str:
        subdirs = {
            "image": "images",
            "document": "documents",
            "video": "videos",
            "audio": "audio"
        }
        return subdirs.get(file_type, "other")

    async def validate_file(
        self,
        file_data: bytes,
        filename: str,
        allowed_types: Optional[List[str]] = None,
        max_size: Optional[int] = None
    ) -> Dict[str, Any]:
        try:
            if not file_data or len(file_data) == 0:
                raise ValidationError("File data is empty")

            ext = Path(filename).suffix.lower()
            file_type = self._detect_file_type(filename)

            if allowed_types:
                if ext not in allowed_types and filename.split(".")[-1].lower() not in [t.split("/")[-1] for t in allowed_types]:
                    raise ValidationError(f"File type {ext} is not allowed. Allowed: {allowed_types}")

            if not max_size:
                max_size = self.MAX_FILE_SIZES.get(file_type, settings.MAX_FILE_SIZE)

            if len(file_data) > max_size:
                max_size_mb = max_size / (1024 * 1024)
                raise ValidationError(
                    f"File size ({len(file_data) / (1024 * 1024):.2f} MB) exceeds maximum "
                    f"allowed size ({max_size_mb:.1f} MB)"
                )

            if file_type == "image" and ext not in self.ALLOWED_EXTENSIONS["images"]:
                raise ValidationError(f"Image format {ext} is not supported")

            mime_type, _ = mimetypes.guess_type(filename)
            if mime_type and mime_type.startswith("image/"):
                try:
                    img = Image.open(io.BytesIO(file_data))
                    img.verify()
                except Exception:
                    raise ValidationError("File is not a valid image")

            result = {
                "valid": True,
                "file_type": file_type,
                "extension": ext,
                "mime_type": mime_type,
                "size_bytes": len(file_data),
                "size_mb": round(len(file_data) / (1024 * 1024), 2),
                "filename": filename
            }

            await self.log_operation("validate_file", {
                "filename": filename,
                "file_type": file_type,
                "size": len(file_data)
            })

            return result

        except ValidationError:
            raise
        except Exception as e:
            await self.log_error("validate_file", e)
            raise ValidationError(f"File validation failed: {str(e)}")

    async def upload_file(
        self,
        file_data: bytes,
        filename: str,
        subdir: Optional[str] = None,
        allowed_types: Optional[List[str]] = None,
        max_size: Optional[int] = None,
        generate_thumb: bool = False
    ) -> Dict[str, Any]:
        try:
            validation = await self.validate_file(file_data, filename, allowed_types, max_size)

            new_filename, ext = self._generate_filename(filename)
            file_type = validation["file_type"]

            if not subdir:
                subdir = self._get_upload_subdir(file_type)

            upload_dir = os.path.join(settings.UPLOAD_DIR, subdir)
            os.makedirs(upload_dir, exist_ok=True)

            file_path = os.path.join(upload_dir, new_filename)
            with open(file_path, "wb") as f:
                f.write(file_data)

            file_url = f"/uploads/{subdir}/{new_filename}"

            thumbnail_url = None
            if generate_thumb and file_type == "image":
                try:
                    thumbnail_result = await self.generate_thumbnail(file_data, new_filename, subdir)
                    thumbnail_url = thumbnail_result.get("thumbnail_url")
                except Exception as e:
                    logger.warning("Thumbnail generation failed", error=str(e))

            result = {
                "filename": new_filename,
                "original_filename": filename,
                "file_url": file_url,
                "thumbnail_url": thumbnail_url,
                "file_type": file_type,
                "mime_type": validation["mime_type"],
                "size_bytes": len(file_data),
                "size_mb": round(len(file_data) / (1024 * 1024), 2),
                "extension": ext,
                "subdir": subdir,
                "storage_type": self._storage_type,
                "uploaded_at": datetime.now(timezone.utc).isoformat()
            }

            await self.log_operation("upload_file", {
                "filename": new_filename,
                "file_type": file_type,
                "size": len(file_data),
                "subdir": subdir
            })

            return result

        except ValidationError:
            raise
        except Exception as e:
            await self.log_error("upload_file", e)
            raise FileUploadError(f"File upload failed: {str(e)}")

    async def upload_image(
        self,
        file_data: bytes,
        filename: str,
        generate_thumb: bool = True
    ) -> Dict[str, Any]:
        return await self.upload_file(
            file_data=file_data,
            filename=filename,
            subdir="images",
            allowed_types=list(FileUploadDefaults.ALLOWED_IMAGE_TYPES),
            max_size=self.MAX_FILE_SIZES["image"],
            generate_thumb=generate_thumb
        )

    async def upload_document(
        self,
        file_data: bytes,
        filename: str
    ) -> Dict[str, Any]:
        return await self.upload_file(
            file_data=file_data,
            filename=filename,
            subdir="documents",
            allowed_types=list(FileUploadDefaults.ALLOWED_DOCUMENT_TYPES),
            max_size=self.MAX_FILE_SIZES["document"]
        )

    async def get_file(self, filename: str, subdir: str = "images") -> Dict[str, Any]:
        try:
            file_path = os.path.join(settings.UPLOAD_DIR, subdir, filename)

            if not os.path.exists(file_path):
                raise NotFoundError(f"File not found: {filename}")

            stat = os.stat(file_path)
            file_type = self._detect_file_type(filename)
            mime_type, _ = mimetypes.guess_type(filename)

            result = {
                "filename": filename,
                "file_path": file_path,
                "file_url": f"/uploads/{subdir}/{filename}",
                "file_type": file_type,
                "mime_type": mime_type,
                "size_bytes": stat.st_size,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "created_at": datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc).isoformat(),
                "modified_at": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
                "subdir": subdir,
                "exists": True
            }

            return result

        except NotFoundError:
            raise
        except Exception as e:
            await self.log_error("get_file", e)
            raise NotFoundError(f"Failed to retrieve file: {filename}")

    async def delete_file(self, filename: str, subdir: str = "images") -> Dict[str, str]:
        try:
            file_path = os.path.join(settings.UPLOAD_DIR, subdir, filename)

            if not os.path.exists(file_path):
                raise NotFoundError(f"File not found: {filename}")

            os.remove(file_path)

            thumb_path = os.path.join(settings.UPLOAD_DIR, "thumbnails", filename)
            if os.path.exists(thumb_path):
                os.remove(thumb_path)

            await self.log_operation("delete_file", {
                "filename": filename,
                "subdir": subdir
            })

            return {"message": f"File {filename} deleted successfully"}

        except NotFoundError:
            raise
        except Exception as e:
            await self.log_error("delete_file", e)
            raise FileUploadError(f"Failed to delete file: {filename}")

    async def get_file_url(self, filename: str, subdir: str = "images") -> str:
        file_path = os.path.join(settings.UPLOAD_DIR, subdir, filename)
        if not os.path.exists(file_path):
            raise NotFoundError(f"File not found: {filename}")
        return f"/uploads/{subdir}/{filename}"

    async def generate_thumbnail(
        self,
        file_data: bytes,
        filename: str,
        subdir: str = "images",
        size: Tuple[int, int] = (200, 200)
    ) -> Dict[str, Any]:
        try:
            img = Image.open(io.BytesIO(file_data))

            img_format = img.format or "JPEG"
            if img_format == "PNG":
                img = img.convert("RGBA")
            else:
                img = img.convert("RGB")

            img.thumbnail(size, Image.Resampling.LANCZOS)

            thumb_dir = os.path.join(settings.UPLOAD_DIR, "thumbnails")
            os.makedirs(thumb_dir, exist_ok=True)

            thumb_filename = f"thumb_{filename}"
            thumb_ext = Path(filename).suffix.lower()
            if thumb_ext not in [".jpg", ".jpeg", ".png", ".webp"]:
                thumb_ext = ".jpg"

            thumb_path = os.path.join(thumb_dir, thumb_filename)
            save_format = "JPEG"
            if thumb_ext == ".png":
                save_format = "PNG"
            elif thumb_ext == ".webp":
                save_format = "WEBP"

            img.save(thumb_path, save_format, quality=85)

            thumbnail_url = f"/uploads/thumbnails/{thumb_filename}"

            result = {
                "thumbnail_filename": thumb_filename,
                "thumbnail_url": thumbnail_url,
                "thumbnail_path": thumb_path,
                "original_size": f"{img.size[0]}x{img.size[1]}",
                "size": f"{size[0]}x{size[1]}",
                "format": save_format
            }

            await self.log_operation("generate_thumbnail", {
                "filename": filename,
                "thumbnail": thumb_filename
            })

            return result

        except Exception as e:
            logger.error("Thumbnail generation failed", error=str(e))
            raise FileUploadError(f"Thumbnail generation failed: {str(e)}")

    async def get_file_info(self, filename: str, subdir: str = "images") -> Dict[str, Any]:
        try:
            file_info = await self.get_file(filename, subdir)

            file_path = file_info["file_path"]
            is_image = file_info["file_type"] == "image"

            extra_info = {}
            if is_image:
                try:
                    img = Image.open(file_path)
                    extra_info["image"] = {
                        "width": img.width,
                        "height": img.height,
                        "format": img.format,
                        "mode": img.mode,
                        "aspect_ratio": round(img.width / img.height, 4) if img.height > 0 else 0
                    }
                except Exception as e:
                    logger.warning("Failed to read image info", error=str(e))

            file_info.update(extra_info)
            return file_info

        except NotFoundError:
            raise
        except Exception as e:
            await self.log_error("get_file_info", e)
            raise NotFoundError(f"Failed to get file info: {filename}")
