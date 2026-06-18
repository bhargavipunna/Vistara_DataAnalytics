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
    ac_name: str = Field(..., min_length=1, max_length=255)
    mandal_name: str = Field(..., min_length=1, max_length=255)
    udise_code: str = Field(..., min_length=1, max_length=20)
    school_name: str = Field(..., min_length=1, max_length=500)
    category: str = Field(..., min_length=1, max_length=50)
    management: str = Field(..., min_length=1, max_length=100)
    location_type: str = Field(..., min_length=1, max_length=50)
    enrolment_boys: int = Field(0, ge=0)
    enrolment_girls: int = Field(0, ge=0)
    enrolment_total: int = Field(0, ge=0)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    remarks: Optional[str] = None
    image_url: Optional[str] = None
    active: bool = True
    order_index: int = Field(0, ge=0)

class SchoolUpdate(BaseModel):
    ac_name: Optional[str] = Field(None, min_length=1, max_length=255)
    mandal_name: Optional[str] = Field(None, min_length=1, max_length=255)
    udise_code: Optional[str] = Field(None, min_length=1, max_length=20)
    school_name: Optional[str] = Field(None, min_length=1, max_length=500)
    category: Optional[str] = Field(None, min_length=1, max_length=50)
    management: Optional[str] = Field(None, min_length=1, max_length=100)
    location_type: Optional[str] = Field(None, min_length=1, max_length=50)
    enrolment_boys: Optional[int] = Field(None, ge=0)
    enrolment_girls: Optional[int] = Field(None, ge=0)
    enrolment_total: Optional[int] = Field(None, ge=0)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    remarks: Optional[str] = None
    image_url: Optional[str] = None
    active: Optional[bool] = None
    order_index: Optional[int] = Field(None, ge=0)

class SchoolResponse(BaseModel):
    id: str
    ac_name: str
    mandal_name: str
    udise_code: str
    school_name: str
    category: str
    management: str
    location_type: str
    enrolment_boys: int
    enrolment_girls: int
    enrolment_total: int
    latitude: Optional[float]
    longitude: Optional[float]
    remarks: Optional[str]
    image_url: Optional[str]
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
    ac_name: Optional[str] = None,
    mandal_name: Optional[str] = None,
    category: Optional[str] = None,
    management: Optional[str] = None,
    location_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all schools with optional filters"""
    query = db.query(School)
    
    if active is not None:
        query = query.filter(School.active == active)
    if ac_name:
        query = query.filter(School.ac_name == ac_name)
    if mandal_name:
        query = query.filter(School.mandal_name == mandal_name)
    if category:
        query = query.filter(School.category == category)
    if management:
        query = query.filter(School.management == management)
    if location_type:
        query = query.filter(School.location_type == location_type)
    
    schools = query.order_by(School.order_index.asc()).offset(skip).limit(limit).all()
    return [school.to_dict() for school in schools]


@router.get("/ac-names/list")
def get_ac_names(db: Session = Depends(get_db)):
    """Get list of all unique AC names"""
    ac_names = db.query(School.ac_name).distinct().all()
    return [a[0] for a in ac_names if a[0]]


@router.get("/mandals/list")
def get_mandals(db: Session = Depends(get_db)):
    """Get list of all unique mandal names"""
    mandals = db.query(School.mandal_name).distinct().all()
    return [m[0] for m in mandals if m[0]]


@router.get("/categories/list")
def get_categories(db: Session = Depends(get_db)):
    """Get list of all unique categories"""
    categories = db.query(School.category).distinct().all()
    return [c[0] for c in categories if c[0]]


@router.get("/managements/list")
def get_managements(db: Session = Depends(get_db)):
    """Get list of all unique management types"""
    managements = db.query(School.management).distinct().all()
    return [m[0] for m in managements if m[0]]


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
