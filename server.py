#!/usr/bin/env python3
"""
AdventureAvenu Backend Server
Standard-library Python server providing:
- Full static file serving for HTML, CSS, JS, and multimedia assets.
- SQL Database integration for user registration (sign-up) with secure salted password hashing.
- SQL Database integration for user authentication (login/logout) with session management.
- Pre-saved locations SQL search API with parameterized queries.
"""

import os
import sys
import json
import urllib.parse
from http import cookies
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn

import database

# Working directory is the directory where server.py lives
WEB_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(WEB_DIR)

PORT = 8000


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


class AdventureAvenuHandler(SimpleHTTPRequestHandler):
    """Custom request handler integrating backend SQL API routes with static files."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    # ---------------- Helper Methods ----------------

    def send_json(self, data, status=200, headers=None):
        """Sends a JSON response with status code and optional headers."""
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        origin = self.headers.get("Origin")
        if origin:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Access-Control-Allow-Credentials", "true")
        else:
            self.send_header("Access-Control-Allow-Origin", "*")
        if headers:
            for k, v in headers.items():
                self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def parse_request_data(self):
        """Parses incoming JSON or Form-Urlencoded POST body."""
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length <= 0:
            return {}

        body = self.rfile.read(content_length).decode("utf-8", errors="replace")
        content_type = self.headers.get("Content-Type", "")

        if "application/json" in content_type:
            try:
                return json.loads(body)
            except Exception:
                return {}
        else:
            # application/x-www-form-urlencoded or plain text
            parsed = urllib.parse.parse_qs(body, keep_blank_values=True)
            return {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}

    def get_session_token(self):
        """Extracts session_id token from the Authorization header or Cookie."""
        auth_header = self.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:].strip()
            if token:
                return token

        cookie_header = self.headers.get("Cookie")
        if not cookie_header:
            return None
        c = cookies.SimpleCookie()
        try:
            c.load(cookie_header)
            if "session_id" in c:
                return c["session_id"].value
        except Exception:
            return None
        return None

    def get_current_user(self):
        """Retrieves currently authenticated user from session token."""
        token = self.get_session_token()
        if not token:
            return None
        return database.get_user_by_session(token)

    # ---------------- HTTP Method Handlers ----------------

    def do_OPTIONS(self):
        """Handles CORS preflight requests."""
        self.send_response(204)
        origin = self.headers.get("Origin")
        if origin:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Access-Control-Allow-Credentials", "true")
        else:
            self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Cookie, Authorization")
        self.end_headers()

    def do_GET(self):
        """Handles GET requests for static files and API endpoints."""
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # Root route redirects/serves index.html
        if path == "/" or path == "":
            self.path = "/index.html"
            return super().do_GET()

        # API: Pre-saved locations search
        if path == "/api/locations":
            query_params = urllib.parse.parse_qs(parsed.query)
            q = query_params.get("q", [""])[0]
            limit = int(query_params.get("limit", [20])[0])
            locations = database.search_locations(query=q, limit=limit)
            return self.send_json({"success": True, "count": len(locations), "locations": locations})

        # API: Single location detail
        if path.startswith("/api/locations/"):
            try:
                loc_id = int(path.split("/")[-1])
                location = database.get_location_by_id(loc_id)
                if location:
                    return self.send_json({"success": True, "location": location})
                return self.send_json({"success": False, "error": "Location not found"}, status=404)
            except ValueError:
                return self.send_json({"success": False, "error": "Invalid location ID"}, status=400)

        # API: Get current logged-in user profile
        if path == "/api/me":
            user = self.get_current_user()
            if user:
                return self.send_json({"logged_in": True, "user": user})
            return self.send_json({"logged_in": False, "user": None})

        # API/Route: Logout
        if path in ("/api/logout", "/logout"):
            token = self.get_session_token()
            if token:
                database.delete_session(token)
            # Clear cookie and redirect to login
            headers = {
                "Set-Cookie": "session_id=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT; Max-Age=0"
            }
            if path == "/logout":
                self.send_response(302)
                self.send_header("Location", "/login.html")
                for k, v in headers.items():
                    self.send_header(k, v)
                self.end_headers()
                return
            return self.send_json({"success": True, "message": "Logged out successfully."}, headers=headers)

        # Serve static file via standard handler
        return super().do_GET()

    def do_POST(self):
        """Handles POST requests for signup, login, logout, and search."""
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        data = self.parse_request_data()

        # API: User Registration (Sign Up)
        if path == "/api/signup":
            name = data.get("name", "").strip()
            first_name = data.get("firstname", "").strip()
            last_name = data.get("lastname", "").strip()
            email = data.get("email", "").strip()
            password = data.get("password", "")
            gender = data.get("gender", "")
            country = data.get("country", "")
            birth_date = data.get("birth_date", "")

            # If full name is omitted, assemble from first + last
            if not name and (first_name or last_name):
                name = f"{first_name} {last_name}".strip()

            result = database.register_user(
                name=name,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                gender=gender,
                country=country,
                birth_date=birth_date
            )

            if not result.get("success"):
                return self.send_json(result, status=400)

            # Auto-login upon successful registration
            user = result["user"]
            token = database.create_session(user["id"])
            headers = {
                "Set-Cookie": f"session_id={token}; Path=/; HttpOnly; SameSite=Lax; Max-Age=604800"
            }
            return self.send_json({
                "success": True,
                "message": "Account created successfully!",
                "token": token,
                "user": user
            }, status=201, headers=headers)

        # API: User Login
        if path == "/api/login":
            email = data.get("email", "").strip()
            password = data.get("password", "")

            result = database.authenticate_user(email, password)
            if not result.get("success"):
                return self.send_json(result, status=401)

            user = result["user"]
            token = database.create_session(user["id"])
            headers = {
                "Set-Cookie": f"session_id={token}; Path=/; HttpOnly; SameSite=Lax; Max-Age=604800"
            }
            return self.send_json({
                "success": True,
                "message": "Login successful!",
                "token": token,
                "user": user
            }, status=200, headers=headers)

        # API: User Logout (POST)
        if path == "/api/logout":
            token = self.get_session_token()
            if token:
                database.delete_session(token)
            headers = {
                "Set-Cookie": "session_id=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT; Max-Age=0"
            }
            return self.send_json({"success": True, "message": "Logged out successfully."}, headers=headers)

        # API: Locations search via POST
        if path == "/api/locations/search":
            q = data.get("q", "").strip()
            limit = int(data.get("limit", 20))
            locations = database.search_locations(query=q, limit=limit)
            return self.send_json({"success": True, "count": len(locations), "locations": locations})

        # Unknown route
        return self.send_json({"success": False, "error": f"Endpoint not found: {path}"}, status=404)


def run_server(port=PORT):
    """Initializes database and starts multi-threaded server."""
    database.init_db()
    print("=" * 60)
    print(" AdventureAvenu Backend Server & SQL Database")
    print("=" * 60)
    print(f" Web Root:  {WEB_DIR}")
    print(f" Database:  {database.DB_FILE}")

    server_address = ("", port)
    try:
        httpd = ThreadedHTTPServer(server_address, AdventureAvenuHandler)
    except OSError:
        port = port + 1
        server_address = ("", port)
        httpd = ThreadedHTTPServer(server_address, AdventureAvenuHandler)

    url = f"http://localhost:{port}"
    print(f" Server running at: {url}")
    print(f" - Home:       {url}/home.html")
    print(f" - Login:      {url}/login.html")
    print(f" - Sign Up:    {url}/singup.html")
    print(f" - API Pre-saved Locations: {url}/api/locations")
    print("=" * 60)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer shutting down gracefully.")
        httpd.server_close()


if __name__ == "__main__":
    p = PORT
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        p = int(sys.argv[1])
    run_server(p)
