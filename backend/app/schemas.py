from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    role: str = "user"

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: int
    role: str
    is_verified: bool
    created_at: datetime
    profile_picture: Optional[str] = None
    
    class Config:
        from_attributes = True

# Psychologist Registration Schema
class PsychologistRegister(UserCreate):
    role: str = "psychologist"
    specialization: str
    years_of_experience: int
    education: str
    consultation_fee: int
    license_number: str
    bio: Optional[str] = None
    profile_picture: Optional[str] = None

class PsychologistProfileResponse(BaseModel):
    id: int
    user_id: int
    specialization: str
    years_of_experience: int
    education: str
    consultation_fee: int
    bio: Optional[str]
    is_available: bool
    license_number: str
    created_at: datetime
    full_name: str
    email: str
    profile_picture: Optional[str]
    
    class Config:
        from_attributes = True

# Consultation Message Schemas
class ConsultationMessageCreate(BaseModel):
    appointment_id: int
    message: str

class ConsultationMessageResponse(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    message: str
    is_read: bool
    timestamp: datetime
    sender_name: str
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class ChatMessageBase(BaseModel):
    content: str = Field(..., max_length=2000)

class ChatMessageResponse(BaseModel):
    id: int
    role: str
    content: str
    timestamp: datetime
    
    class Config:
        from_attributes = True

class ChatSessionResponse(BaseModel):
    session_id: Optional[int]
    messages: List[ChatMessageResponse]
    sessions: List

class AppointmentCreate(BaseModel):
    psychologist_id: int
    scheduled_time: datetime
    duration: int = 60

class AppointmentResponse(BaseModel):
    id: int
    psychologist_name: str
    scheduled_time: datetime
    status: str
    meeting_link: Optional[str]
    duration: Optional[int] = 60

class CommunityPostCreate(BaseModel):
    title: str = Field(..., max_length=200)
    content: str = Field(..., max_length=5000)
    category: str = "General"
    is_anonymous: bool = True

class CommunityPostResponse(BaseModel):
    id: int
    title: str
    content: str
    author: str
    category: str
    created_at: datetime
    likes: int
    comment_count: int
    is_anonymous: bool = True

class CommunityCommentCreate(BaseModel):
    content: str = Field(..., max_length=1000)
    is_anonymous: bool = True

class CommunityCommentResponse(BaseModel):
    id: int
    content: str
    author: str
    created_at: datetime

class WellnessContentResponse(BaseModel):
    id: int
    title: str
    content: str
    category: str
    content_type: str
    views: int
    image_url: Optional[str] = None

class DashboardStats(BaseModel):
    chat_sessions: int
    total_messages: int
    upcoming_appointments: int
    completed_sessions: int
    community_posts: int
    wellness_score: int