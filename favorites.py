from fastapi import HTTPException
from database import DatabaseManager


def get_my_event_favorites(user_id):
    db = DatabaseManager()

    try:
        return db.get_user_event_favorites(user_id)
    finally:
        db.close()


def add_my_event_favorite(user_id, event_id):
    db = DatabaseManager()

    try:
        favorite = db.add_event_favorite(user_id, event_id)

        return {
            "success": True,
            "favorite": favorite
        }

    finally:
        db.close()


def remove_my_event_favorite(user_id, event_id):
    db = DatabaseManager()

    try:
        deleted = db.remove_event_favorite(user_id, event_id)

        if not deleted:
            raise HTTPException(
                status_code=404,
                detail="Preferito non trovato"
            )

        return {
            "success": True
        }

    finally:
        db.close()

def get_my_venue_favorites(user_id):
    db = DatabaseManager()

    try:
        return db.get_user_venue_favorites(user_id)
    finally:
        db.close()


def add_my_venue_favorite(user_id, venue_id):
    db = DatabaseManager()

    try:
        favorite = db.add_venue_favorite(user_id, venue_id)

        return {
            "success": True,
            "favorite": favorite
        }

    finally:
        db.close()


def remove_my_venue_favorite(user_id, venue_id):
    db = DatabaseManager()

    try:
        deleted = db.remove_venue_favorite(user_id, venue_id)

        if not deleted:
            raise HTTPException(
                status_code=404,
                detail="Locale preferito non trovato"
            )

        return {
            "success": True
        }

    finally:
        db.close()


def get_my_organizer_favorites(user_id):
    db = DatabaseManager()

    try:
        return db.get_user_organizer_favorites(user_id)
    finally:
        db.close()


def add_my_organizer_favorite(user_id, organizer_id):
    db = DatabaseManager()

    try:
        favorite = db.add_organizer_favorite(user_id, organizer_id)

        return {
            "success": True,
            "favorite": favorite
        }

    finally:
        db.close()


def remove_my_organizer_favorite(user_id, organizer_id):
    db = DatabaseManager()

    try:
        deleted = db.remove_organizer_favorite(user_id, organizer_id)

        if not deleted:
            raise HTTPException(
                status_code=404,
                detail="Organizzazione preferita non trovata"
            )

        return {
            "success": True
        }

    finally:
        db.close()