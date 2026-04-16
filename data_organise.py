import re
from database import insert_scenario

def populate_data_frame(file_path):
    with open(file_path, "r") as file:
        text = file.read()

    # -----------------------
    # DATE
    # -----------------------
    date_match = re.search(r"date:\s*(.*)", text)
    date = date_match.group(1).strip() if date_match else None

    # -----------------------
    # MISSION BRIEF SECTION
    # -----------------------
    mission_section = re.search(
        r"mission_brief:\s*(.*?)intel_summary:",
        text,
        re.DOTALL | re.IGNORECASE
    )
    mission_text = mission_section.group(1) if mission_section else ""

    mission_brief = mission_text.replace("\n", " ").strip()

    # -----------------------
    # INTEL SUMMARY SECTION
    # -----------------------
    intel_section = re.search(
        r"intel_summary:\s*(.*?)operative:",
        text,
        re.DOTALL | re.IGNORECASE
    )
    intel_text = intel_section.group(1) if intel_section else ""
    intel_text = intel_text.replace("\n", " ").strip()
    # -----------------------
    # COORDINATES (MISSION)
    # -----------------------
    mission_coords = re.findall(r"\((\d+,\d+)\)", mission_text)

    start_coord = tuple(map(int, mission_coords[0].split(','))) if len(mission_coords) > 0 else None
    destination_coord = tuple(map(int, mission_coords[1].split(','))) if len(mission_coords) > 1 else None

    # -----------------------
    # COORDINATES (ENEMY)
    # -----------------------
    enemy_coords_match = re.search(
        r"Last sighted co-ordinates\s*\((\d+,\d+)\).*?co-ordinates\s*\((\d+,\d+)\)",
        intel_text,
        re.DOTALL | re.IGNORECASE
    )

    enemy_last_seen = None
    enemy_predicted = None

    if enemy_coords_match:
        enemy_last_seen = tuple(map(int, enemy_coords_match.group(1).split(',')))
        enemy_predicted = tuple(map(int, enemy_coords_match.group(2).split(',')))

    # -----------------------
    # CLASSES
    # -----------------------
    enemy_class_match = re.search(r"Class:\s*([A-Za-z0-9\s]+),", text)
    enemy_class = enemy_class_match.group(1).strip() if enemy_class_match else None

    friendly_class_match = re.search(
        r"operative:.*?Class:\s*([A-Za-z0-9\s\.]+)",
        text,
        re.DOTALL | re.IGNORECASE
    )
    friendly_class = friendly_class_match.group(1).strip().rstrip(".") if friendly_class_match else None

    # -----------------------
    # SPEEDS
    # -----------------------
    friendly_speed_match = re.search(
        r"speed\s*of\s*(\d+)\s*knots",
        mission_text,
        re.IGNORECASE
    )
    friendly_speed = int(friendly_speed_match.group(1)) if friendly_speed_match else None

    enemy_speed_match = re.search(
        r"speed\s*of\s*(\d+)\s*knots",
        intel_text,
        re.IGNORECASE
    )
    enemy_speed = int(enemy_speed_match.group(1)) if enemy_speed_match else None

    # -----------------------
    # DATA DICTIONARY
    # -----------------------
    data = {
        "date": [date],
        "mission_brief": [mission_brief],
        "intel_summary": [intel_text],

        "start_coord": [start_coord],
        "destination_coord": [destination_coord],

        "enemy_last_seen": [enemy_last_seen],
        "enemy_predicted": [enemy_predicted],

        "enemy_class": [enemy_class],
        "friendly_class": [friendly_class],

        "enemy_speed": [enemy_speed],
        "friendly_speed": [friendly_speed],
    }

    # -----------------------
    # DEBUG PRINT (clean)
    # -----------------------
    print("\n--- PARSED DATA ---")
    for key, value in data.items():
        print(f"{key:<20}: {value[0]}")
    print("--- END ---\n")

    # -----------------------
    # DATABASE
    # -----------------------
    insert_scenario(data)