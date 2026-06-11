from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from datetime import datetime, timezone

from models import Base, Event, Registration
from schemas import EventCreate, RegistrationCreate

app = FastAPI()

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/events")
def create_event(event: EventCreate, db: Session = Depends(get_db)):

    # Checks if seats > 0
    if event.total_seats <= 0:
        raise HTTPException(
            status_code=400,
            detail="Seats must be greater than 0"
        )

    # Check future date
    if event.date <= datetime.now(timezone.utc):
        raise HTTPException(
            status_code=400,
            detail="Event date must be in the future"
        )

    # Check unique event name
    existing_event = db.query(Event).filter(
        Event.name == event.name
    ).first()

    if existing_event:
            raise HTTPException(
                status_code=400,
                detail="Event name already exists"
            )

    # Save event
    new_event = Event (
        name = event.name,
        date=event.date,
        total_seats=event.total_seats
    )

    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    return {
        "message": "Event created successfully",
        "event": new_event
    }

@app.post("/registrations")
def register_user(registration: RegistrationCreate, db = Depends(get_db)):

    event = db.query(Event).filter(
        Event.id == registration.event_id
    ).with_for_update() .first()

    if not event:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    existing = db.query(Registration).filter(
        Registration.event_id == registration.event_id,
        Registration.user_name == registration.user_name,
        Registration.is_cancelled == False
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="User already registered"
        )

    active_registrations = db.query(Registration).filter(
        Registration.event_id == registration.event_id,
        Registration.is_cancelled == False
    ).count()

    if active_registrations >= event.total_seats:
        raise HTTPException(
            status_code=400,
            detail="Event is full"
        )

    new_registration = Registration(
        user_name=registration.user_name,
        event_id=registration.event_id,
        registered_at=datetime.now(timezone.utc),
        is_cancelled=False
    )

    db.add(new_registration)
    db.commit()
    db.refresh(new_registration)

    return {
        "message": "Registration successful",
        "registration_id": new_registration.id
    }

@app.get("/events")
def get_events(db: Session = Depends(get_db)):
    
    upcoming: bool = False
    sort_by_date: bool = False,
    
    # Fetch all events from the database
    events = db.query(Event).all()

    # 1. Filter out past events if upcoming is True
    if upcoming:
        # We make the current time timezone-aware to match your saved dates
        current_time = datetime.now(timezone.utc)
        events = [e for e in events if e.date > current_time]

    # 2. Sort the events by date if sort_by_date is True
    if sort_by_date:
        events.sort(key=lambda x: x.date)

    result = []

    # 3. Calculate seats and registration details
    for event in events:
        active_registrations = db.query(Registration).filter(
            Registration.event_id == event.id,
            Registration.is_cancelled == False
        ).count()

        result.append({
            "id": event.id,
            "event_name": event.name,
            "event_date": event.date,
            "total_seats": event.total_seats,
            "available_seats": event.total_seats - active_registrations,
            "total_registrations": active_registrations
        })

    return result

@app.delete("/registrations/{registration_id}")
def cancel_registration(registration_id: int, db: Session = Depends(get_db) ):

    registration = db.query(
        Registration
    ).filter(
        Registration.id == registration_id
    ).first()

    if not registration:
        raise HTTPException(
            status_code=404,
            detail="Registration not found"
        )

    if registration.is_cancelled:
        raise HTTPException(
            status_code=400,
            detail="Registration already cancelled"
        )

    registration.is_cancelled = True

    db.commit()

    return {
        "message": "Registration cancelled successfully"
    }