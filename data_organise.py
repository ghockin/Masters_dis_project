import re
from database import insert_scenario


def populate_data_frame(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()

    # normalize line endings
    text = text.replace("\r\n", "\n")

    # -----------------------
    # DATE
    # -----------------------
    date_match = re.search(r"date:\s*(.*)", text, re.IGNORECASE)
    date = date_match.group(1).strip() if date_match else None

    # -----------------------
    # MISSION BRIEF SECTION
    # -----------------------
    mission_section = re.search(
        r"Mission Brief\s*(.*?)\s*Intel Summary",
        text,
        re.DOTALL | re.IGNORECASE
    )
    mission_text = mission_section.group(1).strip() if mission_section else ""
    mission_brief = re.sub(r"\s+", " ", mission_text).strip()

    # -----------------------
    # INTEL SUMMARY SECTION
    # -----------------------
    intel_section = re.search(
        r"Intel Summary\s*(.*?)\s*Operative",
        text,
        re.DOTALL | re.IGNORECASE
    )
    intel_text = intel_section.group(1).strip() if intel_section else ""
    intel_summary = re.sub(r"\s+", " ", intel_text).strip()

    # -----------------------
    # COORDINATES (MISSION)
    # -----------------------
    mission_coords = re.findall(r"\((\d+\s*,\s*\d+)\)", mission_text)

    start_coord = tuple(map(int, mission_coords[0].split(","))) if len(mission_coords) > 0 else None
    destination_coord = tuple(map(int, mission_coords[1].split(","))) if len(mission_coords) > 1 else None

    # -----------------------
    # COORDINATES (ENEMY)
    # -----------------------
    enemy_coords = re.findall(r"\((\d+\s*,\s*\d+)\)", intel_text)

    enemy_last_seen = tuple(map(int, enemy_coords[0].split(","))) if len(enemy_coords) > 0 else None
    enemy_predicted = tuple(map(int, enemy_coords[1].split(","))) if len(enemy_coords) > 1 else None

    # -----------------------
    # CLASSES
    # -----------------------
    enemy_class_match = re.search(
        r"Intel Summary.*?Class:\s*([A-Za-z0-9\s\-]+?)[\.,\n]",
        text,
        re.DOTALL | re.IGNORECASE
    )
    enemy_class = enemy_class_match.group(1).strip() if enemy_class_match else None

    friendly_class_match = re.search(
        r"Operative\s*Class:\s*([A-Za-z0-9\s\.-]+)",
        text,
        re.DOTALL | re.IGNORECASE
    )
    friendly_class = friendly_class_match.group(1).strip().rstrip(".") if friendly_class_match else None

    # -----------------------
    # SPEEDS
    # -----------------------
    friendly_speed_match = re.search(
        r"Mission Brief.*?speed\s*of\s*(\d+)\s*knots",
        text,
        re.DOTALL | re.IGNORECASE
    )
    friendly_speed = int(friendly_speed_match.group(1)) if friendly_speed_match else None

    enemy_speed_match = re.search(
        r"Intel Summary.*?speed\s*of\s*(\d+)\s*knots",
        text,
        re.DOTALL | re.IGNORECASE
    )
    enemy_speed = int(enemy_speed_match.group(1)) if enemy_speed_match else None

    # -----------------------
    # EVASION INTERVAL
    # -----------------------
    evasion_match = re.search(
        r"evasion[_\s]*interval\s*[:=]?\s*(\d+)",
        text,
        re.IGNORECASE
    )
    friendly_evasion_interval = int(evasion_match.group(1)) if evasion_match else 0

    # -----------------------
    # DATA DICTIONARY
    # -----------------------
    data = {
        "date": [date],
        "mission_brief": [mission_brief],
        "intel_summary": [intel_summary],

        "start_coord": [start_coord],
        "destination_coord": [destination_coord],

        "enemy_last_seen": [enemy_last_seen],
        "enemy_predicted": [enemy_predicted],

        "enemy_class": [enemy_class],
        "friendly_class": [friendly_class],

        "enemy_speed": [enemy_speed],
        "friendly_speed": [friendly_speed],
        "friendly_evasion_interval": [friendly_evasion_interval],
    }

    # -----------------------
    # DEBUG PRINT
    # -----------------------
    print("\n--- PARSED DATA ---")
    for key, value in data.items():
        print(f"{key:<28}: {value[0]}")
    print("--- END ---\n")

    # -----------------------
    # DATABASE
    # -----------------------
    insert_scenario(data)