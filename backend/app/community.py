from sqlalchemy.orm import Session
from . import models, schemas

def create_post(db: Session, user_id: int, post: schemas.CommunityPostCreate):
    db_post = models.CommunityPost(
        user_id=user_id,
        title=post.title,
        content=post.content,
        category=post.category,
        is_anonymous=post.is_anonymous
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    
    # Get author name (anonymous if requested)
    author_name = "Anonymous" if post.is_anonymous else db.query(models.User).filter(models.User.id == user_id).first().username
    
    return {
        "id": db_post.id,
        "title": db_post.title,
        "content": db_post.content,
        "author": author_name,
        "category": db_post.category,
        "created_at": db_post.created_at,
        "likes": db_post.likes,
        "comment_count": 0
    }