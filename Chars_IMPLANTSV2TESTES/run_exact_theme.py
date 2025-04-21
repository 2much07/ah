import os
import sys
import tkinter as tk

# Add the current directory to sys.path if needed
if os.path.abspath(os.path.dirname(__file__)) not in sys.path:
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    # Create the root window
    root = tk.Tk()
    root.title("ARK Character Implant Manager")
    
    # Try importing the modules
    from modules.character_implant.utils.ocr import ImplantOCR
    from modules.character_implant.utils.data_manager import CharacterDataManager
    from modules.character_implant.character_implant import CharacterImplantApp
    
    # Import the exact match ARK theme
    from modules.character_implant.ark_exact_theme import apply_exact_theme
    
    print("Starting ARK Character Implant Manager with Exact Match UI...")
    
    # Configure the application
    config = {
        'window_width': 1200,
        'window_height': 800,
        'allow_clones': True  # Enable clone support
    }
    
    # Create the application
    app = CharacterImplantApp(root, config)
    
    # Apply the exact match ARK theme
    theme = apply_exact_theme(root, app)
    
    # Add menu bar
    menubar = tk.Menu(root)
    
    # File menu
    file_menu = tk.Menu(menubar, tearoff=0)
    file_menu.add_command(label="Select Implant Image", command=app.open_image)
    file_menu.add_command(label="Import from CSV", command=app.import_from_csv)
    file_menu.add_command(label="Export to CSV", command=app.export_to_csv)
    file_menu.add_command(label="Export CSV Template", command=app.export_csv_template)
    file_menu.add_separator()
    file_menu.add_command(label="Backup Data", command=app.backup_data)
    file_menu.add_command(label="Restore Data", command=app.restore_data)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=root.quit)
    menubar.add_cascade(label="File", menu=file_menu)
    
    # Edit menu
    edit_menu = tk.Menu(menubar, tearoff=0)
    edit_menu.add_command(label="Delete Character", command=app.delete_character)
    edit_menu.add_command(label="Clone Character", command=app.clone_character)
    edit_menu.add_command(label="Change Background", command=app.change_background)
    menubar.add_cascade(label="Edit", menu=edit_menu)
    
    # Tools menu
    tools_menu = tk.Menu(menubar, tearoff=0)
    tools_menu.add_command(label="Compare Selected", command=app.compare_characters)
    tools_menu.add_command(label="Batch Export Selected", command=app.batch_export_characters)
    tools_menu.add_command(label="Show Data Location", command=app.show_data_location)
    menubar.add_cascade(label="Tools", menu=tools_menu)
    
    # Help menu
    help_menu = tk.Menu(menubar, tearoff=0)
    help_menu.add_command(label="About", command=lambda: tk.messagebox.showinfo(
        "About", "ARK Character Implant Manager\n\nA tool for managing ARK character implants."
    ))
    menubar.add_cascade(label="Help", menu=help_menu)
    
    root.config(menu=menubar)
    
    # Run the application
    app.run()
    
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please make sure all required files are in the correct locations.")
    input("Press Enter to exit...")
except Exception as e:
    print(f"An error occurred: {e}")
    import traceback
    traceback.print_exc()
    input("Press Enter to exit...")

  
