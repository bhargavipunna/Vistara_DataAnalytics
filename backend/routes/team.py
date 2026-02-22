"""
Team Members CRUD API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr
from models import get_db
from models.admin_models import TeamMember

router = APIRouter(prefix="/api/team", tags=["team"])

# Pydantic schemas
class TeamMemberCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    role: str = Field(..., min_length=1, max_length=255)
    bio: Optional[str] = None
    image_url: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    linkedin_url: Optional[str] = None
    twitter_url: Optional[str] = None
    order_index: int = Field(0, ge=0)
    category: str = Field('Core Team', max_length=50)
    active: bool = True

class TeamMemberUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    role: Optional[str] = Field(None, min_length=1, max_length=255)
    bio: Optional[str] = None
    image_url: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    linkedin_url: Optional[str] = None
    twitter_url: Optional[str] = None
    order_index: Optional[int] = Field(None, ge=0)
    category: Optional[str] = Field(None, max_length=50)
    active: Optional[bool] = None

class TeamMemberResponse(BaseModel):
    id: str
    name: str
    role: str
    bio: Optional[str]
    image_url: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    linkedin_url: Optional[str]
    twitter_url: Optional[str]
    order_index: int
    category: str
    active: bool
    created_at: Optional[str]
    updated_at: Optional[str]

# CRUD Endpoints

@router.get("/", response_model=List[TeamMemberResponse])
def get_all_team_members(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active: Optional[bool] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all team members with optional filters"""
    query = db.query(TeamMember)
    
    if active is not None:
        query = query.filter(TeamMember.active == active)
    if category:
        query = query.filter(TeamMember.category == category)
    
    members = query.order_by(TeamMember.order_index.asc()).offset(skip).limit(limit).all()
    return [member.to_dict() for member in members]


@router.get("/{member_id}", response_model=TeamMemberResponse)
def get_team_member(member_id: str, db: Session = Depends(get_db)):
    """Get a single team member by ID"""
    member = db.query(TeamMember).filter(TeamMember.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Team member not found")
    return member.to_dict()


@router.post("/", response_model=TeamMemberResponse, status_code=201)
def create_team_member(member: TeamMemberCreate, db: Session = Depends(get_db)):
    """Create a new team member"""
    db_member = TeamMember(**member.dict())
    db.add(db_member)
    
    try:
        db.commit()
        db.refresh(db_member)
        return db_member.to_dict()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create team member: {str(e)}")


@router.put("/{member_id}", response_model=TeamMemberResponse)
def update_team_member(member_id: str, member: TeamMemberUpdate, db: Session = Depends(get_db)):
    """Update an existing team member"""
    db_member = db.query(TeamMember).filter(TeamMember.id == member_id).first()
    if not db_member:
        raise HTTPException(status_code=404, detail="Team member not found")
    
    # Update fields
    update_data = member.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_member, field, value)
    
    try:
        db.commit()
        db.refresh(db_member)
        return db_member.to_dict()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update team member: {str(e)}")


@router.delete("/{member_id}", status_code=204)
def delete_team_member(member_id: str, db: Session = Depends(get_db)):
    """Delete a team member"""
    db_member = db.query(TeamMember).filter(TeamMember.id == member_id).first()
    if not db_member:
        raise HTTPException(status_code=404, detail="Team member not found")
    
    try:
        db.delete(db_member)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete team member: {str(e)}")


@router.patch("/{member_id}/reorder")
def reorder_team_member(
    member_id: str,
    new_order: int = Query(..., ge=0),
    db: Session = Depends(get_db)
):
    """Update the order index of a team member"""
    db_member = db.query(TeamMember).filter(TeamMember.id == member_id).first()
    if not db_member:
        raise HTTPException(status_code=404, detail="Team member not found")
    
    db_member.order_index = new_order
    
    try:
        db.commit()
        db.refresh(db_member)
        return db_member.to_dict()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to reorder team member: {str(e)}")
