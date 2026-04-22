from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, default="")
    is_psychologist = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    appointments = relationship("Appointment", back_populates="user", cascade="all, delete-orphan")
    post_likes = relationship("PostLike", back_populates="user", cascade="all, delete-orphan")

class Psychologist(Base):
    __tablename__ = "psychologists"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    license_number = Column(String, unique=True, nullable=False)
    specialization = Column(String, default="General Psychology")
    bio = Column(Text, default="")
    consultation_fee = Column(Integer, default=1500)
    is_available = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User")
    appointments = relationship("Appointment", back_populates="psychologist", cascade="all, delete-orphan")

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, default="")
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"))
    role = Column(String)  # 'user' or 'assistant'
    content = Column(Text)
    sentiment = Column(String, default="neutral")
    risk_detected = Column(Boolean, default=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")

class Appointment(Base):
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    psychologist_id = Column(Integer, ForeignKey("psychologists.id"))
    scheduled_time = Column(DateTime(timezone=True), nullable=False)
    duration = Column(Integer, default=60)
    status = Column(String, default="scheduled")
    meeting_link = Column(String, default="")
    notes = Column(Text, default="")
    
    # Relationships
    user = relationship("User", back_populates="appointments")
    psychologist = relationship("Psychologist", back_populates="appointments")

class CommunityPost(Base):
    __tablename__ = "community_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    is_anonymous = Column(Boolean, default=True)
    category = Column(String, default="General")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    likes = Column(Integer, default=0)
    
    # Relationships
    comments = relationship("CommunityComment", back_populates="post", cascade="all, delete-orphan")
    likes_relation = relationship("PostLike", back_populates="post", cascade="all, delete-orphan")

class CommunityComment(Base):
    __tablename__ = "community_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("community_posts.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text, nullable=False)
    is_anonymous = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    post = relationship("CommunityPost", back_populates="comments")

class PostLike(Base):
    __tablename__ = "post_likes"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("community_posts.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    post = relationship("CommunityPost", back_populates="likes_relation")
    user = relationship("User", back_populates="post_likes")
    
    __table_args__ = (UniqueConstraint('post_id', 'user_id', name='unique_post_user_like'),)

class WellnessContent(Base):
    __tablename__ = "wellness_content"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content_english = Column(Text, default="")
    content_urdu = Column(Text, default="")
    category = Column(String, default="Wellness")
    content_type = Column(String, default="article")
    tags = Column(JSON, default=list)
    views = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())