from database import DatabaseManager


def get_default_images():
    db = DatabaseManager()

    try:
        return db.get_default_event_images()
    finally:
        db.close()

