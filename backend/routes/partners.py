"""
Partners CRUD API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl
from models import get_db
from models.admin_models import Partner

router = APIRouter(prefix="/api/partners", tags=["partners"])

# Pydantic schemas
class PartnerCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    type: str = Field(..., min_length=1, max_length=100)
    logo_url: Optional[str] = None
    website_url: Optional[str] = None
    description: Optional[str] = None
    since: Optional[str] = Field(None, max_length=50)
    featured: bool = False
    active: bool = True
    order_index: int = Field(0, ge=0)

class PartnerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    type: Optional[str] = Field(None, min_length=1, max_length=100)
    logo_url: Optional[str] = None
    website_url: Optional[str] = None
    description: Optional[str] = None
    since: Optional[str] = Field(None, max_length=50)
    featured: Optional[bool] = None
    active: Optional[bool] = None
    order_index: Optional[int] = Field(None, ge=0)

class PartnerResponse(BaseModel):
    id: str
    name: str
    type: str
    logo_url: Optional[str]
    website_url: Optional[str]
    description: Optional[str]
    since: Optional[str]
    featured: bool
    active: bool
    order_index: int
    created_at: Optional[str]
    updated_at: Optional[str]

# CRUD Endpoints

@router.get("/", response_model=List[PartnerResponse])
def get_all_partners(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    type: Optional[str] = None,
    active: Optional[bool] = None,
    featured: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get all partners with optional filters"""
    query = db.query(Partner)
    
    if type:
        query = query.filter(Partner.type == type)
    if active is not None:
        query = query.filter(Partner.active == active)
    if featured is not None:
        query = query.filter(Partner.featured == featured)
    
    partners = query.order_by(Partner.order_index.asc()).offset(skip).limit(limit).all()
    return [partner.to_dict() for partner in partners]


@router.get("/{partner_id}", response_model=PartnerResponse)
def get_partner(partner_id: str, db: Session = Depends(get_db)):
    """Get a single partner by ID"""
    partner = db.query(Partner).filter(Partner.id == partner_id).first()
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")
    return partner.to_dict()


@router.post("/", response_model=PartnerResponse, status_code=201)
def create_partner(partner: PartnerCreate, db: Session = Depends(get_db)):
    """Create a new partner"""
    db_partner = Partner(**partner.dict())
    db.add(db_partner)
    
    try:
        db.commit()
        db.refresh(db_partner)
        return db_partner.to_dict()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create partner: {str(e)}")


@router.put("/{partner_id}", response_model=PartnerResponse)
def update_partner(partner_id: str, partner: PartnerUpdate, db: Session = Depends(get_db)):
    """Update an existing partner"""
    db_partner = db.query(Partner).filter(Partner.id == partner_id).first()
    if not db_partner:
        raise HTTPException(status_code=404, detail="Partner not found")
    
    # Update fields
    update_data = partner.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_partner, field, value)
    
    try:
        db.commit()
        db.refresh(db_partner)
        return db_partner.to_dict()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update partner: {str(e)}")


@router.delete("/{partner_id}", status_code=204)
def delete_partner(partner_id: str, db: Session = Depends(get_db)):
    """Delete a partner"""
    db_partner = db.query(Partner).filter(Partner.id == partner_id).first()
    if not db_partner:
        raise HTTPException(status_code=404, detail="Partner not found")
    
    try:
        db.delete(db_partner)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete partner: {str(e)}")


@router.get("/types/list")
def get_partner_types(db: Session = Depends(get_db)):
    """Get list of all unique partner types"""
    types = db.query(Partner.type).distinct().all()
    return [t[0] for t in types if t[0]]


@router.patch("/{partner_id}/reorder")
def reorder_partner(
    partner_id: str,
    new_order: int = Query(..., ge=0),
    db: Session = Depends(get_db)
):
    """Update the order index of a partner"""
    db_partner = db.query(Partner).filter(Partner.id == partner_id).first()
    if not db_partner:
        raise HTTPException(status_code=404, detail="Partner not found")
    
    db_partner.order_index = new_order
    
    try:
        db.commit()
        db.refresh(db_partner)
        return db_partner.to_dict()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to reorder partner: {str(e)}")
