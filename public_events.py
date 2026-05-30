from database import DatabaseManager


def get_events_for_map():
    db = DatabaseManager()

    try:
        return db.get_public_events()
    finally:
        db.close()