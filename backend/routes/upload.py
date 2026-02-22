"""
File Upload API Routes
Supports local storage and AWS S3 (configurable)
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel
import os
import uuid
from pathlib import Path
import mimetypes
from datetime import datetime
from models import get_db
from models.admin_models import UploadedFile
import boto3
from botocore.exceptions import ClientError

router = APIRouter(prefix="/api/upload", tags=["upload"])

# Configuration
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
USE_S3 = os.getenv("USE_S3", "false").lower() == "true"
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET = os.getenv("S3_BUCKET_NAME")

# Ensure upload directory exists
Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

# Allowed file types
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp", "image/svg+xml"}
ALLOWED_DOCUMENT_TYPES = {"application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Response schema
class FileUploadResponse(BaseModel):
    id: str
    original_filename: str
    stored_filename: str
    file_url: str
    file_size: int
    mime_type: str
    storage_type: str

def get_s3_client():
    """Get configured S3 client"""
    if not USE_S3:
        return None
    return boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=AWS_REGION
    )

def upload_to_s3(file_path: str, filename: str) -> Optional[str]:
    """Upload file to S3 and return URL"""
    try:
        s3_client = get_s3_client()
        if not s3_client or not S3_BUCKET:
            return None
        
        s3_key = f"uploads/{datetime.now().year}/{datetime.now().month}/{filename}"
        s3_client.upload_file(file_path, S3_BUCKET, s3_key)
        
        # Generate URL
        url = f"https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"
        return url
    except ClientError as e:
        print(f"S3 upload failed: {e}")
        return None

def validate_file(file: UploadFile, allowed_types: set) -> None:
    """Validate file type and size"""
    # Check file type
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(allowed_types)}"
        )
    
    # Check file size (read first 10MB to check)
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to start
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )

@router.post("/image", response_model=FileUploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    entity_type: Optional[str] = Form(None),
    entity_id: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Upload an image file"""
    validate_file(file, ALLOWED_IMAGE_TYPES)
    
    # Generate unique filename
    file_ext = Path(file.filename).suffix
    stored_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, stored_filename)
    
    # Save file locally
    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Get file size
    file_size = os.path.getsize(file_path)
    
    # Upload to S3 if configured
    s3_url = None
    storage_type = "local"
    if USE_S3:
        s3_url = upload_to_s3(file_path, stored_filename)
        if s3_url:
            storage_type = "s3"
    
    # Save file record to database
    db_file = UploadedFile(
        original_filename=file.filename,
        stored_filename=stored_filename,
        file_path=file_path,
        file_size=file_size,
        mime_type=file.content_type,
        storage_type=storage_type,
        s3_url=s3_url,
        entity_type=entity_type,
        entity_id=entity_id
    )
    
    db.add(db_file)
    
    try:
        db.commit()
        db.refresh(db_file)
    except Exception as e:
        db.rollback()
        # Clean up file
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Failed to save file record: {str(e)}")
    
    # Generate file URL
    if storage_type == "s3" and s3_url:
        file_url = s3_url
    else:
        file_url = f"/uploads/{stored_filename}"
    
    return {
        "id": str(db_file.id),
        "original_filename": db_file.original_filename,
        "stored_filename": db_file.stored_filename,
        "file_url": file_url,
        "file_size": db_file.file_size,
        "mime_type": db_file.mime_type,
        "storage_type": db_file.storage_type
    }

@router.post("/document", response_model=FileUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    entity_type: Optional[str] = Form(None),
    entity_id: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Upload a document file"""
    validate_file(file, ALLOWED_DOCUMENT_TYPES)
    
    # Generate unique filename
    file_ext = Path(file.filename).suffix
    stored_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, stored_filename)
    
    # Save file locally
    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Get file size
    file_size = os.path.getsize(file_path)
    
    # Upload to S3 if configured
    s3_url = None
    storage_type = "local"
    if USE_S3:
        s3_url = upload_to_s3(file_path, stored_filename)
        if s3_url:
            storage_type = "s3"
    
    # Save file record to database
    db_file = UploadedFile(
        original_filename=file.filename,
        stored_filename=stored_filename,
        file_path=file_path,
        file_size=file_size,
        mime_type=file.content_type,
        storage_type=storage_type,
        s3_url=s3_url,
        entity_type=entity_type,
        entity_id=entity_id
    )
    
    db.add(db_file)
    
    try:
        db.commit()
        db.refresh(db_file)
    except Exception as e:
        db.rollback()
        # Clean up file
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Failed to save file record: {str(e)}")
    
    # Generate file URL
    if storage_type == "s3" and s3_url:
        file_url = s3_url
    else:
        file_url = f"/uploads/{stored_filename}"
    
    return {
        "id": str(db_file.id),
        "original_filename": db_file.original_filename,
        "stored_filename": db_file.stored_filename,
        "file_url": file_url,
        "file_size": db_file.file_size,
        "mime_type": db_file.mime_type,
        "storage_type": db_file.storage_type
    }

@router.get("/files")
def get_uploaded_files(
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get list of uploaded files with optional filters"""
    query = db.query(UploadedFile)
    
    if entity_type:
        query = query.filter(UploadedFile.entity_type == entity_type)
    if entity_id:
        query = query.filter(UploadedFile.entity_id == entity_id)
    
    files = query.order_by(UploadedFile.created_at.desc()).offset(skip).limit(limit).all()
    return [f.to_dict() for f in files]

@router.delete("/{file_id}", status_code=204)
def delete_file(file_id: str, db: Session = Depends(get_db)):
    """Delete an uploaded file"""
    db_file = db.query(UploadedFile).filter(UploadedFile.id == file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Delete from S3 if applicable
    if db_file.storage_type == "s3" and USE_S3:
        try:
            s3_client = get_s3_client()
            if s3_client and S3_BUCKET:
                # Extract key from URL or use stored filename
                s3_key = f"uploads/{datetime.now().year}/{datetime.now().month}/{db_file.stored_filename}"
                s3_client.delete_object(Bucket=S3_BUCKET, Key=s3_key)
        except ClientError as e:
            print(f"S3 deletion failed: {e}")
    
    # Delete local file
    if os.path.exists(db_file.file_path):
        try:
            os.remove(db_file.file_path)
        except Exception as e:
            print(f"Local file deletion failed: {e}")
    
    # Delete database record
    try:
        db.delete(db_file)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete file record: {str(e)}")
