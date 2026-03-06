from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, jsonify
from pdf2image import convert_from_path
import pytesseract
import pdfplumber
from PIL import ImageDraw
import os

# import paths from config.py
from config import POPPLER_PATH, SCENARIO_TEMPLATE, TESSERACT_PATH, OUTPUT_FILE, DEBUG_DIR, UPLOAD_FOLDER, OCR_BOXES

main = Blueprint("main", __name__)


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
                draw.text((coords[0], coords[1]-15), field, fill="green")
            image.save(os.path.join(DEBUG_DIR, f"page_{page_num}_debug.png"))

            extracted_text += f"--- Page {page_num} ---\n"
            for field, text in page_text.items():
                extracted_text += f"{field}: {text}\n"
            extracted_text += "\n"

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(extracted_text)

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

        # ✅ Return JSON with success category
        return jsonify({"message": f"PDF text extracted successfully with pdfplumber! Saved to {OUTPUT_FILE}", "category": "success"})

    except Exception as e:
        return jsonify({"message": f"pdfplumber extraction failed: {e}", "category": "error"})

    
@main.post("/create-scenario")
def create_scenario():
    # For demo, generate a 10x10 grid of numbers 1-100
    grid_numbers = [i for i in range(1, 101)]
    
    # Split into rows of 10
    grid_rows = [grid_numbers[i:i+10] for i in range(0, 100, 10)]
    
    # Render new template
    return render_template("scenario.html", grid_rows=grid_rows)