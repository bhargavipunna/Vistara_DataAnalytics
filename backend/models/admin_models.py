"""
SQLAlchemy Models for Vistara Admin Panel
"""
from sqlalchemy import Column, String, Text, Boolean, Integer, Date, DateTime, DECIMAL, BigInteger, JSON
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
    name = Column(String(255), nullable=False)
    location = Column(String(255), nullable=False)
    district = Column(String(255), nullable=False)
    state = Column(String(100), default='Telangana')
    students = Column(Integer, default=0)
    image_url = Column(Text)
    description = Column(Text)
    programs_active = Column(JSON)
    needs_funding = Column(Boolean, default=True)
    adoption_year = Column(Integer)
    active = Column(Boolean, default=True)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'location': self.location,
            'district': self.district,
            'state': self.state,
            'students': self.students,
            'image_url': self.image_url,
            'description': self.description,
            'programs_active': self.programs_active or [],
            'needs_funding': self.needs_funding,
            'adoption_year': self.adoption_year,
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
