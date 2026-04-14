from sqlalchemy.orm import Session
from . import models, schemas
from typing import Optional, List

def get_content_items(
    db: Session,
    category: Optional[str] = None,
    content_type: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 20,
    skip: int = 0
):
    """Get wellness content items with filters"""
    query = db.query(models.WellnessContent)
    
    if category:
        query = query.filter(models.WellnessContent.category == category)
    
    if content_type:
        query = query.filter(models.WellnessContent.content_type == content_type)
    
    if search:
        query = query.filter(
            (models.WellnessContent.title.ilike(f"%{search}%")) |
            (models.WellnessContent.content_english.ilike(f"%{search}%")) |
            (models.WellnessContent.content_urdu.ilike(f"%{search}%"))
        )
    
    return query.order_by(models.WellnessContent.created_at.desc()).offset(skip).limit(limit).all()

def increment_views(db: Session, content_id: int):
    """Increment view count for content"""
    content = db.query(models.WellnessContent).filter(models.WellnessContent.id == content_id).first()
    if content:
        content.views += 1
        db.commit()
    return content

def get_categories(db: Session) -> List[str]:
    """Get all unique categories"""
    categories = db.query(models.WellnessContent.category).distinct().all()
    return [cat[0] for cat in categories if cat[0]]