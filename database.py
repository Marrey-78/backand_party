import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()


class DatabaseManager:
    def __init__(self):
        self.conn = psycopg2.connect(
            os.getenv("DATABASE_URL"),
            cursor_factory=RealDictCursor
        )

    def create_user(self, name, email, password_hash, avatar, role):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO users (name, email, password_hash, avatar, role)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, name, email, avatar, role;
            """, (name, email, password_hash, avatar, role))

            self.conn.commit()
            return cur.fetchone()

    def get_user_by_email(self, email):
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT id, name, email, password_hash, avatar, role
                FROM users
                WHERE email = %s;
            """, (email,))

            return cur.fetchone()
    
    def get_venue_types(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT id, code, name, supports_menu, supports_table_booking, supports_ticketing
                FROM venue_types
                ORDER BY name;
            """)
            return cur.fetchall()
    
    def create_venue(
        self,
        owner_user_id,
        venue_type_id,
        name,
        description,
        address,
        city,
        latitude,
        longitude,
        phone,
        email,
        website_url,
        instagram_url,
        image_url
    ):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO venues (
                    owner_user_id,
                    venue_type_id,
                    name,
                    description,
                    address,
                    city,
                    latitude,
                    longitude,
                    phone,
                    email,
                    website_url,
                    instagram_url,
                    image_url
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *;
            """, (
                owner_user_id,
                venue_type_id,
                name,
                description,
                address,
                city,
                latitude,
                longitude,
                phone,
                email,
                website_url,
                instagram_url,
                image_url
            ))

            self.conn.commit()
            return cur.fetchone()


    def get_venues_by_owner(self, owner_user_id):
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    v.*,
                    vt.name AS venue_type_name,
                    vt.code AS venue_type_code,
                    vt.supports_menu,
                    vt.supports_table_booking,
                    vt.supports_ticketing
                FROM venues v
                LEFT JOIN venue_types vt ON v.venue_type_id = vt.id
                WHERE v.owner_user_id = %s
                ORDER BY v.created_at DESC;
            """, (owner_user_id,))

            return cur.fetchall()
        
    def create_event(
        self,
        venue_id,
        title,
        description,
        event_date,
        start_time,
        end_time,
        price,
        category,
        image_url,
        ticket_url,
        max_participants
    ):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO events (
                    venue_id,
                    title,
                    description,
                    event_date,
                    start_time,
                    end_time,
                    price,
                    category,
                    image_url,
                    ticket_url,
                    max_participants
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *;
            """, (
                venue_id,
                title,
                description,
                event_date,
                start_time,
                end_time,
                price,
                category,
                image_url,
                ticket_url,
                max_participants
            ))
    
            self.conn.commit()
            return cur.fetchone()
    
    def get_events_by_venue(self, venue_id, owner_user_id):
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT e.*
                FROM events e
                JOIN venues v ON e.venue_id = v.id
                WHERE e.venue_id = %s
                AND v.owner_user_id = %s
                ORDER BY e.event_date DESC, e.start_time DESC;
            """, (venue_id, owner_user_id))

            return cur.fetchall()


    def user_owns_venue(self, venue_id, owner_user_id):
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT id
                FROM venues
                WHERE id = %s
                AND owner_user_id = %s;
            """, (venue_id, owner_user_id))
    
            return cur.fetchone() is not None
        
    def delete_venue(self, venue_id, owner_user_id):
        with self.conn.cursor() as cur:
            cur.execute("""
                DELETE FROM venues
                WHERE id = %s
                AND owner_user_id = %s
                RETURNING id;
            """, (venue_id, owner_user_id))

            deleted = cur.fetchone()

            self.conn.commit()

            return deleted
    
    def delete_event(self, event_id, owner_user_id):
        with self.conn.cursor() as cur:
            cur.execute("""
                DELETE FROM events e
                WHERE e.id = %s
                AND (
                    EXISTS (
                        SELECT 1
                        FROM venues v
                        WHERE v.id = e.venue_id
                        AND v.owner_user_id = %s
                    )
                    OR
                    EXISTS (
                        SELECT 1
                        FROM organizers o
                        WHERE o.id = e.organizer_id
                        AND o.owner_user_id = %s
                    )
                )
                RETURNING e.id;
            """, (event_id, owner_user_id, owner_user_id))
    
            deleted = cur.fetchone()
            self.conn.commit()
    
            return deleted
    
    def get_default_event_images(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT id, title, category, image_url
                FROM default_event_images
                ORDER BY title;
            """)
            return cur.fetchall()
    
    def get_public_events(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT
                    e.id,
                    e.title,
                    e.description,
                    e.event_date AS date,
                    e.start_time,
                    e.end_time,
                    e.price,
                    e.category,
                    e.image_url,
                    e.ticket_url,
                    e.max_participants,

                    COALESCE(v.id::text, o.id::text) AS source_id,
                    COALESCE(v.name, o.name) AS venue_name,

                    COALESCE(v.address, e.event_address) AS address,
                    COALESCE(v.city, e.event_city) AS city,

                    COALESCE(v.latitude, e.event_latitude) AS latitude,
                    COALESCE(v.longitude, e.event_longitude) AS longitude

                FROM events e
                LEFT JOIN venues v ON e.venue_id = v.id
                LEFT JOIN organizers o ON e.organizer_id = o.id
                        
                WHERE e.event_date >= CURRENT_DATE
                AND COALESCE(v.latitude, e.event_latitude) IS NOT NULL 
                AND COALESCE(v.longitude, e.event_longitude) IS NOT NULL
                
                ORDER BY e.event_date ASC, e.start_time ASC;
            """)
            return cur.fetchall()
    
    def user_owns_organizer(self, organizer_id, owner_user_id):
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT id
                FROM organizers
                WHERE id = %s
                AND owner_user_id = %s;
            """, (organizer_id, owner_user_id))

            return cur.fetchone() is not None
    
    def create_organizer(
        self,
        owner_user_id,
        name,
        description,
        phone,
        email,
        website_url,
        instagram_url,
        image_url
    ):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO organizers (
                    owner_user_id,
                    name,
                    description,
                    phone,
                    email,
                    website_url,
                    instagram_url,
                    image_url
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *;
            """, (
                owner_user_id,
                name,
                description,
                phone,
                email,
                website_url,
                instagram_url,
                image_url
            ))

            self.conn.commit()
            return cur.fetchone()


    def get_organizers_by_owner(self, owner_user_id):
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT *
                FROM organizers
                WHERE owner_user_id = %s
                ORDER BY created_at DESC;
            """, (owner_user_id,))

            return cur.fetchall()


    def delete_organizer(self, organizer_id, owner_user_id):
        with self.conn.cursor() as cur:
            cur.execute("""
                DELETE FROM organizers
                WHERE id = %s
                AND owner_user_id = %s
                RETURNING id;
            """, (organizer_id, owner_user_id))

            deleted = cur.fetchone()
            self.conn.commit()

            return deleted


    def get_organizers_by_owner(self, owner_user_id):
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT *
                FROM organizers
                WHERE owner_user_id = %s
                ORDER BY created_at DESC;
            """, (owner_user_id,))

            return cur.fetchall()


    def user_owns_organizer(self, organizer_id, owner_user_id):
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT id
                FROM organizers
                WHERE id = %s
                AND owner_user_id = %s;
            """, (organizer_id, owner_user_id))

            return cur.fetchone() is not None
    
    def user_owns_organizer(self, organizer_id, owner_user_id):
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT id
                FROM organizers
                WHERE id = %s
                AND owner_user_id = %s;
            """, (organizer_id, owner_user_id))

            return cur.fetchone() is not None


    def create_organizer_event(
        self,
        organizer_id,
        title,
        description,
        event_date,
        start_time,
        end_time,
        price,
        category,
        image_url,
        ticket_url,
        max_participants,
        event_address,
        event_city,
        event_latitude,
        event_longitude
    ):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO events (
                    organizer_id,
                    title,
                    description,
                    event_date,
                    start_time,
                    end_time,
                    price,
                    category,
                    image_url,
                    ticket_url,
                    max_participants,
                    event_address,
                    event_city,
                    event_latitude,
                    event_longitude
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *;
            """, (
                organizer_id,
                title,
                description,
                event_date,
                start_time,
                end_time,
                price,
                category,
                image_url,
                ticket_url,
                max_participants,
                event_address,
                event_city,
                event_latitude,
                event_longitude
            ))

            self.conn.commit()
            return cur.fetchone()


    def get_events_by_organizer(self, organizer_id, owner_user_id):
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT e.*
                FROM events e
                JOIN organizers o ON e.organizer_id = o.id
                WHERE e.organizer_id = %s
                AND o.owner_user_id = %s
                ORDER BY e.event_date DESC, e.start_time DESC;
            """, (organizer_id, owner_user_id))

            return cur.fetchall()

    def get_nearby_events(self, lat, lng, radius_km):
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT *
                FROM (
                    SELECT
                        e.id,
                        e.title,
                        e.description,
                        e.event_date AS date,
                        e.start_time,
                        e.end_time,
                        e.price,
                        e.category,
                        e.image_url,
                        e.ticket_url,
                        e.max_participants,

                        COALESCE(v.name, o.name) AS venue_name,
                        COALESCE(v.address, e.event_address) AS address,
                        COALESCE(v.city, e.event_city) AS city,
                        COALESCE(v.latitude, e.event_latitude) AS latitude,
                        COALESCE(v.longitude, e.event_longitude) AS longitude,

                        (
                            6371 * acos(
                                cos(radians(%s)) *
                                cos(radians(COALESCE(v.latitude, e.event_latitude))) *
                                cos(radians(COALESCE(v.longitude, e.event_longitude)) - radians(%s)) +
                                sin(radians(%s)) *
                                sin(radians(COALESCE(v.latitude, e.event_latitude)))
                            )
                        ) AS distance_km

                    FROM events e
                    LEFT JOIN venues v ON e.venue_id = v.id
                    LEFT JOIN organizers o ON e.organizer_id = o.id
                    
                    WHERE e.event_date >= CURRENT_DATE
                    AND COALESCE(v.latitude, e.event_latitude) IS NOT NULL
                    AND COALESCE(v.longitude, e.event_longitude) IS NOT NULL
                    
                ) nearby_events
                WHERE distance_km <= %s
                ORDER BY date ASC, start_time ASC;
            """, (lat, lng, lat, radius_km))

            return cur.fetchall()
        
    def get_events_by_city(self, city):
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT
                    e.id,
                    e.title,
                    e.description,
                    e.event_date AS date,
                    e.start_time,
                    e.end_time,
                    e.price,
                    e.category,
                    e.image_url,
                    e.ticket_url,
                    e.max_participants,

                    COALESCE(v.name, o.name) AS venue_name,
                    COALESCE(v.address, e.event_address) AS address,
                    COALESCE(v.city, e.event_city) AS city,
                    COALESCE(v.latitude, e.event_latitude) AS latitude,
                    COALESCE(v.longitude, e.event_longitude) AS longitude

                FROM events e
                LEFT JOIN venues v ON e.venue_id = v.id
                LEFT JOIN organizers o ON e.organizer_id = o.id
                WHERE e.event_date >= CURRENT_DATE
                AND LOWER(TRIM(COALESCE(v.city, e.event_city))) LIKE LOWER(%s)
                AND COALESCE(v.latitude, e.event_latitude) IS NOT NULL
                AND COALESCE(v.longitude, e.event_longitude) IS NOT NULL
                        
                ORDER BY e.event_date ASC, e.start_time ASC;
            """, (f"%{city.strip()}%",))

            return cur.fetchall()
        
    def delete_past_events(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                DELETE FROM events
                WHERE event_date < CURRENT_DATE
                RETURNING id;
            """)

            deleted = cur.fetchall()
            self.conn.commit()

            return deleted
        
    def update_event(
        self,
        event_id,
        owner_user_id,
        title,
        description,
        event_date,
        start_time,
        end_time,
        price,
        category,
        image_url,
        ticket_url,
        max_participants
    ):
        with self.conn.cursor() as cur:
            cur.execute("""
                UPDATE events e
                SET
                    title = %s,
                    description = %s,
                    event_date = %s,
                    start_time = %s,
                    end_time = %s,
                    price = %s,
                    category = %s,
                    image_url = %s,
                    ticket_url = %s,
                    max_participants = %s
                WHERE e.id = %s
                AND (
                    EXISTS (
                        SELECT 1
                        FROM venues v
                        WHERE v.id = e.venue_id
                        AND v.owner_user_id = %s
                    )
                    OR
                    EXISTS (
                        SELECT 1
                        FROM organizers o
                        WHERE o.id = e.organizer_id
                        AND o.owner_user_id = %s
                    )
                )
                RETURNING *;
            """, (
                title,
                description,
                event_date,
                start_time,
                end_time,
                price,
                category,
                image_url,
                ticket_url,
                max_participants,
                event_id,
                owner_user_id,
                owner_user_id
            ))

            updated = cur.fetchone()
            self.conn.commit()

            return updated
        
    def update_venue(
        self,
        venue_id,
        owner_user_id,
        venue_type_id,
        name,
        description,
        address,
        city,
        latitude,
        longitude,
        phone,
        email,
        website_url,
        instagram_url,
        image_url
    ):
        with self.conn.cursor() as cur:
            cur.execute("""
                UPDATE venues
                SET
                    venue_type_id = %s,
                    name = %s,
                    description = %s,
                    address = %s,
                    city = %s,
                    latitude = %s,
                    longitude = %s,
                    phone = %s,
                    email = %s,
                    website_url = %s,
                    instagram_url = %s,
                    image_url = %s,
                    updated_at = NOW()
                WHERE id = %s
                AND owner_user_id = %s
                RETURNING *;
            """, (
                venue_type_id,
                name,
                description,
                address,
                city,
                latitude,
                longitude,
                phone,
                email,
                website_url,
                instagram_url,
                image_url,
                venue_id,
                owner_user_id
            ))

            updated = cur.fetchone()
            self.conn.commit()
            return updated
        
    def update_organizer(
        self,
        organizer_id,
        owner_user_id,
        name,
        description,
        phone,
        email,
        website_url,
        instagram_url,
        image_url
    ):
        with self.conn.cursor() as cur:
            cur.execute("""
                UPDATE organizers
                SET
                    name = %s,
                    description = %s,
                    phone = %s,
                    email = %s,
                    website_url = %s,
                    instagram_url = %s,
                    image_url = %s,
                    updated_at = NOW()
                WHERE id = %s
                AND owner_user_id = %s
                RETURNING *;
            """, (
                name,
                description,
                phone,
                email,
                website_url,
                instagram_url,
                image_url,
                organizer_id,
                owner_user_id
            ))

            updated = cur.fetchone()
            self.conn.commit()
            return updated


    def add_event_favorite(self, user_id, event_id):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO user_event_favorites (user_id, event_id)
                VALUES (%s, %s)
                ON CONFLICT (user_id, event_id) DO NOTHING
                RETURNING *;
            """, (user_id, event_id))

            favorite = cur.fetchone()
            self.conn.commit()
            return favorite


    def remove_event_favorite(self, user_id, event_id):
        with self.conn.cursor() as cur:
            cur.execute("""
                DELETE FROM user_event_favorites
                WHERE user_id = %s
                AND event_id = %s
                RETURNING id;
            """, (user_id, event_id))

            deleted = cur.fetchone()
            self.conn.commit()
            return deleted


    def get_user_event_favorites(self, user_id):
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT
                    e.id,
                    e.title,
                    e.description,
                    e.event_date AS date,
                    e.start_time,
                    e.end_time,
                    e.price,
                    e.category,
                    e.image_url,
                    e.ticket_url,
                    e.max_participants,

                    COALESCE(v.name, o.name) AS venue_name,
                    COALESCE(v.address, e.event_address) AS address,
                    COALESCE(v.city, e.event_city) AS city,
                    COALESCE(v.latitude, e.event_latitude) AS latitude,
                    COALESCE(v.longitude, e.event_longitude) AS longitude,

                    f.created_at AS favorite_created_at

                FROM user_event_favorites f
                JOIN events e ON f.event_id = e.id
                LEFT JOIN venues v ON e.venue_id = v.id
                LEFT JOIN organizers o ON e.organizer_id = o.id
                WHERE f.user_id = %s
                ORDER BY e.event_date ASC, e.start_time ASC;
            """, (user_id,))

            return cur.fetchall()
        
    def add_venue_favorite(self, user_id, venue_id):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO user_venue_favorites (user_id, venue_id)
                VALUES (%s, %s)
                ON CONFLICT (user_id, venue_id) DO NOTHING
                RETURNING *;
            """, (user_id, venue_id))

            favorite = cur.fetchone()
            self.conn.commit()
            return favorite


    def remove_venue_favorite(self, user_id, venue_id):
        with self.conn.cursor() as cur:
            cur.execute("""
                DELETE FROM user_venue_favorites
                WHERE user_id = %s
                AND venue_id = %s
                RETURNING id;
            """, (user_id, venue_id))

            deleted = cur.fetchone()
            self.conn.commit()
            return deleted


    def get_user_venue_favorites(self, user_id):
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT
                    v.*,
                    vt.name AS venue_type_name,
                    vt.code AS venue_type_code,
                    f.created_at AS favorite_created_at
                FROM user_venue_favorites f
                JOIN venues v ON f.venue_id = v.id
                LEFT JOIN venue_types vt ON v.venue_type_id = vt.id
                WHERE f.user_id = %s
                ORDER BY f.created_at DESC;
            """, (user_id,))

            return cur.fetchall()
            
    def get_user_by_id(self, user_id):
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT id, name, email, avatar, city, role, password_hash
                FROM users
                WHERE id = %s;
            """, (user_id,))
    
            return cur.fetchone()
    
    
    def update_user_profile(self, user_id, name, email, city, avatar):
        with self.conn.cursor() as cur:
            cur.execute("""
                UPDATE users
                SET
                    name = %s,
                    email = %s,
                    city = %s,
                    avatar = %s
                WHERE id = %s
                RETURNING id, name, email, avatar, city, role;
            """, (name, email, city, avatar, user_id))
    
            updated = cur.fetchone()
            self.conn.commit()
            return updated
    
    
    def update_user_password(self, user_id, password_hash):
        with self.conn.cursor() as cur:
            cur.execute("""
                UPDATE users
                SET password_hash = %s
                WHERE id = %s
                RETURNING id;
            """, (password_hash, user_id))
    
            updated = cur.fetchone()
            self.conn.commit()
            return updated
    
    def close(self):
        self.conn.close()
