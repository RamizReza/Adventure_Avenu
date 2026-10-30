# AdventureAvenu - Full SQL Database & Backend Integration

This project is a fully functional travel website with an integrated **SQL database (SQLite)**, providing secure user registration, user authentication (login/logout), session management, and pre-saved location search, all while strictly preserving your original HTML/CSS design, layouts, and styles.

---

## 🚀 Quick Start (How to Run)

The backend is built using standard Python 3 with **zero external dependencies** required (no `pip install` needed).

1. Open your Terminal and navigate to the project directory:
   ```bash
   cd "/Users/md.ramizreja/Downloads/Aunkita-420582/web"
   ```

2. Start the backend server:
   ```bash
   python3 server.py
   ```

3. Open your browser and go to:
   - **Home Page:** [http://localhost:8000/home.html](http://localhost:8000/home.html)
   - **Sign Up:** [http://localhost:8000/singup.html](http://localhost:8000/singup.html)
   - **Login:** [http://localhost:8000/login.html](http://localhost:8000/login.html)
   - **Landing Page:** [http://localhost:8000/index.html](http://localhost:8000/index.html)

---

## 🗄️ SQL Database Details

- **Database Engine:** SQLite 3 (stored locally in `adventure_avenu.db`)
- **SQL Schema File:** `schema.sql`
- **Database Module:** `database.py`

### Tables Created:
1. `users`: Stores registered user information.
   - `id`: INTEGER PRIMARY KEY AUTOINCREMENT
   - `name`: TEXT NOT NULL
   - `first_name`: TEXT
   - `last_name`: TEXT
   - `email`: TEXT UNIQUE NOT NULL
   - `password_hash`: TEXT NOT NULL (PBKDF2-HMAC-SHA256)
   - `password_salt`: TEXT NOT NULL (16-byte random salt)
   - `gender`: TEXT
   - `country`: TEXT
   - `birth_date`: TEXT
   - `created_at`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

2. `sessions`: Manages secure login sessions.
   - `token`: TEXT PRIMARY KEY
   - `user_id`: INTEGER (Foreign key to `users.id`)
   - `created_at`: TIMESTAMP
   - `expires_at`: TIMESTAMP

3. `locations`: Stores predefined saved destinations.
   - `id`: INTEGER PRIMARY KEY AUTOINCREMENT
   - `name`: TEXT NOT NULL
   - `city`: TEXT NOT NULL
   - `country`: TEXT NOT NULL
   - `category`: TEXT NOT NULL (e.g., Island & Beach, Culture & Romance)
   - `description`: TEXT NOT NULL
   - `image_url`: TEXT (Matches existing images in the website)
   - `price_level`: TEXT

---

## 🔒 Security Architecture

- **Password Hashing:** Passwords are never stored in plaintext. Passwords use **PBKDF2-HMAC-SHA256** with **100,000 iterations** and a unique cryptographically secure 16-byte salt per user (`secrets.token_bytes(16)`).
- **SQL Injection Prevention:** Every database query strictly uses parameterized SQL queries (`?` placeholders).
- **Session Protection:** Session tokens are 256-bit random hex strings stored with `HttpOnly` and `SameSite=Lax` cookies, preventing unauthorized script access.
- **Timing Attack Resistance:** Password verification uses `secrets.compare_digest` for constant-time comparison.

---

## 🌟 Implemented Features

### 1. User Registration (Sign Up) - `singup.html`
- Collects Full Name, Email/Phone, First Name, Last Name, Password, Gender, Country, and Birth Date.
- Validates password length and required fields.
- Checks if the user already exists in the SQL database.
- Saves the user securely in the `users` SQL table.
- Automatically logs the user in upon registration and redirects to `home.html`.
- Displays real-time feedback messages (errors or success) directly on the form without disrupting the layout.

### 2. User Login & Authentication - `login.html`
- Authenticates users against the SQL database.
- Verifies hashed passwords using salted PBKDF2.
- Creates an active session token in the SQL database upon valid credentials.
- Displays helpful error messages if email or password does not match.
- Smoothly redirects to `home.html`.
- Updates the top navigation on pages to display `Welcome, [User Name]` and a working `Logout` button.

### 3. Pre-Saved Location Search
- Preloaded with 16 predefined destinations in the SQL database matching the photos and themes of the website (Paris, Maldives, New York, Tokyo, Dubai, London, Rome, Dhaka, Vrindavan, California, Amalfi Coast, Bangkok, Las Vegas, Quebec, etc.).
- **Live Autocomplete Dropdown:** As users type into destination search fields (in `home.html`, `index.html`, or `Hotel.html`), a dropdown automatically fetches and displays matching locations from the SQL database in real-time.
- **Integrated Results Display:** Clicking "Search" queries the SQL database and renders a responsive card grid showing photo, destination name, country, description, category, and a "Select Destination" button right on the page (no redirect to external search engines).

---

## 🛠️ Database Management CLI

A helper script `init_db.py` is included to inspect or manage the database:

- **Check database statistics:**
  ```bash
  python3 init_db.py
  ```
- **List all registered users and predefined locations:**
  ```bash
  python3 init_db.py --list
  ```
- **Reset database (wipe & re-seed):**
  ```bash
  python3 init_db.py --reset
  ```

---

## 🧪 Running Automated Tests

Run the full automated integration test suite:
```bash
python3 test_integration.py
```
This tests static serving, SQL queries, user registration, password hashing verification, duplicate rejection, login, incorrect credentials handling, session checks, and logout.
