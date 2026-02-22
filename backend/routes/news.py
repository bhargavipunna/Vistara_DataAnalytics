"""
News Articles CRUD API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import date as DateType
from models import get_db
from models.admin_models import NewsArticle
import re

router = APIRouter(prefix="/api/news", tags=["news"])

# Pydantic schemas
class NewsArticleCreate(BaseModel):
    category: str = Field(..., min_length=1, max_length=100)
    title: str = Field(..., min_length=1)
    slug: str = Field(..., min_length=1, max_length=255)
    excerpt: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    image_url: Optional[str] = None
    date: DateType | None = None
    featured: bool = False
    published: bool = False
    student_name: Optional[str] = None
    location: Optional[str] = None
    program: Optional[str] = None

class NewsArticleUpdate(BaseModel):
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    title: Optional[str] = Field(None, min_length=1)
    slug: Optional[str] = Field(None, min_length=1, max_length=255)
    excerpt: Optional[str] = Field(None, min_length=1)
    content: Optional[str] = Field(None, min_length=1)
    image_url: Optional[str] = None
    date: DateType | None = None
    featured: Optional[bool] = None
    published: Optional[bool] = None
    student_name: Optional[str] = None
    location: Optional[str] = None
    program: Optional[str] = None

class NewsArticleResponse(BaseModel):
    id: str
    category: str
    title: str
    slug: str
    excerpt: str
    content: str
    image_url: Optional[str]
    date: Optional[str]
    featured: bool
    published: bool
    student_name: Optional[str]
    location: Optional[str]
    program: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]

# Helper functions
def generate_slug(title: str) -> str:
    """Generate URL-friendly slug from title"""
    slug = title.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')

# CRUD Endpoints

@router.get("/", response_model=List[NewsArticleResponse])
def get_all_news(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = None,
    published: Optional[bool] = None,
    featured: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get all news articles with optional filters"""
    query = db.query(NewsArticle)
    
    if category:
        query = query.filter(NewsArticle.category == category)
    if published is not None:
        query = query.filter(NewsArticle.published == published)
    if featured is not None:
        query = query.filter(NewsArticle.featured == featured)
    
    articles = query.order_by(NewsArticle.date.desc()).offset(skip).limit(limit).all()
    return [article.to_dict() for article in articles]


@router.get("/slug/{slug}", response_model=NewsArticleResponse)
def get_news_by_slug(slug: str, db: Session = Depends(get_db)):
    """Get a single news article by slug"""
    article = db.query(NewsArticle).filter(NewsArticle.slug == slug).first()
    if not article:
        raise HTTPException(status_code=404, detail="News article not found")
    return article.to_dict()


@router.get("/{article_id}", response_model=NewsArticleResponse)
def get_news_by_id(article_id: str, db: Session = Depends(get_db)):
    """Get a single news article by ID"""
    article = db.query(NewsArticle).filter(NewsArticle.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="News article not found")
    return article.to_dict()


@router.post("/", response_model=NewsArticleResponse, status_code=201)
def create_news(article: NewsArticleCreate, db: Session = Depends(get_db)):
    """Create a new news article"""
    # Check if slug already exists
    existing = db.query(NewsArticle).filter(NewsArticle.slug == article.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Slug already exists")
    
    # Create new article
    db_article = NewsArticle(**article.dict())
    db.add(db_article)
    
    try:
        db.commit()
        db.refresh(db_article)
        return db_article.to_dict()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create article: {str(e)}")


@router.put("/{article_id}", response_model=NewsArticleResponse)
def update_news(article_id: str, article: NewsArticleUpdate, db: Session = Depends(get_db)):
    """Update an existing news article"""
    db_article = db.query(NewsArticle).filter(NewsArticle.id == article_id).first()
    if not db_article:
        raise HTTPException(status_code=404, detail="News article not found")
    
    # Check slug uniqueness if it's being updated
    if article.slug and article.slug != db_article.slug:
        existing = db.query(NewsArticle).filter(NewsArticle.slug == article.slug).first()
        if existing:
            raise HTTPException(status_code=400, detail="Slug already exists")
    
    # Update fields
    update_data = article.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_article, field, value)
    
    try:
        db.commit()
        db.refresh(db_article)
        return db_article.to_dict()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update article: {str(e)}")


@router.delete("/{article_id}", status_code=204)
def delete_news(article_id: str, db: Session = Depends(get_db)):
    """Delete a news article"""
    db_article = db.query(NewsArticle).filter(NewsArticle.id == article_id).first()
    if not db_article:
        raise HTTPException(status_code=404, detail="News article not found")
    
    try:
        db.delete(db_article)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete article: {str(e)}")


@router.get("/categories/list")
def get_categories(db: Session = Depends(get_db)):
    """Get list of all unique categories"""
    categories = db.query(NewsArticle.category).distinct().all()
    return [cat[0] for cat in categories if cat[0]]


@router.post("/generate-slug")
def create_slug(title: str = Query(..., min_length=1)):
    """Generate a slug from a title"""
    return {"slug": generate_slug(title)}
