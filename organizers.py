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

def add_organizer_favorite(self, user_id, organizer_id):
    with self.conn.cursor() as cur:
        cur.execute("""
            INSERT INTO user_organizer_favorites (user_id, organizer_id)
            VALUES (%s, %s)
            ON CONFLICT (user_id, organizer_id) DO NOTHING
            RETURNING *;
        """, (user_id, organizer_id))

        favorite = cur.fetchone()
        self.conn.commit()
        return favorite


def remove_organizer_favorite(self, user_id, organizer_id):
    with self.conn.cursor() as cur:
        cur.execute("""
            DELETE FROM user_organizer_favorites
            WHERE user_id = %s
            AND organizer_id = %s
            RETURNING id;
        """, (user_id, organizer_id))

        deleted = cur.fetchone()
        self.conn.commit()
        return deleted


def get_user_organizer_favorites(self, user_id):
    with self.conn.cursor() as cur:
        cur.execute("""
            SELECT
                o.*,
                f.created_at AS favorite_created_at
            FROM user_organizer_favorites f
            JOIN organizers o ON f.organizer_id = o.id
            WHERE f.user_id = %s
            ORDER BY f.created_at DESC;
        """, (user_id,))

        return cur.fetchall()