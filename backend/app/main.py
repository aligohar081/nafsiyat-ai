from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
import os
import uuid

from .database import engine, get_db, Base
from . import models, schemas, auth, chatbot, teleconsultation, community

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Nafsiyat AI", description="Mental Wellness Platform", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ Helper Functions for Sample Data ============

def create_sample_psychologists(db: Session):
    """Create sample psychologists - safely without duplicates"""
    try:
        # Check if psychologists already exist
        existing = db.query(models.Psychologist).first()
        if existing:
            print("✅ Psychologists already exist, skipping creation")
            return
            
        psychologists_data = [
            {
                "username": "dr_ahmed_khan",
                "email": "dr.ahmed@nafsiyat.com",
                "full_name": "Dr. Ahmed Khan",
                "password": "doctor123",
                "license": "PMC-12345",
                "specialization": "Clinical Psychology",
                "bio": "PhD in Clinical Psychology with 10+ years of experience. Specializes in anxiety, depression, and trauma.",
                "fee": 2500
            },
            {
                "username": "dr_fatima_ali",
                "email": "dr.fatima@nafsiyat.com",
                "full_name": "Dr. Fatima Ali",
                "password": "doctor123",
                "license": "PMC-12346",
                "specialization": "Counseling Psychology",
                "bio": "Expert in relationship counseling, stress management, and adolescent mental health.",
                "fee": 2000
            },
            {
                "username": "dr_imran_raza",
                "email": "dr.imran@nafsiyat.com",
                "full_name": "Dr. Imran Raza",
                "password": "doctor123",
                "license": "PMC-12347",
                "specialization": "Psychiatry",
                "bio": "Medical doctor specializing in mental health. Provides medication management and therapy.",
                "fee": 3000
            }
        ]
        
        for doc in psychologists_data:
            # Check if user already exists
            existing_user = db.query(models.User).filter((models.User.username == doc["username"]) | (models.User.email == doc["email"])).first()
            if existing_user:
                print(f"⚠️ User {doc['username']} already exists, skipping")
                continue
                
            user = models.User(
                email=doc["email"],
                username=doc["username"],
                hashed_password=auth.get_password_hash(doc["password"]),
                full_name=doc["full_name"],
                is_psychologist=True,
                is_verified=True
            )
            db.add(user)
            db.flush()
            
            psychologist = models.Psychologist(
                user_id=user.id,
                license_number=doc["license"],
                specialization=doc["specialization"],
                bio=doc["bio"],
                consultation_fee=doc["fee"],
                is_available=True
            )
            db.add(psychologist)
        
        db.commit()
        print("✅ Sample psychologists created!")
    except Exception as e:
        print(f"Error creating psychologists: {e}")
        db.rollback()

def create_sample_wellness_content(db: Session):
    """Create sample wellness content"""
    try:
        existing = db.query(models.WellnessContent).first()
        if existing:
            print("✅ Wellness content already exists, skipping creation")
            return
            
        sample_contents = [
            {
                "title": "Managing Anxiety - A CBT Approach",
                "content_english": """<h2>Understanding Anxiety</h2>
<p>Anxiety is your body's natural response to stress. While some anxiety is normal, excessive anxiety can interfere with daily life.</p>
<h3>CBT Techniques for Anxiety:</h3>
<ul>
<li><strong>Identify Anxious Thoughts:</strong> Write down what you're worried about</li>
<li><strong>Challenge Negative Patterns:</strong> Ask yourself "Is this thought realistic?"</li>
<li><strong>Practice Deep Breathing:</strong> Inhale for 4 counts, hold for 4, exhale for 4</li>
<li><strong>Use Grounding Techniques:</strong> Name 5 things you can see, 4 you can touch, 3 you can hear, 2 you can smell, 1 you can taste</li>
</ul>
<p>Remember: Anxiety is treatable. With practice, these techniques can help you manage anxious feelings.</p>""",
                "content_urdu": """<h2>پریشانی کو سمجھنا</h2>
<p>پریشانی تناؤ کے لیے آپ کے جسم کا قدرتی ردعمل ہے۔</p>
<h3>پریشانی کے لیے CBT تکنیکیں:</h3>
<ul>
<li><strong>پریشان کن خیالات کی نشاندہی کریں</strong></li>
<li><strong>منفی پیٹرن کو چیلنج کریں</strong></li>
<li><strong>گہری سانس لیں</strong></li>
</ul>""",
                "category": "Anxiety",
                "content_type": "article",
                "tags": ["anxiety", "cbt", "breathing"]
            },
            {
                "title": "5-Minute Mindfulness Meditation",
                "content_english": """<h2>Quick Mindfulness Exercise</h2>
<p>Find a comfortable position. Close your eyes if you feel comfortable.</p>
<h3>Step-by-Step Guide:</h3>
<ol>
<li>Take 3 deep breaths, feeling your belly rise and fall</li>
<li>Notice the sensation of air entering and leaving your nostrils</li>
<li>When your mind wanders, gently bring it back to your breath</li>
<li>Expand your awareness to include sounds around you</li>
<li>Notice any sensations in your body without judging them</li>
</ol>
<p>Practice this for 5 minutes daily to reduce stress and increase focus.</p>""",
                "content_urdu": """<h2>فوری ذہنی سکون کی ورزش</h2>
<p>آرام دہ پوزیشن میں بیٹھیں۔</p>
<h3>مرحلہ وار رہنمائی:</h3>
<ol>
<li>3 گہری سانسیں لیں</li>
<li>ہوا کے نتھنوں سے اندر اور باہر جانے کے احساس کو دیکھیں</li>
<li>جب ذہن بھٹکے تو آہستہ سے اسے سانسوں پر لے آئیں</li>
</ol>""",
                "category": "Mindfulness",
                "content_type": "guide",
                "tags": ["mindfulness", "meditation", "stress relief"]
            },
            {
                "title": "Understanding Depression",
                "content_english": """<h2>What is Depression?</h2>
<p>Depression is more than just feeling sad. It's a medical condition that affects your mood, thoughts, and physical health.</p>
<h3>Common Signs of Depression:</h3>
<ul>
<li>Persistent sad, anxious, or "empty" mood</li>
<li>Loss of interest in activities you once enjoyed</li>
<li>Changes in appetite or weight</li>
<li>Trouble sleeping or sleeping too much</li>
<li>Loss of energy or increased fatigue</li>
<li>Difficulty concentrating or making decisions</li>
</ul>
<h3>When to Seek Help:</h3>
<p>If you've experienced these symptoms for more than two weeks, please reach out to a mental health professional.</p>""",
                "content_urdu": """<h2>ڈپریشن کیا ہے؟</h2>
<p>ڈپریشن صرف اداسی محسوس کرنے سے زیادہ ہے۔</p>
<h3>ڈپریشن کی عام علامات:</h3>
<ul>
<li>مسلسل اداس، پریشان، یا "خالی" موڈ</li>
<li>ان سرگرمیوں میں دلچسپی کا خاتمہ</li>
<li>بھوک یا وزن میں تبدیلی</li>
<li>نیند آنے میں دشواری</li>
</ul>""",
                "category": "Depression",
                "content_type": "article",
                "tags": ["depression", "mental health", "support"]
            }
        ]
        
        for content in sample_contents:
            wellness_content = models.WellnessContent(**content)
            db.add(wellness_content)
        
        db.commit()
        print("✅ Sample wellness content created!")
    except Exception as e:
        print(f"Error creating content: {e}")
        db.rollback()

# ============ Authentication Routes ============

@app.post("/api/auth/register", response_model=schemas.UserResponse)
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(
        (models.User.email == user_data.email) | (models.User.username == user_data.username)
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    hashed_password = auth.get_password_hash(user_data.password)
    db_user = models.User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/api/auth/login", response_model=schemas.Token)
def login(user_data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user.last_login = datetime.now()
    db.commit()
    
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/auth/me", response_model=schemas.UserResponse)
def get_current_user(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

# ============ Chatbot Routes ============

@app.post("/api/chat/send")
async def send_message(
    message: schemas.ChatMessageBase,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message to the AI chatbot and get a response"""
    response = await chatbot.process_chat_message(db, current_user.id, message.content)
    return response

@app.post("/api/chat/send-with-session")
async def send_message_with_session(
    message: schemas.ChatMessageBase,
    session_id: int = None,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message with a specific session ID"""
    response = await chatbot.process_chat_message(db, current_user.id, message.content, session_id)
    return response

@app.post("/api/chat/new-session")
async def create_new_session(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Create a brand new chat session"""
    new_session = models.ChatSession(user_id=current_user.id)
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    
    return {"session_id": new_session.id, "message": "New session created"}

@app.get("/api/chat/history")
def get_chat_history(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's chat history with session previews"""
    sessions = db.query(models.ChatSession).filter(
        models.ChatSession.user_id == current_user.id
    ).order_by(models.ChatSession.started_at.desc()).all()
    
    sessions_data = []
    for session in sessions:
        first_message = db.query(models.ChatMessage).filter(
            models.ChatMessage.session_id == session.id,
            models.ChatMessage.role == "user"
        ).first()
        
        if first_message:
            preview = first_message.content[:50] + "..." if len(first_message.content) > 50 else first_message.content
        else:
            preview = "New conversation"
        
        title = f"Chat {session.started_at.strftime('%b %d, %I:%M %p')}"
        
        sessions_data.append({
            "id": session.id,
            "title": title,
            "preview": preview,
            "started_at": session.started_at
        })
    
    if sessions:
        latest_session = sessions[0]
        messages = db.query(models.ChatMessage).filter(
            models.ChatMessage.session_id == latest_session.id
        ).order_by(models.ChatMessage.timestamp).all()
        
        messages_data = []
        for msg in messages:
            messages_data.append({
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat() if msg.timestamp else None
            })
        
        return {"session_id": latest_session.id, "messages": messages_data, "sessions": sessions_data}
    
    return {"session_id": None, "messages": [], "sessions": sessions_data}

@app.get("/api/chat/session/{session_id}")
async def get_session_messages(
    session_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Get messages for a specific session"""
    session = db.query(models.ChatSession).filter(
        models.ChatSession.id == session_id,
        models.ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    messages = db.query(models.ChatMessage).filter(
        models.ChatMessage.session_id == session_id
    ).order_by(models.ChatMessage.timestamp).all()
    
    messages_data = []
    for msg in messages:
        messages_data.append({
            "id": msg.id,
            "role": msg.role,
            "content": msg.content,
            "timestamp": msg.timestamp.isoformat() if msg.timestamp else None
        })
    
    return {"session_id": session_id, "messages": messages_data}

@app.delete("/api/chat/session/{session_id}")
async def delete_session(
    session_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a chat session and all its messages"""
    session = db.query(models.ChatSession).filter(
        models.ChatSession.id == session_id,
        models.ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    db.query(models.ChatMessage).filter(models.ChatMessage.session_id == session_id).delete()
    db.delete(session)
    db.commit()
    
    return {"message": "Session deleted successfully"}

@app.get("/api/chat/current-session")
async def get_current_session(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Get the most recent session for the user"""
    session = db.query(models.ChatSession).filter(
        models.ChatSession.user_id == current_user.id
    ).order_by(models.ChatSession.started_at.desc()).first()
    
    if session:
        return {"session_id": session.id}
    return {"session_id": None}

@app.get("/api/chat/test")
async def test_chatbot():
    """Test endpoint to verify chatbot is working"""
    from .chatbot import detect_emotion, get_cbt_response
    
    test_message = "I'm feeling anxious today"
    emotion = detect_emotion(test_message)
    groq_configured = bool(os.getenv("GROQ_API_KEY")) and os.getenv("GROQ_API_KEY") != "your-groq-api-key-here"
    
    return {
        "status": "online",
        "test_message": test_message,
        "detected_emotion": emotion,
        "sample_response": get_cbt_response(emotion),
        "groq_api_configured": groq_configured,
        "message": "Groq API is configured and ready!" if groq_configured else "Using local CBT responses"
    }

# ============ Teleconsultation Routes ============

@app.get("/api/psychologists")
def get_psychologists(
    specialization: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Psychologist).filter(models.Psychologist.is_available == True)
    
    if specialization:
        query = query.filter(models.Psychologist.specialization.ilike(f"%{specialization}%"))
    
    psychologists = query.all()
    result = []
    for psych in psychologists:
        user = db.query(models.User).filter(models.User.id == psych.user_id).first()
        result.append({
            "id": psych.id,
            "name": user.full_name if user else "Professional",
            "specialization": psych.specialization,
            "bio": psych.bio,
            "consultation_fee": psych.consultation_fee,
            "is_available": psych.is_available
        })
    return result

@app.get("/api/psychologists/{psychologist_id}")
def get_psychologist_detail(psychologist_id: int, db: Session = Depends(get_db)):
    psychologist = db.query(models.Psychologist).filter(models.Psychologist.id == psychologist_id).first()
    if not psychologist:
        raise HTTPException(status_code=404, detail="Psychologist not found")
    
    user = db.query(models.User).filter(models.User.id == psychologist.user_id).first()
    return {
        "id": psychologist.id,
        "name": user.full_name if user else "Professional",
        "specialization": psychologist.specialization,
        "bio": psychologist.bio,
        "consultation_fee": psychologist.consultation_fee,
        "is_available": psychologist.is_available,
        "license_number": psychologist.license_number
    }

@app.post("/api/appointments")
def create_appointment(
    appointment: schemas.AppointmentCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    psychologist = db.query(models.Psychologist).filter(models.Psychologist.id == appointment.psychologist_id).first()
    if not psychologist:
        raise HTTPException(status_code=404, detail="Psychologist not found")
    
    if not psychologist.is_available:
        raise HTTPException(status_code=400, detail="Psychologist is not available")
    
    existing = db.query(models.Appointment).filter(
        models.Appointment.psychologist_id == appointment.psychologist_id,
        models.Appointment.scheduled_time == appointment.scheduled_time,
        models.Appointment.status == "scheduled"
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Time slot already booked")
    
    meeting_id = str(uuid.uuid4())[:8]
    meeting_link = f"/meet/{meeting_id}"
    
    db_appointment = models.Appointment(
        user_id=current_user.id,
        psychologist_id=appointment.psychologist_id,
        scheduled_time=appointment.scheduled_time,
        duration=appointment.duration,
        meeting_link=meeting_link,
        status="scheduled"
    )
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    
    user = db.query(models.User).filter(models.User.id == psychologist.user_id).first()
    
    return {
        "id": db_appointment.id,
        "psychologist_name": user.full_name if user else "Professional",
        "scheduled_time": db_appointment.scheduled_time,
        "status": db_appointment.status,
        "meeting_link": meeting_link,
        "duration": db_appointment.duration
    }

@app.get("/api/appointments")
def get_appointments(
    current_user: models.User = Depends(auth.get_current_user),
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Appointment).filter(models.Appointment.user_id == current_user.id)
    
    if status:
        query = query.filter(models.Appointment.status == status)
    
    appointments = query.order_by(models.Appointment.scheduled_time.desc()).all()
    
    result = []
    for apt in appointments:
        psychologist = db.query(models.Psychologist).filter(models.Psychologist.id == apt.psychologist_id).first()
        user = db.query(models.User).filter(models.User.id == psychologist.user_id).first() if psychologist else None
        result.append({
            "id": apt.id,
            "psychologist_name": user.full_name if user else "Professional",
            "scheduled_time": apt.scheduled_time,
            "status": apt.status,
            "meeting_link": apt.meeting_link,
            "duration": apt.duration
        })
    return result

@app.put("/api/appointments/{appointment_id}/cancel")
def cancel_appointment(
    appointment_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    appointment = db.query(models.Appointment).filter(
        models.Appointment.id == appointment_id,
        models.Appointment.user_id == current_user.id
    ).first()
    
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    if appointment.status == "completed":
        raise HTTPException(status_code=400, detail="Cannot cancel completed appointment")
    
    appointment.status = "cancelled"
    db.commit()
    
    return {"message": "Appointment cancelled successfully"}

# ============ Community Routes ============

@app.post("/api/community/posts/{post_id}/comments")
def add_comment(
    post_id: int,
    comment_data: schemas.CommunityPostCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Add a comment to a post"""
    # Check if post exists
    post = db.query(models.CommunityPost).filter(models.CommunityPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Create the comment
    comment = models.CommunityComment(
        post_id=post_id,
        user_id=current_user.id,
        content=comment_data.content,
        is_anonymous=comment_data.is_anonymous
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    
    # Get author name (anonymous if requested)
    author_name = "Anonymous" if comment.is_anonymous else current_user.username
    
    return {
        "id": comment.id,
        "content": comment.content,
        "author": author_name,
        "is_anonymous": comment.is_anonymous,
        "created_at": comment.created_at
    }

# ============ Wellness Library Routes ============

@app.get("/api/content")
def get_content(
    category: Optional[str] = None,
    content_type: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    query = db.query(models.WellnessContent)
    
    if category:
        query = query.filter(models.WellnessContent.category == category)
    
    if content_type:
        query = query.filter(models.WellnessContent.content_type == content_type)
    
    if search:
        query = query.filter(
            (models.WellnessContent.title.ilike(f"%{search}%")) |
            (models.WellnessContent.content_english.ilike(f"%{search}%"))
        )
    
    contents = query.limit(limit).all()
    
    result = []
    for content_item in contents:
        result.append({
            "id": content_item.id,
            "title": content_item.title,
            "content": content_item.content_english[:200] + "..." if len(content_item.content_english) > 200 else content_item.content_english,
            "category": content_item.category,
            "content_type": content_item.content_type,
            "views": content_item.views
        })
    return result

@app.get("/api/content/{content_id}")
def get_content_detail(
    content_id: int,
    language: str = "english",
    db: Session = Depends(get_db)
):
    content_item = db.query(models.WellnessContent).filter(models.WellnessContent.id == content_id).first()
    if not content_item:
        raise HTTPException(status_code=404, detail="Content not found")
    
    content_item.views += 1
    db.commit()
    
    content_text = content_item.content_english if language == "english" else content_item.content_urdu
    
    return {
        "id": content_item.id,
        "title": content_item.title,
        "content": content_text,
        "category": content_item.category,
        "content_type": content_item.content_type,
        "tags": content_item.tags,
        "views": content_item.views,
        "created_at": content_item.created_at
    }

# ============ Dashboard Stats Routes ============

@app.get("/api/dashboard/stats")
def get_dashboard_stats(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    chat_sessions = db.query(models.ChatSession).filter(
        models.ChatSession.user_id == current_user.id
    ).count()
    
    messages = db.query(models.ChatMessage).join(models.ChatSession).filter(
        models.ChatSession.user_id == current_user.id,
        models.ChatMessage.role == "user"
    ).count()
    
    appointments = db.query(models.Appointment).filter(
        models.Appointment.user_id == current_user.id,
        models.Appointment.status == "scheduled"
    ).count()
    
    completed = db.query(models.Appointment).filter(
        models.Appointment.user_id == current_user.id,
        models.Appointment.status == "completed"
    ).count()
    
    posts = db.query(models.CommunityPost).filter(
        models.CommunityPost.user_id == current_user.id
    ).count()
    
    wellness_score = min(100, max(0, (messages // 10) + (completed * 5) + (posts * 3)))
    
    return {
        "chat_sessions": chat_sessions,
        "total_messages": messages,
        "upcoming_appointments": appointments,
        "completed_sessions": completed,
        "community_posts": posts,
        "wellness_score": wellness_score if wellness_score > 0 else 75
    }

# ============ Startup Event ============

@app.on_event("startup")
def startup_event():
    print("🚀 Starting Nafsiyat AI...")
    db = next(get_db())
    create_sample_psychologists(db)
    create_sample_wellness_content(db)
    db.close()
    print("✅ Nafsiyat AI is ready!")
    print(f"📡 Groq API configured: {bool(os.getenv('GROQ_API_KEY')) and os.getenv('GROQ_API_KEY') != 'your-groq-api-key-here'}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)