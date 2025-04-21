import os
import json
from PIL import Image
import pytesseract

# Set Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# JSON storage file
DATA_FILE = "characters.json"

# Load character data
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return {}

# Save character data
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

# Extract data from implant image
def extract_implant_data(image_path):
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)

    data = {
        "sample_number": None, "vernacular_id": None,
        "gender": None, "survival_quotient": [],
        "chibi_levels": "N/A", "explorer_notes": [],
        "comments": "", "background_image": image_path
    }

    lines = text.split("\n")
    for line in lines:
        line = line.strip()
        if "Sample #:" in line:
            data["sample_number"] = line.split(":")[-1].strip()
        elif "Vernacular ID:" in line:
            data["vernacular_id"] = line.split(":")[-1].strip()
        elif "Gender:" in line:
            data["gender"] = line.split(":")[-1].strip()
        elif "Alpha" in line or "Beta" in line or "Gamma" in line:
            data["survival_quotient"].append(line.strip())
        elif "Chibi-Dino Level-Ups:" in line:
            data["chibi_levels"] = line.strip()
        elif "Explorer Notes" in line or "Tall Tale Explorer Notes" in line:
            data["explorer_notes"].append(line.strip())

    return data

# Check for updates and process implants
def check_for_updates(directory):
    characters = load_data()
    processed_samples = {}

    # Iterate over all folders in the directory (steam accounts)
    for steam_id in os.listdir(directory):
        steam_path = os.path.join(directory, steam_id)
        if os.path.isdir(steam_path):
            if steam_id not in characters:
                characters[steam_id] = []
            
            # Process all image files in the folder
            for filename in os.listdir(steam_path):
                if filename.lower().endswith((".png", ".jpg", ".jpeg")):
                    img_path = os.path.join(steam_path, filename)
                    data = extract_implant_data(img_path)
                    sample_number = data.get("sample_number")

                    if sample_number:
                        if sample_number in processed_samples:
                            data["sample_number"] += "_clone"
                        else:
                            processed_samples[sample_number] = True

                        characters[steam_id].append(data)
                        print(f"Processed: {filename} -> {sample_number}")

    save_data(characters)
    print("Update check complete.")

# Run the check (example usage)
check_for_updates("D:/Chars_IMPLANTS/implants")  # Use full path

