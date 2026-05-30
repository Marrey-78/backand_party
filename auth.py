import os
import bcrypt
import jwt
from datetime import datetime, timedelta
from database import DatabaseManager


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
