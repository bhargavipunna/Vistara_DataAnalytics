"""
Schools CRUD API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from models import get_db
from models.admin_models import School

router = APIRouter(prefix="/api/schools", tags=["schools"])

# Pydantic schemas
class SchoolCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    location: str = Field(..., min_length=1, max_length=255)
    district: str = Field(..., min_length=1, max_length=255)
    state: str = Field('Telangana', max_length=100)
    students: int = Field(0, ge=0)
    image_url: Optional[str] = None
    description: Optional[str] = None
    programs_active: Optional[List[str]] = None
    needs_funding: bool = True
    adoption_year: Optional[int] = None
    active: bool = True
    order_index: int = Field(0, ge=0)

class SchoolUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    location: Optional[str] = Field(None, min_length=1, max_length=255)
    district: Optional[str] = Field(None, min_length=1, max_length=255)
    state: Optional[str] = Field(None, max_length=100)
    students: Optional[int] = Field(None, ge=0)
    image_url: Optional[str] = None
    description: Optional[str] = None
    programs_active: Optional[List[str]] = None
    needs_funding: Optional[bool] = None
    adoption_year: Optional[int] = None
    active: Optional[bool] = None
    order_index: Optional[int] = Field(None, ge=0)

class SchoolResponse(BaseModel):
    id: str
    name: str
    location: str
    district: str
    state: str
    students: int
    image_url: Optional[str]
    description: Optional[str]
    programs_active: Optional[List[str]]
    needs_funding: bool
    adoption_year: Optional[int]
    active: bool
    order_index: int
    created_at: Optional[str]
    updated_at: Optional[str]

# CRUD Endpoints

@router.get("/", response_model=List[SchoolResponse])
def get_all_schools(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active: Optional[bool] = None,
    district: Optional[str] = None,
    needs_funding: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get all schools with optional filters"""
    query = db.query(School)
    
    if active is not None:
        query = query.filter(School.active == active)
    if district:
        query = query.filter(School.district == district)
    if needs_funding is not None:
        query = query.filter(School.needs_funding == needs_funding)
    
    schools = query.order_by(School.order_index.asc()).offset(skip).limit(limit).all()
    return [school.to_dict() for school in schools]


@router.get("/{school_id}", response_model=SchoolResponse)
def get_school(school_id: str, db: Session = Depends(get_db)):
    """Get a single school by ID"""
    school = db.query(School).filter(School.id == school_id).first()
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    return school.to_dict()


@router.post("/", response_model=SchoolResponse, status_code=201)
def create_school(school: SchoolCreate, db: Session = Depends(get_db)):
    """Create a new school"""
    db_school = School(**school.dict())
    db.add(db_school)
    
    try:
        db.commit()
        db.refresh(db_school)
        return db_school.to_dict()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create school: {str(e)}")


@router.put("/{school_id}", response_model=SchoolResponse)
def update_school(school_id: str, school: SchoolUpdate, db: Session = Depends(get_db)):
    """Update an existing school"""
    db_school = db.query(School).filter(School.id == school_id).first()
    if not db_school:
        raise HTTPException(status_code=404, detail="School not found")
    
    update_data = school.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_school, field, value)
    
    try:
        db.commit()
        db.refresh(db_school)
        return db_school.to_dict()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update school: {str(e)}")


@router.delete("/{school_id}", status_code=204)
def delete_school(school_id: str, db: Session = Depends(get_db)):
    """Delete a school"""
    db_school = db.query(School).filter(School.id == school_id).first()
    if not db_school:
        raise HTTPException(status_code=404, detail="School not found")
    
    try:
        db.delete(db_school)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete school: {str(e)}")


@router.get("/districts/list")
def get_districts(db: Session = Depends(get_db)):
    """Get list of all unique districts"""
    districts = db.query(School.district).distinct().all()
    return [d[0] for d in districts if d[0]]
