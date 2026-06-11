from sqlalchemy import *
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    total_seats = Column(Integer)
    date = Column(DateTime)

class Registration(Base):
    __tablename__ = "registrations"

    id = Column(Integer, primary_key=True)
    user_name = Column(String)
    event_id = Column(Integer, ForeignKey("events.id"))
    registered_at = Column(DateTime)
    is_cancelled = Column(Boolean, default=False)