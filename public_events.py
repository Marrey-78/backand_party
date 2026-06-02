from database import DatabaseManager


def get_events_for_map():
    db = DatabaseManager()

    try:
        return db.get_public_events()
    finally:
        db.close()

def get_events_near_user(lat, lng, radius_km):
    db = DatabaseManager()

    try:
        return db.get_nearby_events(lat, lng, radius_km)
    finally:
        db.close()

def get_events_for_city(city):
    db = DatabaseManager()

    try:
        return db.get_events_by_city(city)
    finally:
        db.close()