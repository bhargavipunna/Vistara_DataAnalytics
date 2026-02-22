"""
Careers/Job Postings CRUD API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import date as DateType
from models import get_db
from models.admin_models import JobPosting

router = APIRouter(prefix="/api/careers", tags=["careers"])

# Pydantic schemas
class JobPostingCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    department: str = Field(..., min_length=1, max_length=100)
    location: str = Field(..., min_length=1, max_length=255)
    type: str = Field(..., min_length=1, max_length=50)
    experience: Optional[str] = Field(None, max_length=100)
    description: str = Field(..., min_length=1)
    responsibilities: Optional[List[str]] = None
    requirements: Optional[List[str]] = None
    benefits: Optional[List[str]] = None
    salary: Optional[str] = Field(None, max_length=100)
    posted_date: DateType | None = None
    closing_date: DateType | None = None
    active: bool = True
    featured: bool = False

class JobPostingUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    department: Optional[str] = Field(None, min_length=1, max_length=100)
    location: Optional[str] = Field(None, min_length=1, max_length=255)
    type: Optional[str] = Field(None, min_length=1, max_length=50)
    experience: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, min_length=1)
    responsibilities: Optional[List[str]] = None
    requirements: Optional[List[str]] = None
    benefits: Optional[List[str]] = None
    salary: Optional[str] = Field(None, max_length=100)
    posted_date: DateType | None = None
    closing_date: DateType | None = None
    active: Optional[bool] = None
    featured: Optional[bool] = None

class JobPostingResponse(BaseModel):
    id: str
    title: str
    department: str
    location: str
    type: str
    experience: Optional[str]
    description: str
    responsibilities: Optional[List[str]]
    requirements: Optional[List[str]]
    benefits: Optional[List[str]]
    salary: Optional[str]
    posted_date: Optional[str]
    closing_date: Optional[str]
    active: bool
    featured: bool
    created_at: Optional[str]
    updated_at: Optional[str]

# CRUD Endpoints

@router.get("/", response_model=List[JobPostingResponse])
def get_all_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    type: Optional[str] = None,
    department: Optional[str] = None,
    active: Optional[bool] = None,
    featured: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get all job postings with optional filters"""
    query = db.query(JobPosting)
    
    if type:
        query = query.filter(JobPosting.type == type)
    if department:
        query = query.filter(JobPosting.department == department)
    if active is not None:
        query = query.filter(JobPosting.active == active)
    if featured is not None:
        query = query.filter(JobPosting.featured == featured)
    
    jobs = query.order_by(JobPosting.posted_date.desc()).offset(skip).limit(limit).all()
    return [job.to_dict() for job in jobs]


@router.get("/{job_id}", response_model=JobPostingResponse)
def get_job(job_id: str, db: Session = Depends(get_db)):
    """Get a single job posting by ID"""
    job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")
    return job.to_dict()


@router.post("/", response_model=JobPostingResponse, status_code=201)
def create_job(job: JobPostingCreate, db: Session = Depends(get_db)):
    """Create a new job posting"""
    db_job = JobPosting(**job.dict())
    db.add(db_job)
    
    try:
        db.commit()
        db.refresh(db_job)
        return db_job.to_dict()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create job posting: {str(e)}")


@router.put("/{job_id}", response_model=JobPostingResponse)
def update_job(job_id: str, job: JobPostingUpdate, db: Session = Depends(get_db)):
    """Update an existing job posting"""
    db_job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    if not db_job:
        raise HTTPException(status_code=404, detail="Job posting not found")
    
    # Update fields
    update_data = job.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_job, field, value)
    
    try:
        db.commit()
        db.refresh(db_job)
        return db_job.to_dict()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update job posting: {str(e)}")


@router.delete("/{job_id}", status_code=204)
def delete_job(job_id: str, db: Session = Depends(get_db)):
    """Delete a job posting"""
    db_job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    if not db_job:
        raise HTTPException(status_code=404, detail="Job posting not found")
    
    try:
        db.delete(db_job)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete job posting: {str(e)}")


@router.get("/departments/list")
def get_departments(db: Session = Depends(get_db)):
    """Get list of all unique departments"""
    departments = db.query(JobPosting.department).distinct().all()
    return [dept[0] for dept in departments if dept[0]]


@router.get("/types/list")
def get_job_types(db: Session = Depends(get_db)):
    """Get list of all unique job types"""
    types = db.query(JobPosting.type).distinct().all()
    return [t[0] for t in types if t[0]]
