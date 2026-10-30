#!/usr/bin/env python3
"""
Database Initialization & Management CLI for AdventureAvenu.
Run this script to inspect, initialize, or reseed the SQL database.
Usage:
    python3 init_db.py          # Initialize / ensure tables and predefined locations exist
    python3 init_db.py --reset  # Drop existing tables and recreate freshly
    python3 init_db.py --list   # List all registered users and predefined locations
"""

import sys
import database

def main():
    if "--reset" in sys.argv:
        confirm = input("Are you sure you want to reset the database? All users and data will be wiped! (y/N): ")
        if confirm.lower().strip() == "y":
            conn = database.get_db()
            with conn:
                conn.execute("DROP TABLE IF EXISTS sessions")
                conn.execute("DROP TABLE IF EXISTS users")
                conn.execute("DROP TABLE IF EXISTS locations")
            conn.close()
            print("Dropped all tables.")
            database.init_db()
            print("Database re-initialized and re-seeded successfully.")
        else:
            print("Reset cancelled.")
        return

    if "--list" in sys.argv:
        conn = database.get_db()
        users = conn.execute("SELECT id, name, email, country, created_at FROM users").fetchall()
        locations = conn.execute("SELECT id, name, city, country, category FROM locations").fetchall()
        conn.close()

        print("\n--- Registered Users in SQL Database ---")
        if not users:
            print("No registered users yet.")
        else:
            for u in users:
                print(f"[{u['id']}] {u['name']} <{u['email']}> ({u['country']}) - Created: {u['created_at']}")

        print(f"\n--- Pre-Saved Locations in SQL Database ({len(locations)}) ---")
        for loc in locations:
            print(f"[{loc['id']}] {loc['name']} - {loc['city']}, {loc['country']} [{loc['category']}]")
        print()
        return

    # Default action: ensure database is initialized
    database.init_db()
    conn = database.get_db()
    user_cnt = conn.execute("SELECT COUNT(*) AS c FROM users").fetchone()["c"]
    loc_cnt = conn.execute("SELECT COUNT(*) AS c FROM locations").fetchone()["c"]
    conn.close()
    print("=" * 60)
    print(" AdventureAvenu SQL Database Status")
    print("=" * 60)
    print(f" Database file: {database.DB_FILE}")
    print(f" Registered users:     {user_cnt}")
    print(f" Pre-saved locations:  {loc_cnt}")
    print("=" * 60)

if __name__ == "__main__":
    main()
