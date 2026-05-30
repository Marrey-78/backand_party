import jwt
import os
from fastapi import HTTPException, Header
from database import DatabaseManager
from geocoding import geocode_address

JWT_SECRET = os.getenv("JWT_SECRET")


def get_current_user_id(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Token mancante")

    try:
        token = authorization.replace("Bearer ", "")
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload["user_id"]

    except Exception:
        raise HTTPException(status_code=401, detail="Token non valido")


def get_all_venue_types():
    db = DatabaseManager()

    try:
        return db.get_venue_types()
    finally:
        db.close()


def create_new_venue(owner_user_id, data):
    db = DatabaseManager()

    try:
        latitude, longitude = geocode_address(
            data.address,
            data.city
        )

        return db.create_venue(
            owner_user_id=owner_user_id,
            venue_type_id=data.venue_type_id,
            name=data.name,
            description=data.description,
            address=data.address,
            city=data.city,
            latitude=latitude,
            longitude=longitude,
            phone=data.phone,
            email=data.email,
            website_url=data.website_url,
            instagram_url=data.instagram_url,
            image_url=data.image_url
        )
    finally:
        db.close()


def get_my_venues(owner_user_id):
    db = DatabaseManager()

    try:
        return db.get_venues_by_owner(owner_user_id)
    finally:
        db.close()

def delete_my_venue(owner_user_id, venue_id):
    db = DatabaseManager()

    try:
        deleted = db.delete_venue(
            venue_id=venue_id,
            owner_user_id=owner_user_id
        )

        if not deleted:
            raise HTTPException(
                status_code=404,
                detail="Locale non trovato"
            )

        return {
            "success": True
        }

    finally:
        db.close()