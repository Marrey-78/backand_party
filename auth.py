import os
import bcrypt
import jwt
from datetime import datetime, timedelta
from database import DatabaseManager
from firebase_admin import auth as firebase_auth


JWT_SECRET = os.getenv("JWT_SECRET")


def generate_token(user):
    payload = {
        "user_id": str(user["id"]),
        "role": user["role"],
        "exp": datetime.utcnow() + timedelta(days=7)
    }

    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def register_user(name, email, password, has_venue):
    db = DatabaseManager()

    try:
        existing_user = db.get_user_by_email(email)

        if existing_user:
            return {
                "success": False,
                "message": "Email già registrata"
            }

        password_hash = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        role = "venue_owner" if has_venue else "user"
        avatar = f"https://api.dicebear.com/7.x/avataaars/svg?seed={email}"

        user = db.create_user(
            name=name,
            email=email,
            password_hash=password_hash,
            avatar=avatar,
            role=role
        )

        token = generate_token(user)

        return {
            "success": True,
            "user": user,
            "token": token
        }

    finally:
        db.close()


def login_user(email, password):
    db = DatabaseManager()

    try:
        user = db.get_user_by_email(email)

        if not user:
            return {
                "success": False,
                "message": "Credenziali non valide"
            }

        password_ok = bcrypt.checkpw(
            password.encode("utf-8"),
            user["password_hash"].encode("utf-8")
        )

        if not password_ok:
            return {
                "success": False,
                "message": "Credenziali non valide"
            }

        token = generate_token(user)

        user_public = {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "avatar": user["avatar"],
            "role": user["role"]
        }

        return {
            "success": True,
            "user": user_public,
            "token": token
        }

    finally:
        db.close()

def login_firebase_user(id_token):
    db = DatabaseManager()

    try:
        try:
            decoded_token = firebase_auth.verify_id_token(id_token)
        except Exception as e:
            print("FIREBASE VERIFY ERROR:", repr(e))
            return {
                "success": False,
                "message": f"Errore verifica Firebase: {str(e)}"
            }

        firebase_uid = decoded_token["uid"]
        email = decoded_token.get("email")

        if not email:
            return {
                "success": False,
                "message": "L'account Firebase non contiene una email"
            }

        # 1. Cerchiamo prima l'utente tramite Firebase UID
        user = db.get_user_by_firebase_uid(firebase_uid)

        # 2. Se non esiste, controlliamo se esiste già la stessa email
        if not user:
            existing_user = db.get_user_by_email(email)

            if existing_user:
                return {
                    "success": False,
                    "message": "Esiste già un account con questa email. Accedi con email e password."
                }

            name = (
                decoded_token.get("name")
                or email.split("@")[0]
            )

            avatar = decoded_token.get("picture")

            user = db.create_firebase_user(
                name=name,
                email=email,
                avatar=avatar,
                firebase_uid=firebase_uid
            )

        token = generate_token(user)

        user_public = {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "avatar": user["avatar"],
            "role": user["role"]
        }

        return {
            "success": True,
            "user": user_public,
            "token": token
        }

    finally:
        db.close()
