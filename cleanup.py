from database import DatabaseManager


def cleanup_past_events():
    db = DatabaseManager()

    try:
        deleted = db.delete_past_events()

        print(f"Eventi passati eliminati: {len(deleted)}")

        return {
            "deleted_count": len(deleted)
        }

    finally:
        db.close()