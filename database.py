"""
Database module for AdventureAvenu website.
Handles SQLite connection, schema initialization, secure password hashing,
user registration & authentication, session management, and pre-saved locations search.
"""

import os
import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "adventure_avenu.db")
SCHEMA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema.sql")

# Password Hashing Constants (NIST recommended)
HASH_ALGORITHM = "sha256"
HASH_ITERATIONS = 100_000
SALT_BYTES = 16

# Predefined locations list
PREDEFINED_LOCATIONS = [
    {
        "name": "The Ritz-Carlton & Eiffel Tower",
        "city": "Paris",
        "country": "France",
        "category": "Culture & Romance",
        "description": "Experience the City of Love with its iconic Eiffel Tower, Louvre Museum, exquisite French cuisine, and charming historic boulevards.",
        "image_url": "Image/hotel/The Ritz-Carlton, Paris.webp",
        "price_level": "$$$$"
    },
    {
        "name": "Maldives Tropical Island Resort",
        "city": "Male Atoll",
        "country": "Maldives",
        "category": "Beach & Island",
        "description": "Crystal-clear turquoise waters, private overwater luxury bungalows, pristine coral reefs, and world-class scuba diving.",
        "image_url": "Image/maldiv.jpg",
        "price_level": "$$$$"
    },
    {
        "name": "New York City Times Square & Central Park",
        "city": "New York",
        "country": "USA",
        "category": "City & Entertainment",
        "description": "The city that never sleeps: Broadway theaters, iconic skyscrapers, Central Park strolls, and world-renowned dining and nightlife.",
        "image_url": "Image/New York.png.png",
        "price_level": "$$$"
    },
    {
        "name": "Aman Tokyo & Heritage Temples",
        "city": "Tokyo",
        "country": "Japan",
        "category": "City & Culture",
        "description": "A dazzling blend of futuristic neon architecture, historic Shinto shrines, tranquil gardens, and Michelin-starred culinary excellence.",
        "image_url": "Image/hotel/Aman Tokyo.jpeg",
        "price_level": "$$$$"
    },
    {
        "name": "Vrindavan Heritage & Holi Celebrations",
        "city": "Vrindavan",
        "country": "India",
        "category": "Culture & Spiritual",
        "description": "Sacred cultural town celebrated for vibrant Holi festival gatherings, centuries-old temples, and serene spiritual traditions.",
        "image_url": "Image/Vrindavan Holi festival.jpg",
        "price_level": "$"
    },
    {
        "name": "Ventana Wilderness Campground",
        "city": "Big Sur, California",
        "country": "USA",
        "category": "Nature & Camping",
        "description": "Dramatic Pacific coastal bluffs, soaring coastal redwoods, wilderness hiking trails, and breathtaking stargazing camps.",
        "image_url": "Image/Campaning.png.png",
        "price_level": "$$"
    },
    {
        "name": "Pohela Boishakh Heritage Rally",
        "city": "Dhaka",
        "country": "Bangladesh",
        "category": "Culture & Heritage",
        "description": "Vibrant Bengali New Year festivities, colourful Mangal Shobhajatra processions, Mughal architecture, and rich culinary street food.",
        "image_url": "Image/boishakhi.png.jpg",
        "price_level": "$"
    },
    {
        "name": "Burj Al Arab & Desert Safari",
        "city": "Dubai",
        "country": "United Arab Emirates",
        "category": "Luxury & Modern",
        "description": "Iconic sail-shaped 7-star architecture, desert dune safaris, world-famous luxury shopping, and golden Persian Gulf beaches.",
        "image_url": "Image/hotel/Burj Al Arab Jumeirah.jpg",
        "price_level": "$$$$"
    },
    {
        "name": "The Ritz London & Westminster",
        "city": "London",
        "country": "United Kingdom",
        "category": "History & Heritage",
        "description": "Classic British elegance with Big Ben, Tower Bridge, British Museum, Hyde Park, and traditional afternoon tea.",
        "image_url": "Image/hotel/The Ritz London.webp",
        "price_level": "$$$$"
    },
    {
        "name": "Belmond Hotel Caruso & Amalfi Cliffs",
        "city": "Amalfi Coast",
        "country": "Italy",
        "category": "Scenic & Coastal",
        "description": "Perched on dramatic sun-drenched Mediterranean cliffs, offering panoramic sea views, lemon groves, and authentic Italian pasta.",
        "image_url": "Image/hotel/Belmond Hotel Caruso.webp",
        "price_level": "$$$$"
    },
    {
        "name": "Mandarin Oriental Chao Phraya",
        "city": "Bangkok",
        "country": "Thailand",
        "category": "Culture & River",
        "description": "Golden Grand Palace temples, floating river markets, bustling night bazaars, and warm Thai royal hospitality.",
        "image_url": "Image/hotel/Mandarin Oriental, Bangkok.jpg",
        "price_level": "$$$"
    },
    {
        "name": "Plaza Hotel & The Strip",
        "city": "Las Vegas",
        "country": "USA",
        "category": "Entertainment & Nightlife",
        "description": "World-famous neon strip, spectacular concerts, world-class entertainment, and luxury resort dining.",
        "image_url": "Image/hotel/plaza hotel las vegas.jpg",
        "price_level": "$$$"
    },
    {
        "name": "Hôtel de Glace Winter Wonderland",
        "city": "Quebec City",
        "country": "Canada",
        "category": "Winter & Adventure",
        "description": "Architectural marvel sculpted entirely of ice and snow, surrounded by French-Canadian cobblestone streets and cozy bistros.",
        "image_url": "Image/hotel/Hotel de Glace.jpg",
        "price_level": "$$$"
    },
    {
        "name": "Emirates Palace Grand Retreat",
        "city": "Abu Dhabi",
        "country": "United Arab Emirates",
        "category": "Luxury & Architecture",
        "description": "Opulent Arabian palace overlooking pristine private bay, near the stunning Sheikh Zayed Grand Mosque and Louvre Abu Dhabi.",
        "image_url": "Image/hotel/Emirates Palace.jpg",
        "price_level": "$$$$"
    },
    {
        "name": "Four Seasons George V Paris",
        "city": "Paris",
        "country": "France",
        "category": "Luxury & Romance",
        "description": "Steps from the Champs-Élysées with private terraces overlooking the Eiffel Tower and world-renowned floral artistry.",
        "image_url": "Image/hotel/Four Seasons Hotel George V.jpg",
        "price_level": "$$$$"
    },
    {
        "name": "Ancient Colosseum & Roman Forum",
        "city": "Rome",
        "country": "Italy",
        "category": "History & Culture",
        "description": "The Eternal City featuring the ancient Colosseum, Pantheon, Vatican City, and lively piazza dining.",
        "image_url": "Image/pexels-aleksandar-pasaric-2341830.jpg",
        "price_level": "$$$"
    }
]


def get_db():
    """Returns a connection to the SQLite database with row_factory enabled."""
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Initializes database tables and seeds predefined locations if not present."""
    conn = get_db()
    with conn:
        # Load and execute schema
        if os.path.exists(SCHEMA_FILE):
            with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
                conn.executescript(f.read())
        else:
            # Fallback inline schema creation
            conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                first_name TEXT,
                last_name TEXT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                password_salt TEXT NOT NULL,
                gender TEXT,
                country TEXT,
                birth_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                token TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """)
            conn.execute("""
            CREATE TABLE IF NOT EXISTS locations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                city TEXT NOT NULL,
                country TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                image_url TEXT,
                price_level TEXT DEFAULT '$$'
            )
            """)

        # Check if locations are already seeded
        cur = conn.execute("SELECT COUNT(*) AS cnt FROM locations")
        count = cur.fetchone()["cnt"]
        if count == 0:
            for loc in PREDEFINED_LOCATIONS:
                conn.execute("""
                INSERT INTO locations (name, city, country, category, description, image_url, price_level)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    loc["name"],
                    loc["city"],
                    loc["country"],
                    loc["category"],
                    loc["description"],
                    loc["image_url"],
                    loc["price_level"]
                ))
            print(f"[Database] Seeded {len(PREDEFINED_LOCATIONS)} predefined locations.")
    conn.close()


def hash_password(password: str, salt: bytes = None) -> tuple:
    """Hashes a password using PBKDF2-HMAC-SHA256 with 100,000 iterations."""
    if salt is None:
        salt = secrets.token_bytes(SALT_BYTES)
    key = hashlib.pbkdf2_hmac(HASH_ALGORITHM, password.encode("utf-8"), salt, HASH_ITERATIONS)
    return key.hex(), salt.hex()


def verify_password(password: str, stored_hash: str, stored_salt_hex: str) -> bool:
    """Verifies a password against the stored salt and hash using constant-time comparison."""
    try:
        salt = bytes.fromhex(stored_salt_hex)
        key = hashlib.pbkdf2_hmac(HASH_ALGORITHM, password.encode("utf-8"), salt, HASH_ITERATIONS)
        return secrets.compare_digest(key.hex(), stored_hash)
    except Exception:
        return False


def register_user(name: str, email: str, password: str, first_name: str = "",
                  last_name: str = "", gender: str = "", country: str = "", birth_date: str = ""):
    """Registers a new user into the SQL database with salted password hash."""
    name = (name or "").strip()
    email = (email or "").strip().lower()
    password = password or ""

    if not email:
        return {"success": False, "error": "Email or phone number is required."}
    if not password:
        return {"success": False, "error": "Password is required."}
    if len(password) < 6:
        return {"success": False, "error": "Password must be at least 6 characters long."}

    # If full name is empty, combine first and last names
    if not name:
        name = f"{first_name} {last_name}".strip() or email.split("@")[0]

    pwd_hash, salt_hex = hash_password(password)

    conn = get_db()
    try:
        with conn:
            cur = conn.execute("""
            INSERT INTO users (name, first_name, last_name, email, password_hash, password_salt, gender, country, birth_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, first_name, last_name, email, pwd_hash, salt_hex, gender, country, birth_date))
            user_id = cur.lastrowid
        return {
            "success": True,
            "user": {
                "id": user_id,
                "name": name,
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "gender": gender,
                "country": country,
                "birth_date": birth_date
            }
        }
    except sqlite3.IntegrityError:
        return {"success": False, "error": "An account with this email or phone number already exists."}
    except Exception as e:
        return {"success": False, "error": f"Database error: {str(e)}"}
    finally:
        conn.close()


def authenticate_user(email: str, password: str):
    """Authenticates a user with email and password."""
    email = (email or "").strip().lower()
    password = password or ""

    if not email or not password:
        return {"success": False, "error": "Email and password are required."}

    conn = get_db()
    try:
        cur = conn.execute("""
        SELECT id, name, first_name, last_name, email, password_hash, password_salt, gender, country, birth_date
        FROM users
        WHERE LOWER(email) = ?
        """, (email,))
        row = cur.fetchone()

        if not row:
            return {"success": False, "error": "Invalid email/phone or password."}

        if not verify_password(password, row["password_hash"], row["password_salt"]):
            return {"success": False, "error": "Invalid email/phone or password."}

        return {
            "success": True,
            "user": {
                "id": row["id"],
                "name": row["name"],
                "email": row["email"],
                "first_name": row["first_name"],
                "last_name": row["last_name"],
                "gender": row["gender"],
                "country": row["country"],
                "birth_date": row["birth_date"]
            }
        }
    finally:
        conn.close()


def create_session(user_id: int, days_valid: int = 7) -> str:
    """Creates a secure session token stored in the sessions SQL table."""
    token = secrets.token_hex(32)
    expires_at = datetime.utcnow() + timedelta(days=days_valid)

    conn = get_db()
    try:
        with conn:
            conn.execute("""
            INSERT INTO sessions (token, user_id, expires_at)
            VALUES (?, ?, ?)
            """, (token, user_id, expires_at.isoformat()))
        return token
    finally:
        conn.close()


def get_user_by_session(token: str):
    """Retrieves user profile associated with an active session token."""
    if not token:
        return None

    conn = get_db()
    try:
        cur = conn.execute("""
        SELECT u.id, u.name, u.first_name, u.last_name, u.email, u.gender, u.country, u.birth_date, s.expires_at
        FROM sessions s
        JOIN users u ON s.user_id = u.id
        WHERE s.token = ?
        """, (token,))
        row = cur.fetchone()

        if not row:
            return None

        # Check expiration
        try:
            exp = datetime.fromisoformat(row["expires_at"])
            if datetime.utcnow() > exp:
                delete_session(token)
                return None
        except Exception:
            pass

        return {
            "id": row["id"],
            "name": row["name"],
            "first_name": row["first_name"],
            "last_name": row["last_name"],
            "email": row["email"],
            "gender": row["gender"],
            "country": row["country"],
            "birth_date": row["birth_date"]
        }
    finally:
        conn.close()


def delete_session(token: str):
    """Deletes a session from the SQL database."""
    if not token:
        return
    conn = get_db()
    try:
        with conn:
            conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
    finally:
        conn.close()


def search_locations(query: str = "", limit: int = 20):
    """Searches predefined locations using SQL LIKE pattern matching."""
    conn = get_db()
    try:
        q = (query or "").strip()
        if not q:
            cur = conn.execute("""
            SELECT id, name, city, country, category, description, image_url, price_level
            FROM locations
            ORDER BY name ASC
            LIMIT ?
            """, (limit,))
        else:
            term = f"%{q}%"
            cur = conn.execute("""
            SELECT id, name, city, country, category, description, image_url, price_level
            FROM locations
            WHERE name LIKE ? OR city LIKE ? OR country LIKE ? OR category LIKE ? OR description LIKE ?
            ORDER BY
                CASE
                    WHEN name LIKE ? THEN 1
                    WHEN city LIKE ? THEN 2
                    WHEN country LIKE ? THEN 3
                    ELSE 4
                END,
                name ASC
            LIMIT ?
            """, (term, term, term, term, term, f"{q}%", f"{q}%", f"{q}%", limit))

        rows = cur.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_location_by_id(loc_id: int):
    """Returns single location by primary key."""
    conn = get_db()
    try:
        cur = conn.execute("""
        SELECT id, name, city, country, category, description, image_url, price_level
        FROM locations
        WHERE id = ?
        """, (loc_id,))
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()
