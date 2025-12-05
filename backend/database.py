import sqlite3
import json
import os
from typing import List, Optional
from models import Trip

# Use environment variable for DB path if set (for Docker volume), else default
DB_NAME = os.getenv("DB_PATH", "good_friend.db")

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS trips (
            id TEXT PRIMARY KEY,
            name TEXT,
            status TEXT,
            data TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_trip(trip: Trip):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Upsert (Insert or Replace)
    c.execute('''
        INSERT OR REPLACE INTO trips (id, name, status, data)
        VALUES (?, ?, ?, ?)
    ''', (trip.id, trip.name, trip.status, trip.model_dump_json()))
    conn.commit()
    conn.close()

def get_trip(trip_id: str) -> Optional[Trip]:
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT data FROM trips WHERE id = ?', (trip_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return Trip.model_validate_json(row[0])
    return None

def list_trips() -> List[Trip]:
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT data FROM trips')
    rows = c.fetchall()
    conn.close()
    return [Trip.model_validate_json(row[0]) for row in rows]

def delete_trip(trip_id: str):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('DELETE FROM trips WHERE id = ?', (trip_id,))
    conn.commit()
    conn.close()
