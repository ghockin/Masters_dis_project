from flask import Blueprint, render_template, request, redirect, url_for, send_file, jsonify
from pdf2image import convert_from_path
import pytesseract
import pdfplumber
from PIL import ImageDraw
import os

from data_organise import populate_data_frame
from database import (
    get_all_scenarios,
    get_scenario_by_id,
    create_mutations,
    has_mutations,
    get_mutation_count,
)
from run_simulation import SimulationState

from config import POPPLER_PATH, SCENARIO_TEMPLATE, OUTPUT_FILE, DEBUG_DIR, UPLOAD_FOLDER, OCR_BOXES

main = Blueprint("main", __name__)
sim = None

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@main.get("/")
def index():
    return render_template("index.html")


@main.get("/download-scenario-template")
def download_scenario_template():
    return send_file(
        SCENARIO_TEMPLATE,
        as_attachment=True,
        download_name="scenario_template.pdf"
    )


@main.post("/upload-scenario")
def upload_pdf():
    file = request.files.get("pdf")
    if not file or not file.filename.lower().endswith(".pdf"):
        return jsonify({"message": "Please upload a valid PDF file", "category": "error"})

    pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(pdf_path)

    return jsonify({"message": f"PDF '{file.filename}' uploaded successfully.", "category": "success"})


@main.post("/extract-ocr")
def extract_ocr():
    file = request.files.get("pdf")
    if not file or not file.filename.lower().endswith(".pdf"):
        return jsonify({"message": "Please upload a valid PDF", "category": "error"})

    pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(pdf_path)

    extracted_text = ""

    try:
        images = convert_from_path(pdf_path, poppler_path=str(POPPLER_PATH))
        for page_num, image in enumerate(images, start=1):
            draw = ImageDraw.Draw(image)
            page_text = {}
            for field, coords in OCR_BOXES.items():
                cropped = image.crop(coords)
                text = pytesseract.image_to_string(cropped).strip()
                page_text[field] = text
                draw.rectangle(coords, outline="green", width=3)
                draw.text((coords[0], coords[1] - 15), field, fill="green")

            image.save(os.path.join(DEBUG_DIR, f"page_{page_num}_debug.png"))

            extracted_text += f"--- Page {page_num} ---\n"
            for field, text in page_text.items():
                extracted_text += f"{field}: {text}\n"
            extracted_text += "\n"

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(extracted_text)

        populate_data_frame(OUTPUT_FILE)
        return jsonify({"message": f"PDF text extracted successfully with OCR! Saved to {OUTPUT_FILE}", "category": "success"})
    except Exception as e:
        return jsonify({"message": f"OCR failed: {e}", "category": "error"})


@main.post("/upload-scenario-pdfplumber")
def extract_pdfplumber():
    file = request.files.get("pdf")
    if not file or not file.filename.lower().endswith(".pdf"):
        return jsonify({"message": "Please upload a valid PDF file", "category": "error"})

    pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(pdf_path)

    extracted_text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""
                extracted_text += f"--- Page {page_num} ---\n{text}\n"

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(extracted_text)

        populate_data_frame(OUTPUT_FILE)
        return jsonify({"message": f"PDF text extracted successfully with pdfplumber! Saved to {OUTPUT_FILE}", "category": "success"})
    except Exception as e:
        return jsonify({"message": f"pdfplumber extraction failed: {e}", "category": "error"})


@main.get("/scenarios")
def scenarios():
    scenarios = get_all_scenarios()
    mutations_exist = has_mutations()
    mutation_count = get_mutation_count()

    return render_template(
        "scenarios.html",
        scenarios=scenarios,
        mutations_exist=mutations_exist,
        mutation_count=mutation_count
    )


@main.post("/create-mutations")
def create_mutations_route():
    if not has_mutations():
        create_mutations()
    return redirect(url_for("main.scenarios"))


@main.get("/view-scenario")
def view_scenario():
    global sim

    scenario_id = request.args.get("scenario_id")
    scenario = get_scenario_by_id(int(scenario_id))

    sim = SimulationState(scenario)

    return render_template("simulation.html", sim=sim)


@main.get("/state")
def state():
    global sim

    if sim is None:
        return {"error": "no active simulation"}

    return {
        "tick": sim.tick_count,
        "enemy": sim.enemy,
        "friendly": sim.friendly,
        "friendly_target": list(sim.friendly_destination),
        "friendly_path": [list(p) for p in sim.friendly_path],
        "finished": sim.finished,
        "destroyed": sim.friendly_destroyed
    }


@main.post("/tick")
def tick():
    global sim

    if sim is None:
        return {"error": "no simulation"}, 400

    sim.tick()

    return {
        "tick": sim.tick_count,
        "enemy": sim.enemy,
        "friendly": sim.friendly,
        "friendly_target": list(sim.friendly_destination),
        "friendly_path": [list(p) for p in sim.friendly_path],
        "finished": sim.finished,
        "destroyed": sim.friendly_destroyed
    }


@main.post("/reset")
def reset():
    global sim

    if sim is None:
        return {"error": "no simulation"}, 400

    sim = SimulationState(sim.scenario)

    return {"ok": True}
    
    
    
@main.get("/db-view")
def db_view():
    scenarios = get_all_scenarios()
    return render_template("view_database_scenarios.html", scenarios=scenarios)