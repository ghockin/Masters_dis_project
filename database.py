import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "scenario.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scenarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        scenario_name TEXT,
        is_mutation INTEGER DEFAULT 0,

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
        friendly_evasion_interval INTEGER DEFAULT 0,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


def insert_scenario(data):
    def first_or_value(value):
        if isinstance(value, list):
            return value[0] if value else None
        return value

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO scenarios (
            scenario_name,
            is_mutation,
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
            friendly_speed,
            friendly_evasion_interval
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        first_or_value(data.get("scenario_name")),
        int(first_or_value(data.get("is_mutation", 0)) or 0),
        first_or_value(data.get("date")),
        first_or_value(data.get("mission_brief")),
        first_or_value(data.get("intel_summary")),

        str(first_or_value(data.get("start_coord"))),
        str(first_or_value(data.get("destination_coord"))),
        str(first_or_value(data.get("enemy_last_seen"))),
        str(first_or_value(data.get("enemy_predicted"))),

        first_or_value(data.get("enemy_class")),
        first_or_value(data.get("friendly_class")),
        int(first_or_value(data.get("enemy_speed"))) if first_or_value(data.get("enemy_speed")) is not None else None,
        int(first_or_value(data.get("friendly_speed"))) if first_or_value(data.get("friendly_speed")) is not None else None,
        int(first_or_value(data.get("friendly_evasion_interval"))) if first_or_value(data.get("friendly_evasion_interval")) is not None else 0,
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


def has_mutations():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM scenarios WHERE is_mutation = 1")
    count = cursor.fetchone()[0]

    conn.close()
    return count > 0


def get_mutation_count():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM scenarios WHERE is_mutation = 1")
    count = cursor.fetchone()[0]

    conn.close()
    return count


def delete_mutations():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM scenarios WHERE is_mutation = 1")
    conn.commit()
    conn.close()


def create_mutations():
    scenarios = get_all_scenarios()
    originals = [row for row in scenarios if row["is_mutation"] == 0]

    created = 0

    for base in originals:
        for donor in originals:

            if base["id"] == donor["id"]:
                continue

            # ✅ Build the mutation name FIRST
            existing_name = (
                f"Mutation | Base {base['id']} | "
                f"Friendly Speed from {donor['id']} | "
                f"Evasion from {donor['id']}"
            )

            # ✅ Skip if already exists
            if any(s["scenario_name"] == existing_name for s in scenarios):
                continue

            # ✅ Create mutation
            mutation = {
                "scenario_name": existing_name,
                "is_mutation": 1,

                "date": base["date"],
                "mission_brief": base["mission_brief"],
                "intel_summary": base["intel_summary"],

                "start_coord": base["start_coord"],
                "destination_coord": base["destination_coord"],

                "enemy_last_seen": base["enemy_last_seen"],
                "enemy_predicted": base["enemy_predicted"],

                "enemy_class": base["enemy_class"],
                "friendly_class": base["friendly_class"],

                # 🔒 enemy stays fixed
                "enemy_speed": base["enemy_speed"],

                # 🔄 ONLY mutate friendly behaviour
                "friendly_speed": donor["friendly_speed"],
                "friendly_evasion_interval": donor["friendly_evasion_interval"],
            }

            # ✅ Insert into DB
            insert_scenario(mutation)

            # ✅ IMPORTANT: update local list so duplicates in SAME RUN are prevented
            scenarios.append({"scenario_name": existing_name})

            created += 1

    return created