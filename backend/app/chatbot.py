import httpx
import json
import re
import random
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from . import models
import os
from datetime import datetime

# Groq API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = os.getenv("GROQ_API_URL", "https://api.groq.com/openai/v1/chat/completions")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# Crisis keywords for risk detection
CRISIS_KEYWORDS = [
    "kill myself", "suicide", "end my life", "want to die", "self harm",
    "hurt myself", "no reason to live", "better off dead", "take my life",
    "commit suicide", "end it all", "want to end it"
]

# Comprehensive CBT-based responses for different emotions (Fallback)
CBT_RESPONSES = {
    "anxiety": [
        "I notice you're feeling anxious. Let's try a grounding exercise together: Name 5 things you can see, 4 things you can touch, 3 things you can hear, 2 things you can smell, and 1 thing you can taste. How do you feel now?",
        "Anxiety is your body's way of preparing for challenges. Let's try the 4-7-8 breathing technique: Inhale for 4 seconds, hold for 7 seconds, exhale for 8 seconds. Repeat this 4 times.",
        "When feeling anxious, remember that thoughts are not facts. Can you identify what triggered this anxiety? Let's work through it together.",
        "Let's practice a quick mindfulness exercise. Focus on your breath for 60 seconds. Notice how each breath feels different. You're doing great just by being here.",
        "Anxiety can feel overwhelming, but it will pass. What's one small thing that usually helps you feel calmer? Let's try that together."
    ],
    "sadness": [
        "It's completely okay to feel sad. Sadness is a natural human emotion. Would you like to try a thought record exercise to explore what's contributing to this feeling?",
        "I hear that you're feeling sad. Remember that emotions are like waves - they come and go. What's one small thing that could bring you a moment of peace right now?",
        "Thank you for sharing this with me. Even on difficult days, you matter. Can you name three things you're grateful for today, no matter how small?",
        "Sadness often signals that something important to us needs attention. Would you like to explore what might be underneath this feeling?",
        "I'm here with you. Sometimes just acknowledging our feelings can help them feel less overwhelming. You're not alone in this."
    ],
    "stress": [
        "Stress is your body's response to demands. Let's try a progressive muscle relaxation technique: Tense your shoulders for 5 seconds, then release. Notice the difference.",
        "I understand you're feeling stressed. Let's break down what's overwhelming you. What's one thing you can control in this situation?",
        "Taking a 5-minute walk or stepping away from the stressor can help reset your nervous system. Would you like to try a quick breathing exercise with me?",
        "Stress often comes from feeling overwhelmed. Let's prioritize: What's urgent? What can wait? What can you delegate or let go of?",
        "Remember to be kind to yourself during stressful times. You're doing the best you can with what you have right now."
    ],
    "default": [
        "Thank you for sharing that with me. Would you like to explore some coping strategies together? I'm here to listen and support you.",
        "I appreciate you opening up. What would be most helpful for you right now - coping strategies, just listening, or exploring these feelings further?",
        "You're taking an important step by expressing how you feel. Let's work together on this. What's been on your mind lately?",
        "I'm here to support you. Would you like to try a CBT technique, practice mindfulness, or just continue our conversation?",
        "That's really insightful. Tell me more about what's on your mind - I'm listening carefully."
    ]
}

def detect_emotion(text: str) -> str:
    """Advanced emotion detection using keyword matching"""
    text_lower = text.lower()
    
    emotions = {
        "anxiety": ["anxious", "nervous", "worry", "worried", "scared", "panic", "fear", "terrified", "uneasy", "overthinking"],
        "sadness": ["sad", "depressed", "hopeless", "lonely", "empty", "grief", "crying", "tears", "miserable", "down", "blue"],
        "stress": ["stressed", "pressure", "tired", "exhausted", "burnout", "overwhelmed", "drained", "tense"]
    }
    
    for emotion, keywords in emotions.items():
        for keyword in keywords:
            if keyword in text_lower:
                return emotion
    
    return "default"

def detect_risk(text: str) -> bool:
    """Detect crisis keywords in user input"""
    text_lower = text.lower()
    for keyword in CRISIS_KEYWORDS:
        if keyword in text_lower:
            return True
    return False

def get_cbt_response(emotion: str) -> str:
    """Get randomized CBT-based response based on detected emotion"""
    responses = CBT_RESPONSES.get(emotion, CBT_RESPONSES["default"])
    return random.choice(responses)

async def get_groq_response(messages: List[Dict[str, str]]) -> str:
    """Get response from Groq API with fallback"""
    
    if not GROQ_API_KEY or GROQ_API_KEY == "your-groq-api-key-here":
        last_user_message = messages[-1]["content"] if messages else ""
        emotion = detect_emotion(last_user_message)
        return get_cbt_response(emotion)
    
    system_prompt = """You are Nafsiyat AI, a caring, culturally aware mental wellness companion for users in Pakistan. 

IMPORTANT RULES:
1. Be empathetic, warm, and non-judgmental
2. Use Cognitive Behavioral Therapy (CBT) principles in your responses
3. NEVER give medical advice or diagnose conditions
4. If someone expresses crisis thoughts, gently guide them to professional help
5. Keep responses concise (2-4 sentences max)
6. Use simple English, can mix with common Urdu words like "Assalam-o-Alaikum", "Shukriya"
7. Be specific and practical in your suggestions
8. Show you're actively listening by referencing what they shared
9. NEVER repeat the exact same response
10. End with an open-ended question to continue the conversation

Remember: You're a supportive companion, not a therapist. Be helpful but know your limits."""

    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post(
                GROQ_API_URL,
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": GROQ_MODEL,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        *messages
                    ],
                    "temperature": 0.7,
                    "max_tokens": 500,
                    "top_p": 0.9,
                    "frequency_penalty": 0.5,
                    "presence_penalty": 0.5
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data["choices"][0]["message"]["content"]
                print(f"✅ Groq API response received")
                return ai_response
            else:
                print(f"❌ Groq API error: {response.status_code}")
                last_user_message = messages[-1]["content"] if messages else ""
                emotion = detect_emotion(last_user_message)
                return get_cbt_response(emotion)
                
    except httpx.TimeoutException:
        print("❌ Groq API timeout")
        last_user_message = messages[-1]["content"] if messages else ""
        emotion = detect_emotion(last_user_message)
        return get_cbt_response(emotion)
    except Exception as e:
        print(f"❌ Groq API exception: {e}")
        last_user_message = messages[-1]["content"] if messages else ""
        emotion = detect_emotion(last_user_message)
        return get_cbt_response(emotion)

async def process_chat_message(db: Session, user_id: int, message: str, session_id: int = None) -> Dict[str, Any]:
    """Process chat message and return response"""
    
    # Detect risk and emotion
    is_risk = detect_risk(message)
    emotion = detect_emotion(message)
    
    print(f"📝 User message: {message[:100]}...")
    print(f"🎭 Detected emotion: {emotion}")
    print(f"⚠️ Risk detected: {is_risk}")
    
    # Get or create session
    session = None
    if session_id:
        session = db.query(models.ChatSession).filter(
            models.ChatSession.id == session_id,
            models.ChatSession.user_id == user_id
        ).first()
    
    if not session:
        # Create new session
        session = models.ChatSession(user_id=user_id)
        db.add(session)
        db.commit()
        db.refresh(session)
        print(f"💬 New chat session created: {session.id}")
    
    # Save user message
    user_message = models.ChatMessage(
        session_id=session.id,
        role="user",
        content=message,
        sentiment=emotion,
        risk_detected=is_risk
    )
    db.add(user_message)
    db.commit()
    
    # Generate response
    if is_risk:
        response_text = """⚠️ **I'm really concerned about what you're sharing.** ⚠️

Your feelings are valid and you don't have to go through this alone. 

**Please reach out for immediate support:**
• 📞 GIKI Emergency Helpline: 0311-778-6264 
• 🏥 Visit GIKI Medical Center immediately
• 👨‍⚕️ Contact a mental health professional immediately

You matter, and there is help available. Would you like me to help you find local mental health resources?"""
    else:
        # Get conversation history (last 10 messages for context)
        previous_messages = db.query(models.ChatMessage).filter(
            models.ChatMessage.session_id == session.id
        ).order_by(models.ChatMessage.timestamp).limit(10).all()
        
        history = []
        for msg in previous_messages:
            history.append({"role": msg.role, "content": msg.content})
        
        print(f"🤖 Calling Groq API...")
        response_text = await get_groq_response(history)
        print(f"💬 Response: {response_text[:100]}...")
    
    # Save assistant response
    assistant_message = models.ChatMessage(
        session_id=session.id,
        role="assistant",
        content=response_text,
        sentiment="supportive"
    )
    db.add(assistant_message)
    db.commit()
    
    return {
        "response": response_text,
        "risk_detected": is_risk,
        "sentiment": emotion,
        "session_id": session.id
    }