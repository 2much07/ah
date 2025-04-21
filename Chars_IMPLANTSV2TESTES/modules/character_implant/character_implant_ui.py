import os
import tkinter as tk
from tkinter import messagebox

# Import local modules using relative imports
try:
    from .character_implant import CharacterImplantApp
except ImportError:
    # Fallback to direct imports for testing
    from character_implant import CharacterImplantApp

class EnhancedCharacterImplantUI(CharacterImplantApp):
    """Enhanced UI for ARK character implant management."""
    
    def __init__(self, root=None, config=None):
        """Initialize the enhanced UI.
        
        Args:
            root (tk.Tk, optional): Tkinter root window
            config (dict, optional): Configuration settings
        """
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
        """Add enhanced UI elements."""
        # Add a button to test the enhanced UI
        test_btn = tk.Button(
            self.root,
            text="Test Enhanced UI",
            command=self.test_enhanced_ui
        )
        test_btn.pack(pady=10)
        
    def test_enhanced_ui(self):
        """Test the enhanced UI."""
        messagebox.showinfo(
            "Enhanced UI Test", 
            "Enhanced UI is working correctly!"
        )
        
    # Override the test_connection method to demonstrate inheritance
    def test_connection(self):
        """Test connection with enhanced messaging."""
        steam_ids = self.data_manager.get_all_steam_ids()
        messagebox.showinfo(
            "Enhanced Connection Test", 
            f"Connection successful! Found {len(steam_ids)} Steam accounts.\n\nRunning in Enhanced UI mode."
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