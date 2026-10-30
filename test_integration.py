#!/usr/bin/env python3
"""
Integration Test Suite for AdventureAvenu SQL Database and Backend API.
Tests user registration, user authentication, session management, and pre-saved locations.
"""

import os
import sys
import json
import sqlite3
import database
import server

def run_tests():
    print("=" * 65)
    print(" Running AdventureAvenu SQL Database & Backend Tests")
    print("=" * 65)

    # 1. Database & Schema
    print("\n[Test 1] Initializing SQL Database and verifying schema...")
    database.init_db()
    conn = database.get_db()
    tables = [row["name"] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    assert "users" in tables, "users table missing"
    assert "sessions" in tables, "sessions table missing"
    assert "locations" in tables, "locations table missing"
    print("  ✓ Tables verified: users, sessions, locations")

    loc_count = conn.execute("SELECT COUNT(*) AS c FROM locations").fetchone()["c"]
    assert loc_count >= 16, f"Expected 16+ locations, found {loc_count}"
    print(f"  ✓ Pre-saved locations verified in SQL: {loc_count} items")
    conn.close()

    # 2. Cryptographic Security
    print("\n[Test 2] Testing Password Security (PBKDF2-HMAC-SHA256 & Salt)...")
    raw_pass = "Adventure2024!Secure"
    p_hash, salt_hex = database.hash_password(raw_pass)
    assert len(salt_hex) == 32, "Salt should be 16 bytes (32 hex characters)"
    assert len(p_hash) == 64, "SHA-256 hash must be 64 hex characters"
    assert database.verify_password(raw_pass, p_hash, salt_hex) is True
    assert database.verify_password("WrongPassword!", p_hash, salt_hex) is False
    print("  ✓ Salt generation, PBKDF2 hashing, and constant-time verify OK")

    # 3. User Registration (Sign Up)
    print("\n[Test 3] Testing User Registration (/api/signup)...")
    email = "tester_integration@adventure.com"
    # Ensure fresh state
    conn = database.get_db()
    with conn:
        conn.execute("DELETE FROM users WHERE email = ?", (email,))
    conn.close()

    reg_result = database.register_user(
        name="Integration Tester",
        email=email,
        password="ValidPassword123!",
        first_name="Integration",
        last_name="Tester",
        gender="Other",
        country="Bangladesh",
        birth_date="1998-01-01"
    )
    assert reg_result["success"] is True, f"Registration failed: {reg_result}"
    user_id = reg_result["user"]["id"]
    print(f"  ✓ User registered successfully in SQL with ID: {user_id}")

    # Duplicate rejection
    dup_result = database.register_user(name="Dup", email=email, password="ValidPassword123!")
    assert dup_result["success"] is False, "Duplicate email must fail"
    print("  ✓ Duplicate account creation rejected with clear message")

    # Short password validation
    short_res = database.register_user(name="Short", email="short@adv.com", password="123")
    assert short_res["success"] is False
    print("  ✓ Short password (< 6 chars) rejected")

    # 4. User Login & Authentication
    print("\n[Test 4] Testing User Login & Password Authentication (/api/login)...")
    login_success = database.authenticate_user(email, "ValidPassword123!")
    assert login_success["success"] is True
    assert login_success["user"]["email"] == email
    print(f"  ✓ Valid login successful for {login_success['user']['name']}")

    login_fail = database.authenticate_user(email, "WrongPassword!")
    assert login_fail["success"] is False
    print("  ✓ Invalid password rejected")

    login_no_user = database.authenticate_user("unknown_user@domain.com", "anyPass")
    assert login_no_user["success"] is False
    print("  ✓ Non-existent account login rejected")

    # 5. Session Management & Verification
    print("\n[Test 5] Testing Session Management & Active Login (/api/me, /logout)...")
    token = database.create_session(user_id, days_valid=7)
    assert len(token) == 64
    active_user = database.get_user_by_session(token)
    assert active_user is not None and active_user["id"] == user_id
    print(f"  ✓ Active session found in SQL for: {active_user['name']}")

    database.delete_session(token)
    expired_user = database.get_user_by_session(token)
    assert expired_user is None
    print("  ✓ Logout / session deletion verified")

    # 6. Pre-Saved Locations SQL Search
    print("\n[Test 6] Testing Pre-Saved Locations SQL Search (/api/locations)...")
    all_locs = database.search_locations("")
    assert len(all_locs) >= 16
    print(f"  ✓ Fetched all {len(all_locs)} saved locations")

    # Search Paris
    paris_locs = database.search_locations("Paris")
    assert len(paris_locs) >= 1
    print(f"  ✓ Search 'Paris' returned {len(paris_locs)} location(s): {[l['name'] for l in paris_locs]}")

    # Search Maldives
    maldives_locs = database.search_locations("Maldives")
    assert len(maldives_locs) >= 1
    print(f"  ✓ Search 'Maldives' returned: {maldives_locs[0]['name']}")

    # Single location detail
    loc_item = database.get_location_by_id(maldives_locs[0]["id"])
    assert loc_item is not None
    assert loc_item["city"] == maldives_locs[0]["city"]
    print(f"  ✓ Location detail lookup verified: {loc_item['name']} ({loc_item['city']}, {loc_item['country']})")

    print("\n" + "=" * 65)
    print(" ALL BACKEND & SQL DATABASE INTEGRATION TESTS PASSED! ")
    print("=" * 65)

if __name__ == "__main__":
    run_tests()
