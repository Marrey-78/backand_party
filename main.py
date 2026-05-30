import os
import shutil
from uuid import uuid4
from fastapi import UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from auth import register_user, login_user
from typing import Optional
from fastapi import Depends
from venues import (get_current_user_id, get_all_venue_types, create_new_venue, get_my_venues, delete_my_venue)
from events import create_new_event, get_venue_events, delete_my_event, create_new_organizer_event, get_organizer_events
from images import get_default_images
from public_events import get_events_for_map
from organizers import create_new_organizer, get_my_organizers, delete_my_organizer


app = FastAPI()

os.makedirs("uploads/events", exist_ok=True)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    hasVenue: bool


class LoginRequest(BaseModel):
    email: str
    password: str

class CreateVenueRequest(BaseModel):
    venue_type_id: str
    name: str
    description: Optional[str] = None
    address: str
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website_url: Optional[str] = None
    instagram_url: Optional[str] = None
    image_url: Optional[str] = None

class CreateOrganizerRequest(BaseModel):
    name: str
    description: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website_url: Optional[str] = None
    instagram_url: Optional[str] = None
    image_url: Optional[str] = None

class CreateEventRequest(BaseModel):
    venue_id: str

    title: str
    description: Optional[str] = None
    event_date: str
    start_time: str
    end_time: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    ticket_url: Optional[str] = None
    max_participants: Optional[int] = None

class CreateOrganizerEventRequest(BaseModel):
    organizer_id: str
    title: str
    description: Optional[str] = None
    event_date: str
    start_time: str
    end_time: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    ticket_url: Optional[str] = None
    max_participants: Optional[int] = None
    event_address: str
    event_city: str

@app.get("/")
def home():
    return {"message": "Backend NightLife attivo"}


@app.post("/auth/register")
def register(data: RegisterRequest):
    result = register_user(
        name=data.name,
        email=data.email,
        password=data.password,
        has_venue=data.hasVenue
    )

    if not result["success"]:
        raise HTTPException(status_code=409, detail=result["message"])

    return {
        "user": result["user"],
        "token": result["token"]
    }


@app.post("/auth/login")
def login(data: LoginRequest):
    result = login_user(
        email=data.email,
        password=data.password
    )

    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["message"])

    return {
        "user": result["user"],
        "token": result["token"]
    }

@app.get("/venue-types")
def venue_types():
    return get_all_venue_types()


@app.get("/venues/my")
def my_venues(user_id: str = Depends(get_current_user_id)):
    return get_my_venues(user_id)


@app.post("/venues")
def create_venue(
    data: CreateVenueRequest,
    user_id: str = Depends(get_current_user_id)
):
    venue = create_new_venue(user_id, data)
    return venue

@app.delete("/venues/{venue_id}")
def delete_venue(
    venue_id: str,
    user_id: str = Depends(get_current_user_id)
):
    return delete_my_venue(
        owner_user_id=user_id,
        venue_id=venue_id
    )

@app.get("/venues/{venue_id}/events")
def venue_events(
    venue_id: str,
    user_id: str = Depends(get_current_user_id)
):
    return get_venue_events(user_id, venue_id)


@app.post("/events")
def create_event(
    data: CreateEventRequest,
    user_id: str = Depends(get_current_user_id)
):
    event = create_new_event(user_id, data)
    return event

@app.delete("/events/{event_id}")
def delete_event(
    event_id: str,
    user_id: str = Depends(get_current_user_id)
):
    return delete_my_event(
        owner_user_id=user_id,
        event_id=event_id
    )

@app.get("/event-images/defaults")
def default_event_images():
    return get_default_images()

@app.post("/uploads/event-image")
def upload_event_image(file: UploadFile = File(...)):
    extension = file.filename.split(".")[-1].lower()

    if extension not in ["jpg", "jpeg", "png", "webp"]:
        raise HTTPException(status_code=400, detail="Formato immagine non valido")

    filename = f"{uuid4()}.{extension}"
    path = f"uploads/events/{filename}"

    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "image_url": f"http://localhost:3000/uploads/events/{filename}"
    }

@app.get("/events/public")
def public_events():
    return get_events_for_map()

@app.get("/organizers/my")
def my_organizers(user_id: str = Depends(get_current_user_id)):
    return get_my_organizers(user_id)


@app.post("/organizers")
def create_organizer(data: CreateOrganizerRequest, user_id: str = Depends(get_current_user_id)):
    return create_new_organizer(user_id, data)


@app.delete("/organizers/{organizer_id}")
def delete_organizer(
    organizer_id: str,
    user_id: str = Depends(get_current_user_id)
):
    return delete_my_organizer(user_id, organizer_id)

@app.get("/organizers/{organizer_id}/events")
def organizer_events(organizer_id: str, user_id: str = Depends(get_current_user_id)):
    return get_organizer_events(user_id, organizer_id)


@app.post("/organizer-events")
def create_organizer_event( data: CreateOrganizerEventRequest, user_id: str = Depends(get_current_user_id)):
    return create_new_organizer_event(user_id, data)