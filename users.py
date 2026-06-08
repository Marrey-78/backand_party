import bcrypt
from fastapi import HTTPException
from database import DatabaseManager


def get_my_profile(user_id):
    db = DatabaseManager()

    try:
        user = db.get_user_by_id(user_id)

        if not user:
            raise HTTPException(status_code=404, detail="Utente non trovato")

        user.pop("password_hash", None)
        return user

    finally:
        db.close()


def update_my_profile(user_id, data):
    db = DatabaseManager()

    try:
        current_user = db.get_user_by_id(user_id)

        if not current_user:
            raise HTTPException(status_code=404, detail="Utente non trovato")

        updated = db.update_user_profile(
            user_id=user_id,
            name=data.name,
            email=data.email,
            city=data.city,
            avatar=data.avatar
        )

        if not updated:
            raise HTTPException(status_code=404, detail="Utente non trovato")

        return updated

    finally:
        db.close()


def change_my_password(user_id, data):
    db = DatabaseManager()

    try:
        user = db.get_user_by_id(user_id)

        if not user:
            raise HTTPException(status_code=404, detail="Utente non trovato")

        is_valid = bcrypt.checkpw(
            data.old_password.encode("utf-8"),
            user["password_hash"].encode("utf-8")
        )

        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail="Password attuale errata"
            )

        new_hash = bcrypt.hashpw(
            data.new_password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        db.update_user_password(user_id, new_hash)

        return {
            "success": True
        }

    finally:
        db.close()