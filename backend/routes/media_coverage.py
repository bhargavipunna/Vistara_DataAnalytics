"""
Media Coverage CRUD API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from models import get_db
from models.admin_models import MediaCoverage

router = APIRouter(prefix="/api/media-coverage", tags=["media-coverage"])

# Pydantic schemas
class MediaCoverageCreate(BaseModel):
    type: str = Field(..., min_length=1, max_length=50)
    publication: str = Field(..., min_length=1, max_length=255)
    title: str = Field(..., min_length=1)
    date: Optional[str] = Field(None, max_length=100)
    link: Optional[str] = None
    active: bool = True
    order_index: int = Field(0, ge=0)

class MediaCoverageUpdate(BaseModel):
    type: Optional[str] = Field(None, min_length=1, max_length=50)
    publication: Optional[str] = Field(None, min_length=1, max_length=255)
    title: Optional[str] = Field(None, min_length=1)
    date: Optional[str] = Field(None, max_length=100)
    link: Optional[str] = None
    active: Optional[bool] = None
    order_index: Optional[int] = Field(None, ge=0)

class MediaCoverageResponse(BaseModel):
    id: str
    type: str
    publication: str
    title: str
    date: Optional[str]
    link: Optional[str]
    active: bool
    order_index: int
    created_at: Optional[str]
    updated_at: Optional[str]

# CRUD Endpoints

@router.get("/", response_model=List[MediaCoverageResponse])
def get_all_media_coverage(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active: Optional[bool] = None,
    type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all media coverage items"""
    query = db.query(MediaCoverage)
    if active is not None:
        query = query.filter(MediaCoverage.active == active)
    if type:
        query = query.filter(MediaCoverage.type == type)
    items = query.order_by(MediaCoverage.order_index.asc()).offset(skip).limit(limit).all()
    return [item.to_dict() for item in items]


@router.get("/{item_id}", response_model=MediaCoverageResponse)
def get_media_coverage(item_id: str, db: Session = Depends(get_db)):
    """Get a single media coverage item"""
    item = db.query(MediaCoverage).filter(MediaCoverage.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Media coverage item not found")
    return item.to_dict()


@router.post("/", response_model=MediaCoverageResponse, status_code=201)
def create_media_coverage(data: MediaCoverageCreate, db: Session = Depends(get_db)):
    """Create a new media coverage item"""
    db_item = MediaCoverage(**data.dict())
    db.add(db_item)
    try:
        db.commit()
        db.refresh(db_item)
        return db_item.to_dict()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create: {str(e)}")


@router.put("/{item_id}", response_model=MediaCoverageResponse)
def update_media_coverage(item_id: str, data: MediaCoverageUpdate, db: Session = Depends(get_db)):
    """Update an existing media coverage item"""
    db_item = db.query(MediaCoverage).filter(MediaCoverage.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Media coverage item not found")
    update_data = data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_item, field, value)
    try:
        db.commit()
        db.refresh(db_item)
        return db_item.to_dict()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update: {str(e)}")


@router.delete("/{item_id}", status_code=204)
def delete_media_coverage(item_id: str, db: Session = Depends(get_db)):
    """Delete a media coverage item"""
    db_item = db.query(MediaCoverage).filter(MediaCoverage.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Media coverage item not found")
    try:
        db.delete(db_item)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete: {str(e)}")
