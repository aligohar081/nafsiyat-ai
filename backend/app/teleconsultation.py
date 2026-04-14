from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime
import uuid

def create_appointment(db: Session, user_id: int, appointment: schemas.AppointmentCreate):
    # Generate unique meeting link
    meeting_id = str(uuid.uuid4())[:8]
    meeting_link = f"/meet/{meeting_id}"
    
    db_appointment = models.Appointment(
        user_id=user_id,
        psychologist_id=appointment.psychologist_id,
        scheduled_time=appointment.scheduled_time,
        duration=appointment.duration,
        meeting_link=meeting_link
    )
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    
    psychologist = db.query(models.Psychologist).filter(models.Psychologist.id == appointment.psychologist_id).first()
    
    return {
        "id": db_appointment.id,
        "psychologist_name": psychologist.user.full_name if psychologist else "Professional",
        "scheduled_time": db_appointment.scheduled_time,
        "status": db_appointment.status,
        "meeting_link": meeting_link
    }