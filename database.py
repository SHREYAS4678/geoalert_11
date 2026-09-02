import sqlite3
import json
from datetime import datetime, timedelta

DB_NAME = "geoalert.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            node_id TEXT,
            timestamp TEXT,
            soil_moisture_pct REAL,
            rainfall_1h_mm REAL,
            rainfall_24h_mm REAL,
            temperature_c REAL,
            humidity_pct REAL,
            vibration_events_10min REAL,
            tilt_deg REAL,
            vibration_events_3h REAL,
            tilt_delta_3h REAL,
            soil_trend_3h REAL,
            risk_label INTEGER,
            risk_name TEXT,
            confidence REAL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            node_id TEXT,
            timestamp TEXT,
            severity TEXT,
            message TEXT,
            narrative TEXT,
            sent INTEGER
        )
    """)
    conn.commit()
    conn.close()

def insert_reading(node_id: str, features: dict, label: int, name: str, confidence: float):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
    cursor.execute("""
        INSERT INTO readings (
            node_id, timestamp, soil_moisture_pct, rainfall_1h_mm, rainfall_24h_mm,
            temperature_c, humidity_pct, vibration_events_10min, tilt_deg,
            vibration_events_3h, tilt_delta_3h, soil_trend_3h,
            risk_label, risk_name, confidence
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        node_id, now,
        features.get("soil_moisture_pct"), features.get("rainfall_1h_mm"), features.get("rainfall_24h_mm"),
        features.get("temperature_c"), features.get("humidity_pct"),
        features.get("vibration_events_10min"), features.get("tilt_deg"),
        features.get("vibration_events_3h"), features.get("tilt_delta_3h"), features.get("soil_trend_3h"),
        label, name, confidence
    ))
    conn.commit()
    conn.close()

def latest_reading(node_id: str = None):
    conn = get_connection()
    cursor = conn.cursor()
    if node_id:
        cursor.execute("SELECT * FROM readings WHERE node_id = ? ORDER BY id DESC LIMIT 1", (node_id,))
    else:
        cursor.execute("SELECT * FROM readings ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def recent_readings(node_id: str, hours: float = 24.0, limit: int = 500):
    conn = get_connection()
    cursor = conn.cursor()
    cutoff = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
    cursor.execute("""
        SELECT * FROM readings 
        WHERE node_id = ? AND timestamp >= ? 
        ORDER BY id ASC LIMIT ?
    """, (node_id, cutoff, limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def all_readings(limit: int = 500):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM readings ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def insert_alert(node_id: str, severity: str, message: str, narrative: str, sent: int):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
    cursor.execute("""
        INSERT INTO alerts (node_id, timestamp, severity, message, narrative, sent)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (node_id, now, severity, message, narrative, sent))
    conn.commit()
    conn.close()

def recent_alerts(limit: int = 50):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM alerts ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]
