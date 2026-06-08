from fastapi import HTTPException
from database import DatabaseManager


def create_new_organizer(owner_user_id, data):
    db = DatabaseManager()

    try:
        return db.create_organizer(
            owner_user_id=owner_user_id,
            name=data.name,
            description=data.description,
            phone=data.phone,
            email=data.email,
            website_url=data.website_url,
            instagram_url=data.instagram_url,
            image_url=data.image_url
        )
    finally:
        db.close()


def get_my_organizers(owner_user_id):
    db = DatabaseManager()

    try:
        return db.get_organizers_by_owner(owner_user_id)
    finally:
        db.close()


def delete_my_organizer(owner_user_id, organizer_id):
    db = DatabaseManager()

    try:
        deleted = db.delete_organizer(
            organizer_id=organizer_id,
            owner_user_id=owner_user_id
        )

        if not deleted:
            raise HTTPException(
                status_code=404,
                detail="Organizzatore non trovato"
            )

        return {"success": True}

    finally:
        db.close()

def update_my_organizer(owner_user_id, organizer_id, data):
    db = DatabaseManager()

    try:
        updated = db.update_organizer(
            organizer_id=organizer_id,
            owner_user_id=owner_user_id,
            name=data.name,
            description=data.description,
            phone=data.phone,
            email=data.email,
            website_url=data.website_url,
            instagram_url=data.instagram_url,
            image_url=data.image_url
        )

        if not updated:
            raise HTTPException(
                status_code=404,
                detail="Organizzatore non trovato"
            )

        return updated

    finally:
        db.close()