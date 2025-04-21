import os
import sys
import tkinter as tk

# Add the current directory to sys.path if needed
if os.path.abspath(os.path.dirname(__file__)) not in sys.path:
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    # Import modules
    from modules.character_implant.character_implant_ui import EnhancedCharacterImplantUI
    
    print("Starting ARK Character Implant Manager...")
    
    # Create and run the application
    root = tk.Tk()
    app = EnhancedCharacterImplantUI(root)
    app.run()
    
except Exception as e:
    print(f"An error occurred: {e}")
    import traceback
    traceback.print_exc()
    input("Press Enter to exit...")