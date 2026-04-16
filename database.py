import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "scenario.db"


# -----------------------
# CONNECTION
# -----------------------
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# -----------------------
# INIT DB (clean schema)
# -----------------------
def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scenarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        date TEXT,
        mission_brief TEXT,
        intel_summary TEXT,

        start_coord TEXT,
        destination_coord TEXT,

        enemy_last_seen TEXT,
        enemy_predicted TEXT,

        enemy_class TEXT,
        friendly_class TEXT,

        enemy_speed INTEGER,
        friendly_speed INTEGER,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()
    
    
def insert_scenario(data):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO scenarios (
            date,
            mission_brief,
            intel_summary,
            start_coord,
            destination_coord,
            enemy_last_seen,
            enemy_predicted,
            enemy_class,
            friendly_class,
            enemy_speed,
            friendly_speed
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("date", [None])[0],
        data.get("mission_brief", [None])[0],
        data.get("intel_summary", [None])[0],

        str(data.get("start_coord", [None])[0]),
        str(data.get("destination_coord", [None])[0]),

        str(data.get("enemy_last_seen", [None])[0]),
        str(data.get("enemy_predicted", [None])[0]),

        data.get("enemy_class", [None])[0],
        data.get("friendly_class", [None])[0],

        data.get("enemy_speed", [None])[0],
        data.get("friendly_speed", [None])[0],
    ))

    conn.commit()
    conn.close()
    
    
def get_all_scenarios():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM scenarios ORDER BY id DESC")
    rows = cursor.fetchall()

    conn.close()
    return rows
    
    
def get_scenario_by_id(scenario_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM scenarios WHERE id = ?", (scenario_id,))
    row = cursor.fetchone()

    conn.close()
    return row