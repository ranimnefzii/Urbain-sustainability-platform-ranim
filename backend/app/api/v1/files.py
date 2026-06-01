"""
File Upload Routes - Urbain Sustainability System
Gestion de fichiers avec upload, validation et stockage
"""

import structlog
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.api.deps import get_current_user
from app.services.file_service import FileService
from app.core.exceptions import FileUploadError, ValidationError

logger = structlog.get_logger()
router = APIRouter()


@router.post("/upload/image", summary="Upload an image file",
             description="Upload an image (jpg, png, gif, webp, svg) with automatic thumbnail generation")
async def upload_image(
    file: UploadFile = File(..., description="Image file to upload"),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = FileService(db)
    result = await service.upload_image(file)
    return {"success": True, "message": "Image uploaded successfully", "data": result}


@router.post("/upload/document", summary="Upload a document file",
             description="Upload a document (pdf, doc, xls, txt, csv)")
async def upload_document(
    file: UploadFile = File(..., description="Document file to upload"),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = FileService(db)
    result = await service.upload_document(file)
    return {"success": True, "message": "Document uploaded successfully", "data": result}


@router.post("/upload/profile-picture", summary="Upload profile picture",
             description="Upload a profile picture image, automatically resized to 256x256")
async def upload_profile_picture(
    file: UploadFile = File(..., description="Profile picture image"),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = FileService(db)
    result = await service.upload_image(file, subdir="profiles", resize=(256, 256))
    return {"success": True, "message": "Profile picture uploaded", "data": result}


@router.get("/files/{file_id}", summary="Get file information",
            description="Retrieve metadata and URL for an uploaded file")
async def get_file(
    file_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = FileService(db)
    result = await service.get_file_info(file_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    return {"success": True, "message": "File info retrieved", "data": result}


@router.delete("/files/{file_id}", summary="Delete a file",
               description="Delete an uploaded file from storage")
async def delete_file(
    file_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = FileService(db)
    result = await service.delete_file(file_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    return {"success": True, "message": "File deleted successfully", "data": None}
