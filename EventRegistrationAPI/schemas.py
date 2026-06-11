from pydantic import BaseModel, AwareDatetime

class EventCreate(BaseModel):
    name: str
    total_seats: int
    date: AwareDatetime


class RegistrationCreate(BaseModel):
    user_name: str
    event_id: int