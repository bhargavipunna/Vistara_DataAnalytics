"""
SQLAlchemy Models for Vistara Admin Panel
"""
from sqlalchemy import Column, String, Text, Boolean, Integer, Date, DateTime, DECIMAL, BigInteger, JSON, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class NewsArticle(Base):
    __tablename__ = 'news_articles'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category = Column(String(100), nullable=False)
    title = Column(Text, nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    excerpt = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    image_url = Column(Text)
    date = Column(Date, nullable=True, server_default=func.current_date())
    featured = Column(Boolean, default=False)
    published = Column(Boolean, default=False)
    student_name = Column(String(255))
    location = Column(String(255))
    program = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            'id': str(self.id),
            'category': self.category,
            'title': self.title,
            'slug': self.slug,
            'excerpt': self.excerpt,
            'content': self.content,
            'image_url': self.image_url,
            'date': self.date.isoformat() if self.date else None,
            'featured': self.featured,
            'published': self.published,
            'student_name': self.student_name,
            'location': self.location,
            'program': self.program,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class TeamMember(Base):
    __tablename__ = 'team_members'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    role = Column(String(255), nullable=False)
    bio = Column(Text)
    image_url = Column(Text)
    email = Column(String(255))
    phone = Column(String(50))
    linkedin_url = Column(Text)
    twitter_url = Column(Text)
    order_index = Column(Integer, default=0)
    category = Column(String(50), default='Core Team')
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'role': self.role,
            'bio': self.bio,
            'image_url': self.image_url,
            'email': self.email,
            'phone': self.phone,
            'linkedin_url': self.linkedin_url,
            'twitter_url': self.twitter_url,
            'order_index': self.order_index,
            'category': self.category,
            'active': self.active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Partner(Base):
    __tablename__ = 'partners'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    type = Column(String(100), nullable=False)
    logo_url = Column(Text)
    website_url = Column(Text)
    description = Column(Text)
    since = Column(String(50))
    featured = Column(Boolean, default=False)
    active = Column(Boolean, default=True)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'type': self.type,
            'logo_url': self.logo_url,
            'website_url': self.website_url,
            'description': self.description,
            'since': self.since,
            'featured': self.featured,
            'active': self.active,
            'order_index': self.order_index,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class JobPosting(Base):
    __tablename__ = 'job_postings'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    department = Column(String(100), nullable=False)
    location = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)
    experience = Column(String(100))
    description = Column(Text, nullable=False)
    responsibilities = Column(JSON)
    requirements = Column(JSON)
    benefits = Column(JSON)
    salary = Column(String(100))
    requisition_id = Column(String(20), unique=True, nullable=False)
    work_mode = Column(String(50), default='Hybrid')
    posted_date = Column(Date, nullable=False, server_default=func.current_date())
    closing_date = Column(Date)
    active = Column(Boolean, default=True)
    featured = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            'id': str(self.id),
            'title': self.title,
            'department': self.department,
            'location': self.location,
            'type': self.type,
            'experience': self.experience,
            'description': self.description,
            'responsibilities': self.responsibilities,
            'requirements': self.requirements,
            'benefits': self.benefits,
            'salary': self.salary,
            'requisition_id': self.requisition_id,
            'work_mode': self.work_mode,
            'posted_date': self.posted_date.isoformat() if self.posted_date else None,
            'closing_date': self.closing_date.isoformat() if self.closing_date else None,
            'active': self.active,
            'featured': self.featured,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class UploadedFile(Base):
    __tablename__ = 'uploaded_files'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False)
    file_path = Column(Text, nullable=False)
    file_size = Column(BigInteger)
    mime_type = Column(String(100))
    storage_type = Column(String(50), default='local')
    s3_url = Column(Text)
    uploaded_by = Column(String(255))
    entity_type = Column(String(100))
    entity_id = Column(UUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def to_dict(self):
        return {
            'id': str(self.id),
            'original_filename': self.original_filename,
            'stored_filename': self.stored_filename,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'storage_type': self.storage_type,
            's3_url': self.s3_url,
            'uploaded_by': self.uploaded_by,
            'entity_type': self.entity_type,
            'entity_id': str(self.entity_id) if self.entity_id else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class School(Base):
    __tablename__ = 'schools'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ac_name = Column(String(255), nullable=False)
    mandal_name = Column(String(255), nullable=False)
    udise_code = Column(String(20), nullable=False, unique=True)
    school_name = Column(String(500), nullable=False)
    category = Column(String(50), nullable=False)
    management = Column(String(100), nullable=False)
    location_type = Column(String(50), nullable=False)
    enrolment_boys = Column(Integer, default=0)
    enrolment_girls = Column(Integer, default=0)
    enrolment_total = Column(Integer, default=0)
    latitude = Column(Numeric(10, 5))
    longitude = Column(Numeric(10, 5))
    remarks = Column(Text)
    image_url = Column(Text)
    active = Column(Boolean, default=True)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            'id': str(self.id),
            'ac_name': self.ac_name,
            'mandal_name': self.mandal_name,
            'udise_code': self.udise_code,
            'school_name': self.school_name,
            'category': self.category,
            'management': self.management,
            'location_type': self.location_type,
            'enrolment_boys': self.enrolment_boys or 0,
            'enrolment_girls': self.enrolment_girls or 0,
            'enrolment_total': self.enrolment_total or 0,
            'latitude': float(self.latitude) if self.latitude else None,
            'longitude': float(self.longitude) if self.longitude else None,
            'remarks': self.remarks,
            'image_url': self.image_url,
            'active': self.active,
            'order_index': self.order_index,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class FormSubmission(Base):
    """Generic form submissions (contact, newsletter, volunteer, etc.)"""
    __tablename__ = 'form_submissions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    form_type = Column(String(50), nullable=False)  # contact, newsletter, volunteer, donation
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(50))
    subject = Column(String(255))
    category = Column(String(100))
    message = Column(Text)
    data = Column(JSON)  # Extra form-specific data
    status = Column(String(50), default='new')  # new, read, responded, archived
    notes = Column(Text)  # Admin notes
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            'id': str(self.id),
            'form_type': self.form_type,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'subject': self.subject,
            'category': self.category,
            'message': self.message,
            'data': self.data,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class JobApplication(Base):
    """Job applications submitted via the careers page"""
    __tablename__ = 'job_applications'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    applicant_id = Column(String(20), unique=True)
    job_id = Column(UUID(as_uuid=True), nullable=False)
    job_title = Column(String(255), nullable=False)
    requisition_id = Column(String(20))
    department = Column(String(100))
    location = Column(String(255))
    employment_type = Column(String(50))
    work_mode = Column(String(50))
    # Personal details
    name = Column(String(255), nullable=False)
    first_name = Column(String(255))
    last_name = Column(String(255))
    middle_name = Column(String(255))
    email = Column(String(255), nullable=False)
    phone = Column(String(50))
    current_city = Column(String(255))
    current_state = Column(String(255))
    date_of_birth = Column(Date)
    gender = Column(String(20))
    # Professional info
    total_experience = Column(String(50))
    relevant_experience = Column(String(50))
    experience_years = Column(String(50))
    current_organization = Column(String(255))
    current_designation = Column(String(255))
    current_ctc = Column(String(100))
    expected_ctc = Column(String(100))
    notice_period = Column(String(100))
    expected_salary = Column(String(100))
    # Education
    highest_qualification = Column(String(100))
    degree = Column(String(255))
    specialization = Column(String(255))
    college = Column(String(500))
    graduation_year = Column(Integer)
    percentage_cgpa = Column(String(50))
    # Resume & links
    resume_url = Column(Text)
    cover_letter = Column(Text)
    linkedin_url = Column(Text)
    portfolio_url = Column(Text)
    github_url = Column(Text)
    # Role questions
    why_interested = Column(Text)
    relevant_experience_summary = Column(Text)
    key_strengths = Column(Text)
    # Eligibility
    authorized_to_work = Column(Boolean)
    willing_to_relocate = Column(Boolean)
    previously_interviewed = Column(Boolean)
    referred_by_employee = Column(Boolean)
    referrer_name = Column(String(255))
    referrer_id = Column(String(100))
    # Declarations
    declaration_accurate = Column(Boolean, default=False)
    declaration_consent = Column(Boolean, default=False)
    declaration_false_info = Column(Boolean, default=False)
    # Status
    status = Column(String(50), default='submitted')
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            'id': str(self.id),
            'applicant_id': self.applicant_id,
            'job_id': str(self.job_id),
            'job_title': self.job_title,
            'requisition_id': self.requisition_id,
            'department': self.department,
            'location': self.location,
            'employment_type': self.employment_type,
            'work_mode': self.work_mode,
            'name': self.name,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'middle_name': self.middle_name,
            'email': self.email,
            'phone': self.phone,
            'current_city': self.current_city,
            'current_state': self.current_state,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender,
            'total_experience': self.total_experience,
            'relevant_experience': self.relevant_experience,
            'experience_years': self.experience_years,
            'current_organization': self.current_organization,
            'current_designation': self.current_designation,
            'current_ctc': self.current_ctc,
            'expected_ctc': self.expected_ctc,
            'notice_period': self.notice_period,
            'expected_salary': self.expected_salary,
            'highest_qualification': self.highest_qualification,
            'degree': self.degree,
            'specialization': self.specialization,
            'college': self.college,
            'graduation_year': self.graduation_year,
            'percentage_cgpa': self.percentage_cgpa,
            'resume_url': self.resume_url,
            'cover_letter': self.cover_letter,
            'linkedin_url': self.linkedin_url,
            'portfolio_url': self.portfolio_url,
            'github_url': self.github_url,
            'why_interested': self.why_interested,
            'relevant_experience_summary': self.relevant_experience_summary,
            'key_strengths': self.key_strengths,
            'authorized_to_work': self.authorized_to_work,
            'willing_to_relocate': self.willing_to_relocate,
            'previously_interviewed': self.previously_interviewed,
            'referred_by_employee': self.referred_by_employee,
            'referrer_name': self.referrer_name,
            'referrer_id': self.referrer_id,
            'declaration_accurate': self.declaration_accurate,
            'declaration_consent': self.declaration_consent,
            'declaration_false_info': self.declaration_false_info,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class MediaCoverage(Base):
    """Media coverage articles"""
    __tablename__ = 'media_coverage'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(String(50), nullable=False)  # Print, Online, TV, Radio
    publication = Column(String(255), nullable=False)
    title = Column(Text, nullable=False)
    date = Column(String(100))
    link = Column(Text)
    active = Column(Boolean, default=True)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            'id': str(self.id),
            'type': self.type,
            'publication': self.publication,
            'title': self.title,
            'date': self.date,
            'link': self.link,
            'active': self.active,
            'order_index': self.order_index,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ImpactMetric(Base):
    __tablename__ = 'impact_metrics'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    metric_name = Column(String(255), nullable=False)
    metric_value = Column(DECIMAL(15, 2), nullable=False)
    metric_unit = Column(String(50))
    category = Column(String(100))
    description = Column(Text)
    display_order = Column(Integer, default=0)
    active = Column(Boolean, default=True)
    recorded_at = Column(Date, server_default=func.current_date())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            'id': str(self.id),
            'metric_name': self.metric_name,
            'metric_value': float(self.metric_value),
            'metric_unit': self.metric_unit,
            'category': self.category,
            'description': self.description,
            'display_order': self.display_order,
            'active': self.active,
            'recorded_at': self.recorded_at.isoformat() if self.recorded_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
