from fastapi import HTTPException
from database import DatabaseManager
from geocoding import geocode_address


def create_new_event(owner_user_id, data):
    db = DatabaseManager()

    try:
        owns_venue = db.user_owns_venue(
            venue_id=data.venue_id,
            owner_user_id=owner_user_id
        )

        if not owns_venue:
            raise HTTPException(
                status_code=403,
                detail="Non puoi creare eventi per questo locale"
            )

        return db.create_event(
            venue_id=data.venue_id,
            title=data.title,
            description=data.description,
            event_date=data.event_date,
            start_time=data.start_time,
            end_time=data.end_time,
            price=data.price,
            category=data.category,
            image_url=data.image_url,
            ticket_url=data.ticket_url,
            max_participants=data.max_participants
        )

    finally:
        db.close()


def get_venue_events(owner_user_id, venue_id):
    db = DatabaseManager()

    try:
        owns_venue = db.user_owns_venue(
            venue_id=venue_id,
            owner_user_id=owner_user_id
        )

        if not owns_venue:
            raise HTTPException(
                status_code=403,
                detail="Non puoi vedere eventi di questo locale"
            )

        return db.get_events_by_venue(
            venue_id=venue_id,
            owner_user_id=owner_user_id
        )

    finally:
        db.close()

def delete_my_event(owner_user_id, event_id):
    db = DatabaseManager()

    try:
        deleted = db.delete_event(
            event_id=event_id,
            owner_user_id=owner_user_id
        )

        if not deleted:
            raise HTTPException(
                status_code=404,
                detail="Evento non trovato"
            )

        return {
            "success": True
        }

    finally:
        db.close()

def create_new_organizer_event(owner_user_id, data):
    db = DatabaseManager()

    try:
        owns_organizer = db.user_owns_organizer(
            organizer_id=data.organizer_id,
            owner_user_id=owner_user_id
        )

        if not owns_organizer:
            raise HTTPException(
                status_code=403,
                detail="Non puoi creare eventi per questo organizzatore"
            )

        latitude, longitude = geocode_address(
            data.event_address,
            data.event_city
        )

        if latitude is None or longitude is None:
            raise HTTPException(
                status_code=400,
                detail="Impossibile trovare le coordinate dell'indirizzo evento"
            )

        return db.create_organizer_event(
            organizer_id=data.organizer_id,
            title=data.title,
            description=data.description,
            event_date=data.event_date,
            start_time=data.start_time,
            end_time=data.end_time,
            price=data.price,
            category=data.category,
            image_url=data.image_url,
            ticket_url=data.ticket_url,
            max_participants=data.max_participants,
            event_address=data.event_address,
            event_city=data.event_city,
            event_latitude=latitude,
            event_longitude=longitude
        )

    finally:
        db.close()


def get_organizer_events(owner_user_id, organizer_id):
    db = DatabaseManager()

    try:
        owns_organizer = db.user_owns_organizer(
            organizer_id=organizer_id,
            owner_user_id=owner_user_id
        )

        if not owns_organizer:
            raise HTTPException(
                status_code=403,
                detail="Non puoi vedere eventi di questo organizzatore"
            )

        return db.get_events_by_organizer(
            organizer_id=organizer_id,
            owner_user_id=owner_user_id
        )

    finally:
        db.close()