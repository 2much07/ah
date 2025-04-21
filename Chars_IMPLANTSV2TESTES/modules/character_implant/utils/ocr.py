import os
import pytesseract
from PIL import Image
from datetime import datetime

class ImplantOCR:
    """Handles Optical Character Recognition for ARK implant images."""
    
    def __init__(self, tesseract_path=None):
        """Initialize the OCR module.
        
        Args:
            tesseract_path (str, optional): Path to Tesseract executable
        """
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        elif os.name == 'nt':  # Default path for Windows
            pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    
    def extract_implant_data(self, image_path):
        """Extract character data from an implant image.
        
        Args:
            image_path (str): Path to the implant image
            
        Returns:
            dict: Extracted character data
        """
        img = Image.open(image_path)
        try:
            text = pytesseract.image_to_string(img)
        except Exception as e:
            print(f"OCR error: {e}")
            text = ""

        data = {
            "sample_number": None, 
            "vernacular_id": None,
            "gender": None, 
            "survival_quotient": [],
            "chibi_levels": "N/A", 
            "explorer_notes": [],
            "comments": "", 
            "background_image": image_path,
            "date_added": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        lines = text.split("\n")
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if "Sample #:" in line:
                data["sample_number"] = line.split(":")[-1].strip()
            elif "Vernacular ID:" in line:
                data["vernacular_id"] = line.split(":")[-1].strip()
            elif "Gender:" in line:
                data["gender"] = line.split(":")[-1].strip()
            elif any(boss in line for boss in ["Alpha", "Beta", "Gamma"]):
                data["survival_quotient"].append(line)
            elif "Chibi-Dino Level-Ups:" in line:
                data["chibi_levels"] = line
            elif "Explorer Notes" in line or "Tall Tale Explorer Notes" in line:
                data["explorer_notes"].append(line)

        return data