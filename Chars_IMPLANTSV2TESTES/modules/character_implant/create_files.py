"""
Script to create all necessary files for the ARK Character Implant Manager.
Save this file anywhere and run it to create the required files.
"""

import os

# Base directory
BASE_DIR = r"D:\Chars_IMPLANTSV2"

# File definitions
files = {
    # Main __init__.py
    os.path.join(BASE_DIR, "modules", "__init__.py"): 
    """# This file is intentionally left empty
""",

    # Character implant module __init__.py
    os.path.join(BASE_DIR, "modules", "character_implant", "__init__.py"): 
    """ARK Character Implant Module

This module provides functionality for managing ARK: Survival Evolved character implants.
"""

# These imports will be used after the other files are created
# from .character_implant import CharacterImplantApp
# from .character_implant_ui import EnhancedCharacterImplantUI
# from .utils.ocr import ImplantOCR
# from .utils.data_manager import CharacterDataManager
""",

    # Utils directory __init__.py
    os.path.join(BASE_DIR, "modules", "character_implant", "utils", "__init__.py"): 
    """# This file is intentionally left empty
""",

    # OCR utility
    os.path.join(BASE_DIR, "modules", "character_implant", "utils", "ocr.py"): 
    """import os
import pytesseract
from PIL import Image
from datetime import datetime

class ImplantOCR:
    \"\"\"Handles Optical Character Recognition for ARK implant images.\"\"\"
    
    def __init__(self, tesseract_path=None):
        \"\"\"Initialize the OCR module.
        
        Args:
            tesseract_path (str, optional): Path to Tesseract executable
        \"\"\"
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        elif os.name == 'nt':  # Default path for Windows
            pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
    
    def extract_implant_data(self, image_path):
        \"\"\"Extract character data from an implant image.
        
        Args:
            image_path (str): Path to the implant image
            
        Returns:
            dict: Extracted character data
        \"\"\"
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

        lines = text.split("\\n")
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
""",

    # Data Manager
    os.path.join(BASE_DIR, "modules", "character_implant", "utils", "data_manager.py"): 
    """import os
import json
import shutil
from datetime import datetime

class CharacterDataManager:
    \"\"\"Manages character implant data storage and retrieval.\"\"\"
    
    def __init__(self, base_directory=None, data_file=None):
        \"\"\"Initialize the data manager.
        
        Args:
            base_directory (str, optional): Base directory for character data
            data_file (str, optional): JSON file path for data storage
        \"\"\"
        # Set default paths if not provided
        self.base_directory = base_directory or os.path.join(os.path.expanduser("~"), "ARK_AssistantV2", "data", "character_implants")
        self.data_file = data_file or os.path.join(self.base_directory, "characters.json")
        
        # Ensure directories exist
        os.makedirs(self.base_directory, exist_ok=True)
        
        # Initialize character data
        self.characters = self.load_data()
    
    def load_data(self, reset=False):
        \"\"\"Load character data from JSON file.
        
        Args:
            reset (bool): Whether to reset the data file
            
        Returns:
            dict: Character data
        \"\"\"
        if reset and os.path.exists(self.data_file):
            os.remove(self.data_file)
        
        if not os.path.exists(self.data_file):
            empty_data = {}
            self.save_data(empty_data)
            return empty_data
        
        try:
            with open(self.data_file, "r", encoding="utf-8") as file:
                return json.load(file)
        except json.JSONDecodeError:
            return {}
    
    def save_data(self, data=None):
        \"\"\"Save character data to JSON file.
        
        Args:
            data (dict, optional): Data to save, defaults to self.characters
        \"\"\"
        with open(self.data_file, "w", encoding="utf-8") as file:
            json.dump(data or self.characters, file, indent=4)
            
    # Simple method for testing
    def get_all_steam_ids(self):
        \"\"\"Get all Steam account IDs.
        
        Returns:
            list: List of Steam account IDs
        \"\"\"
        return list(self.characters.keys())
""",

    # Main application file
    os.path.join(BASE_DIR, "modules", "character_implant", "character_implant.py"): 
    """import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk

# Import local modules using relative imports
try:
    from .utils.ocr import ImplantOCR
    from .utils.data_manager import CharacterDataManager
except ImportError:
    # Fallback to direct imports for testing
    from utils.ocr import ImplantOCR
    from utils.data_manager import CharacterDataManager

class CharacterImplantApp:
    \"\"\"Main application for ARK character implant management.\"\"\"
    
    def __init__(self, root=None, config=None):
        \"\"\"Initialize the application.
        
        Args:
            root (tk.Tk, optional): Tkinter root window
            config (dict, optional): Configuration settings
        \"\"\"
        # Default configuration
        self.config = {
            'base_directory': os.path.join(os.path.expanduser("~"), "ARK_AssistantV2", "data", "character_implants"),
            'tesseract_path': r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe",
            'font_family': "Arial",
            'font_size': 12,
            'window_width': 800,
            'window_height': 600,
            'theme': "dark"
        }
        
        # Update with provided config
        if config:
            self.config.update(config)
            
        # Initialize OCR handler
        self.ocr = ImplantOCR(self.config['tesseract_path'])
        
        # Initialize data manager
        self.data_manager = CharacterDataManager(self.config['base_directory'])
        
        # Load character data
        self.characters = self.data_manager.characters
        
        # Setup UI
        self.root = root or tk.Tk()
        self.setup_ui()
        
    def setup_ui(self):
        \"\"\"Setup the user interface.\"\"\"
        # Configure root window
        self.root.title("ARK Character Implant Manager")
        self.root.geometry(f"{self.config['window_width']}x{self.config['window_height']}")
        self.root.configure(bg="black")
        
        # Create label
        label = tk.Label(
            self.root, 
            text="Character Implant Manager", 
            fg="white", 
            bg="black",
            font=(self.config['font_family'], 16)
        )
        label.pack(pady=20)
        
        # Create a button
        btn = tk.Button(
            self.root,
            text="Test Connection",
            command=self.test_connection
        )
        btn.pack(pady=10)
        
    def test_connection(self):
        \"\"\"Test connection to data manager.\"\"\"
        steam_ids = self.data_manager.get_all_steam_ids()
        messagebox.showinfo(
            "Connection Test", 
            f"Connection successful! Found {len(steam_ids)} Steam accounts."
        )
        
    def run(self):
        \"\"\"Run the application main loop.\"\"\"
        self.root.mainloop()


# Test function for standalone execution
def test():
    print("Testing CharacterImplantApp...")
    app = CharacterImplantApp()
    print("OCR and Data Manager initialized successfully.")
    return app

# Entry point for standalone execution
if __name__ == "__main__":
    app = test()
    app.run()
""",

    # UI enhancement file
    os.path.join(BASE_DIR, "modules", "character_implant", "character_implant_ui.py"): 
    """import os
import tkinter as tk
from tkinter import messagebox

# Import local modules using relative imports
try:
    from .character_implant import CharacterImplantApp
except ImportError:
    # Fallback to direct imports for testing
    from character_implant import CharacterImplantApp

class EnhancedCharacterImplantUI(CharacterImplantApp):
    \"\"\"Enhanced UI for ARK character implant management.\"\"\"
    
    def __init__(self, root=None, config=None):
        \"\"\"Initialize the enhanced UI.
        
        Args:
            root (tk.Tk, optional): Tkinter root window
            config (dict, optional): Configuration settings
        \"\"\"
        # Default enhanced configuration
        enhanced_config = {
            'window_width': 900,
            'window_height': 700,
            'theme': "dark"
        }
        
        # Update with provided config
        if config:
            enhanced_config.update(config)
            
        # Initialize base class
        super().__init__(root, enhanced_config)
        
        # Add additional UI elements
        self.add_enhanced_ui()
        
    def add_enhanced_ui(self):
        \"\"\"Add enhanced UI elements.\"\"\"
        # Add a button to test the enhanced UI
        test_btn = tk.Button(
            self.root,
            text="Test Enhanced UI",
            command=self.test_enhanced_ui
        )
        test_btn.pack(pady=10)
        
    def test_enhanced_ui(self):
        \"\"\"Test the enhanced UI.\"\"\"
        messagebox.showinfo(
            "Enhanced UI Test", 
            "Enhanced UI is working correctly!"
        )
        
    # Override the test_connection method to demonstrate inheritance
    def test_connection(self):
        \"\"\"Test connection with enhanced messaging.\"\"\"
        steam_ids = self.data_manager.get_all_steam_ids()
        messagebox.showinfo(
            "Enhanced Connection Test", 
            f"Connection successful! Found {len(steam_ids)} Steam accounts.\\n\\nRunning in Enhanced UI mode."
        )


# Test function for standalone execution
def test():
    print("Testing EnhancedCharacterImplantUI...")
    app = EnhancedCharacterImplantUI()
    print("Enhanced UI initialized successfully.")
    return app

# Entry point for standalone execution
if __name__ == "__main__":
    app = test()
    app.run()
""",

    # Simple runner script
    os.path.join(BASE_DIR, "run_char_implant.py"): 
    """import os
import sys
import tkinter as tk

# Add the current directory to sys.path if needed
if os.path.abspath(os.path.dirname(__file__)) not in sys.path:
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    from modules.character_implant.character_implant_ui import EnhancedCharacterImplantUI
    
    # Create and run the application
    root = tk.Tk()
    app = EnhancedCharacterImplantUI(root)
    app.run()
    
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please make sure all required files are in the correct locations.")
    input("Press Enter to exit...")
except Exception as e:
    print(f"An error occurred: {e}")
    input("Press Enter to exit...")
"""
}

def create_files():
    """Create all necessary files."""
    for file_path, content in files.items():
        try:
            # Create directory if it doesn't exist
            directory = os.path.dirname(file_path)
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"Created directory: {directory}")
            
            # Write file
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"Created file: {file_path}")
        except Exception as e:
            print(f"Error creating {file_path}: {e}")

if __name__ == "__main__":
    create_files()
    print("\nAll files created successfully!")
    print(f"\nTo run the application, go to {BASE_DIR} and run:")
    print("python run_char_implant.py")
    input("\nPress Enter to continue...")
