"""
Form Submissions + Job Applications CRUD API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr
from datetime import date as DateType
from models import get_db
from models.admin_models import FormSubmission, JobApplication
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/submissions", tags=["submissions"])

# ========================
# Form Submission Schemas
# ========================
class FormSubmissionCreate(BaseModel):
    form_type: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=50)
    subject: Optional[str] = Field(None, max_length=255)
    category: Optional[str] = Field(None, max_length=100)
    message: Optional[str] = None
    data: Optional[dict] = None

class FormSubmissionUpdate(BaseModel):
    status: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None

class FormSubmissionResponse(BaseModel):
    id: str
    form_type: str
    name: str
    email: str
    phone: Optional[str]
    subject: Optional[str]
    category: Optional[str]
    message: Optional[str]
    data: Optional[dict]
    status: str
    notes: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]

# ========================
# Job Application Schemas
# ========================
class JobApplicationCreate(BaseModel):
    job_id: str
    job_title: str = Field(..., min_length=1, max_length=255)
    requisition_id: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    work_mode: Optional[str] = Field(default="Hybrid")
    # Personal details
    name: str = Field(..., min_length=2, max_length=255)
    first_name: str = Field(..., min_length=1, max_length=255)
    last_name: str = Field(..., min_length=1, max_length=255)
    middle_name: Optional[str] = Field(None, max_length=255)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=50)
    current_city: str = Field(..., min_length=1, max_length=255)
    current_state: str = Field(..., min_length=1, max_length=255)
    date_of_birth: Optional[DateType] = None
    gender: Optional[str] = Field(None, max_length=20)
    # Professional info
    total_experience: str = Field(..., max_length=50)
    relevant_experience: str = Field(..., max_length=50)
    notice_period: str = Field(..., max_length=100)
    current_organization: Optional[str] = Field(None, max_length=255)
    current_designation: Optional[str] = Field(None, max_length=255)
    current_ctc: Optional[str] = Field(None, max_length=100)
    expected_ctc: Optional[str] = Field(None, max_length=100)
    experience_years: Optional[str] = Field(None, max_length=50)
    expected_salary: Optional[str] = Field(None, max_length=100)
    # Education
    highest_qualification: str = Field(..., max_length=100)
    degree: str = Field(..., max_length=255)
    specialization: str = Field(..., max_length=255)
    college: str = Field(..., max_length=500)
    graduation_year: int
    percentage_cgpa: Optional[str] = Field(None, max_length=50)
    # Resume & links
    resume_url: Optional[str] = None
    cover_letter: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    github_url: Optional[str] = None
    # Role questions
    why_interested: str = Field(..., max_length=1000)
    relevant_experience_summary: str = Field(..., max_length=2000)
    key_strengths: str = Field(..., max_length=1000)
    # Eligibility
    authorized_to_work: bool
    willing_to_relocate: bool
    previously_interviewed: bool
    referred_by_employee: bool
    referrer_name: Optional[str] = Field(None, max_length=255)
    referrer_id: Optional[str] = Field(None, max_length=100)
    # Declarations
    declaration_accurate: bool
    declaration_consent: bool
    declaration_false_info: bool

class JobApplicationUpdate(BaseModel):
    status: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None

class JobApplicationResponse(BaseModel):
    id: str
    applicant_id: Optional[str]
    job_id: str
    job_title: str
    requisition_id: Optional[str]
    department: Optional[str]
    location: Optional[str]
    employment_type: Optional[str]
    work_mode: Optional[str]
    name: str
    first_name: Optional[str]
    last_name: Optional[str]
    middle_name: Optional[str]
    email: str
    phone: Optional[str]
    current_city: Optional[str]
    current_state: Optional[str]
    date_of_birth: Optional[str]
    gender: Optional[str]
    total_experience: Optional[str]
    relevant_experience: Optional[str]
    experience_years: Optional[str]
    current_organization: Optional[str]
    current_designation: Optional[str]
    current_ctc: Optional[str]
    expected_ctc: Optional[str]
    notice_period: Optional[str]
    expected_salary: Optional[str]
    highest_qualification: Optional[str]
    degree: Optional[str]
    specialization: Optional[str]
    college: Optional[str]
    graduation_year: Optional[int]
    percentage_cgpa: Optional[str]
    resume_url: Optional[str]
    cover_letter: Optional[str]
    linkedin_url: Optional[str]
    portfolio_url: Optional[str]
    github_url: Optional[str]
    why_interested: Optional[str]
    relevant_experience_summary: Optional[str]
    key_strengths: Optional[str]
    authorized_to_work: Optional[bool]
    willing_to_relocate: Optional[bool]
    previously_interviewed: Optional[bool]
    referred_by_employee: Optional[bool]
    referrer_name: Optional[str]
    referrer_id: Optional[str]
    declaration_accurate: Optional[bool]
    declaration_consent: Optional[bool]
    declaration_false_info: Optional[bool]
    status: str
    notes: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]


# ========================================
# Form Submission Endpoints
# ========================================

@router.get("/forms", response_model=List[FormSubmissionResponse])
def get_all_submissions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    form_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all form submissions with optional filters"""
    query = db.query(FormSubmission)
    if form_type:
        query = query.filter(FormSubmission.form_type == form_type)
    if status:
        query = query.filter(FormSubmission.status == status)
    submissions = query.order_by(FormSubmission.created_at.desc()).offset(skip).limit(limit).all()
    return [s.to_dict() for s in submissions]


@router.get("/forms/{submission_id}", response_model=FormSubmissionResponse)
def get_submission(submission_id: str, db: Session = Depends(get_db)):
    """Get a single form submission by ID"""
    sub = db.query(FormSubmission).filter(FormSubmission.id == submission_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")
    return sub.to_dict()


@router.post("/forms", response_model=FormSubmissionResponse, status_code=201)
def create_submission(data: FormSubmissionCreate, db: Session = Depends(get_db)):
    """Submit a form (public endpoint)"""
    db_sub = FormSubmission(**data.dict())
    db.add(db_sub)
    try:
        db.commit()
        db.refresh(db_sub)
        return db_sub.to_dict()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to submit form: {str(e)}")


@router.put("/forms/{submission_id}", response_model=FormSubmissionResponse)
def update_submission(submission_id: str, data: FormSubmissionUpdate, db: Session = Depends(get_db)):
    """Update submission status/notes (admin)"""
    sub = db.query(FormSubmission).filter(FormSubmission.id == submission_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")
    update_data = data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(sub, field, value)
    try:
        db.commit()
        db.refresh(sub)
        return sub.to_dict()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update: {str(e)}")


@router.delete("/forms/{submission_id}", status_code=204)
def delete_submission(submission_id: str, db: Session = Depends(get_db)):
    """Delete a form submission"""
    sub = db.query(FormSubmission).filter(FormSubmission.id == submission_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")
    try:
        db.delete(sub)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete: {str(e)}")


# ========================================
# Job Application Endpoints
# ========================================

@router.get("/applications", response_model=List[JobApplicationResponse])
def get_all_applications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    job_id: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all job applications with optional filters"""
    query = db.query(JobApplication)
    if job_id:
        query = query.filter(JobApplication.job_id == job_id)
    if status:
        query = query.filter(JobApplication.status == status)
    apps = query.order_by(JobApplication.created_at.desc()).offset(skip).limit(limit).all()
    return [a.to_dict() for a in apps]


@router.get("/applications/{application_id}", response_model=JobApplicationResponse)
def get_application(application_id: str, db: Session = Depends(get_db)):
    """Get a single job application by ID"""
    app = db.query(JobApplication).filter(JobApplication.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app.to_dict()


@router.post("/applications", response_model=JobApplicationResponse, status_code=201)
def create_application(data: JobApplicationCreate, db: Session = Depends(get_db)):
    """Submit a job application (public endpoint) — generates applicant_id and sends confirmation email"""
    # Generate applicant_id from sequence
    result = db.execute(text("SELECT nextval('applicant_id_seq')"))
    seq_val = result.scalar()
    applicant_id = f"VST-AP-{str(seq_val).zfill(5)}"

    app_data = data.dict()
    app_data['applicant_id'] = applicant_id

    db_app = JobApplication(**app_data)
    db.add(db_app)
    try:
        db.commit()
        db.refresh(db_app)

        # Send confirmation email (non-blocking — don't fail the request if email fails)
        try:
            from routes.email_service import send_application_confirmation
            send_application_confirmation(
                to_email=data.email,
                applicant_name=f"{data.first_name} {data.last_name}",
                applicant_id=applicant_id,
                job_title=data.job_title,
                requisition_id=data.requisition_id or "",
                department=data.department or "",
                location=data.location or "",
                employment_type=data.employment_type or "",
                work_mode=data.work_mode or "Hybrid",
            )
        except Exception as email_err:
            logger.error(f"Email send failed (non-fatal): {str(email_err)}")

        return db_app.to_dict()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to submit application: {str(e)}")


@router.put("/applications/{application_id}", response_model=JobApplicationResponse)
def update_application(application_id: str, data: JobApplicationUpdate, db: Session = Depends(get_db)):
    """Update application status/notes (admin)"""
    app = db.query(JobApplication).filter(JobApplication.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    update_data = data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(app, field, value)
    try:
        db.commit()
        db.refresh(app)
        return app.to_dict()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update: {str(e)}")


@router.delete("/applications/{application_id}", status_code=204)
def delete_application(application_id: str, db: Session = Depends(get_db)):
    """Delete a job application"""
    app = db.query(JobApplication).filter(JobApplication.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    try:
        db.delete(app)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete: {str(e)}")


@router.get("/forms/types/list")
def get_form_types(db: Session = Depends(get_db)):
    """Get list of unique form types"""
    types = db.query(FormSubmission.form_type).distinct().all()
    return [t[0] for t in types if t[0]]


@router.get("/applications/statuses/list")
def get_application_statuses():
    """Get list of possible application statuses"""
    return ["new", "reviewing", "shortlisted", "interview_scheduled", "interview_completed", "offer_extended", "hired", "rejected", "withdrawn"]
