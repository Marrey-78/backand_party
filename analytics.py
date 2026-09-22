from database import DatabaseManager


def track_analytics_event(
    event_type,
    user_id=None,
    session_id=None,
    venue_id=None,
    event_id=None
):
    db = DatabaseManager()

    try:
        return db.create_analytics_event(
            event_type=event_type,
            user_id=user_id,
            session_id=session_id,
            venue_id=venue_id,
            event_id=event_id
        )
    finally:
        db.close()