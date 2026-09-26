from database import DatabaseManager
from fastapi import HTTPException

def track_analytics_event(
    event_type,
    user_id=None,
    session_id=None,
    venue_id=None,
    event_id=None,
    organizer_id=None
):
    db = DatabaseManager()

    try:
        return db.create_analytics_event(
            event_type=event_type,
            user_id=user_id,
            session_id=session_id,
            venue_id=venue_id,
            event_id=event_id,
            organizer_id=organizer_id
        )
    finally:
        db.close()

def get_venue_stats(
    venue_id,
    user_id,
    period="30d"
):
    days = parse_period(period)

    db = DatabaseManager()

    try:
        stats = db.get_venue_analytics_stats(
            venue_id=venue_id,
            owner_user_id=user_id,
            days=days
        )

        if stats is None:
            raise HTTPException(
                status_code=403,
                detail="Non autorizzato"
            )
        stats["views_change_percentage"] = (
            calculate_percentage_change(
                stats["venue_views"],
                stats["previous_venue_views"]
            )
        )    

        return stats

    finally:
        db.close()

def get_organizer_stats(
    organizer_id,
    user_id,
    period="30d"
):
    days = parse_period(period)

    db = DatabaseManager()

    try:
        stats = db.get_organizer_analytics_stats(
            organizer_id=organizer_id,
            owner_user_id=user_id,
            days=days
        )

        if stats is None:
            raise HTTPException(
                status_code=403,
                detail="Non autorizzato"
            )
        stats["views_change_percentage"] = (
            calculate_percentage_change(
                stats["organizer_views"],
                stats["previous_organizer_views"]
            )
        )

        return stats

    finally:
        db.close()

VALID_PERIODS = {
    "7d": 7,
    "30d": 30,
    "90d": 90,
    "all": None
}


def parse_period(period):
    if period not in VALID_PERIODS:
        raise HTTPException(
            status_code=400,
            detail="Periodo non valido. Usa 7d, 30d, 90d o all."
        )

    return VALID_PERIODS[period]

def calculate_percentage_change(current, previous):
    if previous is None:
        return None

    if previous == 0:
        if current == 0:
            return 0

        return None

    return round(
        ((current - previous) / previous) * 100,
        1
    )

def get_venue_timeline(
    venue_id,
    user_id,
    period="30d"
):
    days = parse_period(period)

    # Per il grafico "all" non ha molto senso:
    # utilizziamo 90 giorni.
    if days is None:
        days = 90

    db = DatabaseManager()

    try:
        timeline = db.get_venue_analytics_timeline(
            venue_id=venue_id,
            owner_user_id=user_id,
            days=days
        )

        if timeline is None:
            raise HTTPException(
                status_code=403,
                detail="Non autorizzato"
            )

        return timeline

    finally:
        db.close()


def get_organizer_timeline(
    organizer_id,
    user_id,
    period="30d"
):
    days = parse_period(period)

    if days is None:
        days = 90

    db = DatabaseManager()

    try:
        timeline = db.get_organizer_analytics_timeline(
            organizer_id=organizer_id,
            owner_user_id=user_id,
            days=days
        )

        if timeline is None:
            raise HTTPException(
                status_code=403,
                detail="Non autorizzato"
            )

        return timeline

    finally:
        db.close()