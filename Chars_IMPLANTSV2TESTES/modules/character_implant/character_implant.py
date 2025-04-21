import os
import sys
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk

# Import local modules
try:
    from .utils.ocr import ImplantOCR
    from .utils.data_manager import CharacterDataManager
except ImportError:
    # Fallback to direct imports for testing
    from utils.ocr import ImplantOCR
    from utils.data_manager import CharacterDataManager

class CharacterImplantApp:
    """Main application for ARK character implant management."""
    
    def __init__(self, root=None, config=None):
        """Initialize the application."""
        # Default configuration
        self.config = {
            'base_directory': os.path.join(os.path.expanduser("~"), "ARK_AssistantV2", "data", "character_implants"),
            'tesseract_path': r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            'font_family': "Arial",
            'font_size': 12,
            'window_width': 1150,
            'window_height': 800,
            'display_frame_height': 500,
            'theme': "dark",
            'allow_clones': True
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
        
        # Create character lookup dictionary
        self.char_lookup = {}
        
        # Setup UI
        self.root = root or tk.Tk()
        
        # IMPORTANT: Initialize StringVar for Steam account selection BEFORE using it
        self.selected_steam = tk.StringVar(self.root)
        
        # Now set up the UI components
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface."""
        # Configure root window
        self.root.title("ARK Character Implant Manager")
        self.root.geometry(f"{self.config['window_width']}x{self.config['window_height']}")
        self.root.configure(bg="black")
        self.root.option_add("*Font", (self.config['font_family'], self.config['font_size']))
        
        # Create main frames
        self.create_control_frame()
        self.create_display_frame()
        self.create_character_list_frame()
        
        # Add search panel
        self.add_search_panel()
        
        # Create buttons
        self.create_action_buttons()
        
        # Update Steam account dropdown
        self.update_steam_dropdown()
        
        # Scan for implants
        self.scan_and_update_implants()
        
    def create_control_frame(self):
        """Create the control frame with Steam account management."""
        self.control_frame = tk.Frame(self.root, bg="black")
        self.control_frame.pack(anchor="nw", padx=10, pady=10)
        
        # Steam account label
        tk.Label(self.control_frame, text="Steam Account:", fg="white", bg="black").pack(side="left")
        
        # Steam account entry
        self.steam_entry = tk.Entry(self.control_frame)
        self.steam_entry.pack(side="left", padx=5)
        
        # Add Steam account button
        tk.Button(
            self.control_frame, 
            text="Add Steam Account", 
            command=self.add_steam_account
        ).pack(side="left", padx=5)
        
        # Steam account dropdown
        self.steam_dropdown = ttk.Combobox(
            self.control_frame, 
            textvariable=self.selected_steam, 
            state="readonly"
        )
        self.steam_dropdown.pack(side="left", padx=5)
        self.steam_dropdown.bind("<<ComboboxSelected>>", self.update_character_list)
        
    def create_display_frame(self):
        """Create the display frame for character details."""
        self.display_frame = tk.Frame(
            self.root, 
            bg="black", 
            height=self.config['display_frame_height']
        )
        self.display_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    def add_search_panel(self):
        """Add a search panel to the application."""
        search_frame = tk.Frame(self.root, bg="black")
        search_frame.pack(fill="x", padx=10, pady=5)
        
        # Search label
        tk.Label(search_frame, text="Search:", fg="white", bg="black").pack(side="left")
        
        # Search entry
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.filter_characters)
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side="left", padx=5)
        
        # Filter options
        filter_frame = tk.Frame(search_frame, bg="black")
        filter_frame.pack(side="left", padx=10)
        
        # Filter checkboxes
        self.filter_name = tk.BooleanVar(value=True)
        self.filter_sample = tk.BooleanVar(value=True)
        self.filter_gender = tk.BooleanVar(value=False)
        
        tk.Checkbutton(filter_frame, text="Name", variable=self.filter_name, 
                      bg="black", fg="white", selectcolor="black", 
                      command=self.filter_characters).pack(side="left")
        
        tk.Checkbutton(filter_frame, text="Sample #", variable=self.filter_sample,
                      bg="black", fg="white", selectcolor="black",
                      command=self.filter_characters).pack(side="left")
        
        tk.Checkbutton(filter_frame, text="Gender", variable=self.filter_gender,
                      bg="black", fg="white", selectcolor="black",
                      command=self.filter_characters).pack(side="left")
        
        # Clear button
        tk.Button(search_frame, text="Clear", command=self.clear_search).pack(side="right")
        
    def create_character_list_frame(self):
        """Create the character list frame."""
        self.list_frame = tk.Frame(self.root, bg="black")
        self.list_frame.pack(fill="x", padx=10, pady=5)
        
        # Character list label
        tk.Label(
            self.list_frame, 
            text="Character List:", 
            fg="white", 
            bg="black"
        ).pack(anchor="w")
        
        # Character listbox with multi-select enabled
        self.char_listbox = tk.Listbox(
            self.list_frame, 
            bg="#333333", 
            fg="white", 
            width=90, 
            height=8,
            selectbackground="#555555",
            selectforeground="white",
            selectmode=tk.EXTENDED  # Allow multiple selections
        )
        self.char_listbox.pack(fill="x")
        self.char_listbox.bind("<<ListboxSelect>>", self.load_selected_character)
        
    def create_action_buttons(self):
        """Create action buttons."""
        self.button_frame = tk.Frame(self.root, bg="black")
        self.button_frame.pack(fill="x", padx=10, pady=10)
        
        # Select implant button
        tk.Button(
            self.button_frame,
            text="Select Implant Image",
            bg="#444444",
            fg="white",
            command=self.open_image
        ).pack(side="left", padx=5)
        
        # Delete character button
        tk.Button(
            self.button_frame,
            text="Delete Character",
            bg="#993333",
            fg="white",
            command=self.delete_character
        ).pack(side="left", padx=5)
        
        # Change background button
        tk.Button(
            self.button_frame,
            text="Change Background",
            bg="#444444",
            fg="white",
            command=self.change_background
        ).pack(side="left", padx=5)
        
        # Export to CSV button
        tk.Button(
            self.button_frame,
            text="Export to CSV",
            bg="#444444",
            fg="white",
            command=self.export_to_csv
        ).pack(side="left", padx=5)
        
        # Import from CSV button
        tk.Button(
            self.button_frame,
            text="Import from CSV",
            bg="#444444",
            fg="white",
            command=self.import_from_csv
        ).pack(side="left", padx=5)
        
        # Add a clone button
        tk.Button(
            self.button_frame,
            text="Clone Character",
            bg="#444444",
            fg="white",
            command=self.clone_character
        ).pack(side="left", padx=5)
        
        # Compare button for selected characters
        tk.Button(
            self.button_frame,
            text="Compare Selected",
            bg="#444444",
            fg="white",
            command=self.compare_characters
        ).pack(side="left", padx=5)
        
        # Show data location button
        tk.Button(
            self.button_frame,
            text="Show Data Location",
            bg="#444444",
            fg="white",
            command=self.show_data_location
        ).pack(side="left", padx=5)
        
    def update_steam_dropdown(self):
        """Update the Steam account dropdown menu."""
        steam_ids = self.data_manager.get_all_steam_ids()
        self.steam_dropdown["values"] = steam_ids
        
        if steam_ids:
            self.selected_steam.set(steam_ids[0])
            self.update_character_list()
        else:
            self.selected_steam.set("")
            
    def filter_characters(self, *args):
        """Filter characters based on search criteria."""
        search_text = self.search_var.get().lower()
        
        if not search_text:
            # If search is empty, just update without filtering
            self.update_character_list()
            return
        
        # Get current Steam account
        steam_id = self.selected_steam.get()
        if not steam_id or steam_id not in self.characters:
            return
            
        # Clear listbox
        self.char_listbox.delete(0, tk.END)
        self.char_lookup = {}
        
        # Filter characters
        for i, char in enumerate(self.characters[steam_id]):
            match = False
            
            # Check name
            if self.filter_name.get() and char.get("vernacular_id", "").lower().find(search_text) != -1:
                match = True
                
            # Check sample number
            if self.filter_sample.get() and str(char.get("sample_number", "")).find(search_text) != -1:
                match = True
                
            # Check gender
            if self.filter_gender.get() and char.get("gender", "").lower().find(search_text) != -1:
                match = True
            
            if match:
                # Create display text
                if char.get("background_image"):
                    file_name = os.path.basename(char.get("background_image"))
                else:
                    file_name = "Unknown"
                    
                vernacular_id = char.get("vernacular_id", "N/A")
                sample_number = char.get("sample_number", "N/A")
                gender = char.get("gender", "N/A")
                
                # Add clone indicator if this is a clone
                clone_indicator = " (Clone)" if char.get("is_clone") else ""
                
                display_text = f"{i+1}. {file_name} - {vernacular_id} (Sample #{sample_number}, {gender}){clone_indicator}"
                
                # Store in lookup dictionary
                self.char_lookup[display_text] = (steam_id, i)
                
                # Add to listbox
                self.char_listbox.insert(tk.END, display_text)

    def clear_search(self):
        """Clear search field and filters."""
        self.search_var.set("")
        self.update_character_list()
            
    def update_character_list(self, event=None):
        """Update the character list based on the selected Steam account."""
        self.char_listbox.delete(0, tk.END)  # Clear listbox
        self.char_lookup = {}  # Reset character lookup
        
        steam_id = self.selected_steam.get()
        if not steam_id or steam_id not in self.characters:
            return
            
        for i, char in enumerate(self.characters[steam_id]):
            # Extract file name from background_image path if available
            if char.get("background_image"):
                file_name = os.path.basename(char.get("background_image"))
            else:
                file_name = "Unknown"
                
            # Create display text
            vernacular_id = char.get("vernacular_id", "N/A")
            sample_number = char.get("sample_number", "N/A")
            gender = char.get("gender", "N/A")
            
            # Add clone indicator if this is a clone
            clone_indicator = " (Clone)" if char.get("is_clone") else ""
            
            display_text = f"{i+1}. {file_name} - {vernacular_id} (Sample #{sample_number}, {gender}){clone_indicator}"
            
            # Store in lookup dictionary
            self.char_lookup[display_text] = (steam_id, i)
            
            # Add to listbox
            self.char_listbox.insert(tk.END, display_text)
            
    def load_selected_character(self, event):
        """Load and display the selected character."""
        selected_idx = self.char_listbox.curselection()
        if not selected_idx:
            return
            
        # Use the first selected character for display
        selected_text = self.char_listbox.get(selected_idx[0])
        if selected_text not in self.char_lookup:
            return
            
        steam_id, char_idx = self.char_lookup[selected_text]
        char_data = self.characters[steam_id][char_idx]
        
        # Update display
        self.update_display(char_data)
        
    def update_display(self, data):
        """Update the display with character data."""
        # Clear previous widgets
        for widget in self.display_frame.winfo_children():
            widget.destroy()
            
        # Create scrollable canvas for display
        canvas = tk.Canvas(
            self.display_frame, 
            bg="black",
            highlightthickness=0
        )
        scrollbar = ttk.Scrollbar(
            self.display_frame, 
            orient="vertical", 
            command=canvas.yview
        )
        
        scrollable_frame = tk.Frame(canvas, bg="black")
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Set background image if available
        bg_path = data.get("background_image")
        if bg_path and os.path.exists(bg_path):
            try:
                img = Image.open(bg_path)
                img = img.resize((600, 400), Image.LANCZOS)
                img_photo = ImageTk.PhotoImage(img)
                
                img_label = tk.Label(scrollable_frame, image=img_photo, bg="black")
                img_label.image = img_photo
                img_label.pack(pady=10)
            except Exception as e:
                print(f"Error loading image: {e}")
                
        # Character information
        info_frame = tk.Frame(scrollable_frame, bg="black", padx=10, pady=10)
        info_frame.pack(fill="x")
        
        # Basic information
        tk.Label(
            info_frame, 
            text=f"Sample Number: {data.get('sample_number', 'N/A')}", 
            fg="white", 
            bg="black",
            font=(self.config['font_family'], self.config['font_size']+2, "bold")
        ).pack(anchor="w")
        
        tk.Label(
            info_frame, 
            text=f"Vernacular ID: {data.get('vernacular_id', 'N/A')}", 
            fg="lightblue", 
            bg="black",
            font=(self.config['font_family'], self.config['font_size']+2)
        ).pack(anchor="w")
        
        tk.Label(
            info_frame, 
            text=f"Gender: {data.get('gender', 'N/A')}", 
            fg="pink", 
            bg="black"
        ).pack(anchor="w")
        
        tk.Label(
            info_frame, 
            text=f"Date Added: {data.get('date_added', 'N/A')}", 
            fg="gray", 
            bg="black"
        ).pack(anchor="w")
        
        # Display clone information if this is a clone
        if data.get("is_clone"):
            clone_frame = tk.Frame(info_frame, bg="#333333", padx=5, pady=5)
            clone_frame.pack(fill="x", pady=5)
            
            tk.Label(
                clone_frame, 
                text=f"CLONE CHARACTER (Index: {data.get('clone_index', 0)})", 
                fg="yellow", 
                bg="#333333",
                font=(self.config['font_family'], self.config['font_size'], "bold")
            ).pack(anchor="w")
            
        # Boss kills
        if data.get("survival_quotient"):
            tk.Label(
                info_frame, 
                text="Boss Kills:", 
                fg="yellow", 
                bg="black",
                font=(self.config['font_family'], self.config['font_size']+1, "bold")
            ).pack(anchor="w", pady=(10, 5))
            
            for boss in data["survival_quotient"]:
                tk.Label(
                    info_frame, 
                    text=f"• {boss}", 
                    fg="orange", 
                    bg="black"
                ).pack(anchor="w", padx=20)
                
        # Chibi levels
        tk.Label(
            info_frame, 
            text="Chibi Levels:", 
            fg="yellow", 
            bg="black",
            font=(self.config['font_family'], self.config['font_size']+1, "bold")
        ).pack(anchor="w", pady=(10, 5))
        
        tk.Label(
            info_frame, 
            text=data.get("chibi_levels", "N/A"), 
            fg="cyan", 
            bg="black"
        ).pack(anchor="w", padx=20)
        
        # Explorer notes
        if data.get("explorer_notes"):
            tk.Label(
                info_frame, 
                text="Explorer Notes Bonuses:", 
                fg="yellow", 
                bg="black",
                font=(self.config['font_family'], self.config['font_size']+1, "bold")
            ).pack(anchor="w", pady=(10, 5))
            
            for note in data["explorer_notes"]:
                tk.Label(
                    info_frame, 
                    text=f"• {note}", 
                    fg="lightgreen", 
                    bg="black"
                ).pack(anchor="w", padx=20)
                
        # Comments section
        tk.Label(
            info_frame, 
            text="Comments:", 
            fg="yellow", 
            bg="black",
            font=(self.config['font_family'], self.config['font_size']+1, "bold")
        ).pack(anchor="w", pady=(10, 5))
        
        comments_text = tk.Text(
            info_frame, 
            height=4, 
            width=50, 
            bg="#333333", 
            fg="white"
        )
        comments_text.pack(anchor="w", padx=20, pady=5)
        comments_text.insert(tk.END, data.get("comments", ""))
        
        # Save comments button
        def save_comments():
            selected_idx = self.char_listbox.curselection()
            if not selected_idx:
                return
                
            selected_text = self.char_listbox.get(selected_idx[0])
            if selected_text not in self.char_lookup:
                return
                
            steam_id, char_idx = self.char_lookup[selected_text]
            
            # Update comments
            self.characters[steam_id][char_idx]["comments"] = comments_text.get("1.0", tk.END).strip()
            self.data_manager.save_data(self.characters)
            
            messagebox.showinfo("Comments Saved", "Comments have been saved successfully!")
            
        tk.Button(
            info_frame, 
            text="Save Comments", 
            command=save_comments,
            bg="#444444",
            fg="white"
        ).pack(anchor="w", padx=20, pady=5)
        
    def open_image(self):
        """Open an implant image and extract character data."""
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")]
        )
        
        if not file_path:
            return
            
        steam_id = self.selected_steam.get()
        if not steam_id:
            messagebox.showerror("Error", "Please select or add a Steam account first.")
            return
            
        try:
            # Extract data from image
            data = self.ocr.extract_implant_data(file_path)
            
            # Check if this is a clone
            sample_number = data.get("sample_number")
            if sample_number:
                existing = [char for char in self.characters.get(steam_id, []) 
                           if char.get("sample_number") == sample_number]
                
                if existing and self.config['allow_clones']:
                    result = messagebox.askyesnocancel(
                        "Duplicate Sample Number",
                        f"A character with sample number {sample_number} already exists.\n\n"
                        f"Would you like to add this as a clone?\n\n"
                        f"Yes: Add as clone\nNo: Replace existing\nCancel: Abort import"
                    )
                    
                    if result is None:  # Cancel
                        return
                    elif result:  # Yes - add as clone
                        # Add character with clone flag
                        self.data_manager.add_character(steam_id, data, file_path, allow_clone=True)
                    else:  # No - replace existing
                        # Find and replace the existing character
                        for i, char in enumerate(self.characters[steam_id]):
                            if char.get("sample_number") == sample_number:
                                # Update with new data
                                self.data_manager.update_character(steam_id, i, data)
                                break
                else:
                    # Normal add
                    self.data_manager.add_character(steam_id, data, file_path, allow_clone=self.config['allow_clones'])
            else:
                # Normal add if no sample number
                self.data_manager.add_character(steam_id, data, file_path)
            
            # Refresh character list
            self.characters = self.data_manager.characters
            self.update_character_list()
            
            # Display the new character
            self.update_display(data)
            
            messagebox.showinfo("Success", "Character implant data extracted and saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process image: {e}")
    
    def clone_character(self):
        """Create a clone of the selected character."""
        selected_idx = self.char_listbox.curselection()
        if not selected_idx:
            messagebox.showinfo("Info", "Please select a character to clone.")
            return
            
        # Use the first selected character
        selected_text = self.char_listbox.get(selected_idx[0])
        if selected_text not in self.char_lookup:
            return
            
        steam_id, char_idx = self.char_lookup[selected_text]
        
        # Get original character data
        original_char = self.characters[steam_id][char_idx]
        
        # Create clone data
        clone_data = dict(original_char)  # Copy all data
        
        # Set clone flag
        clone_data["is_clone"] = True
        
        # Check existing clones to determine clone index
        sample_number = clone_data.get("sample_number")
        existing_clones = [char for char in self.characters[steam_id] 
                         if char.get("sample_number") == sample_number and char.get("is_clone")]
        
        clone_data["clone_index"] = len(existing_clones) + 1
        
        # Handle image
        image_path = clone_data.get("background_image")
        if image_path and os.path.exists(image_path):
            # Create a new image name with _clone suffix
            dir_name = os.path.dirname(image_path)
            base_name, ext = os.path.splitext(os.path.basename(image_path))
            
            if "_clone" in base_name:
                # Already a clone, increment index
                base_name = base_name.split("_clone")[0]
            
            new_image_name = f"{base_name}_clone{clone_data['clone_index']}{ext}"
            new_image_path = os.path.join(dir_name, new_image_name)
            
            # Copy image
            try:
                shutil.copy2(image_path, new_image_path)
                clone_data["background_image"] = new_image_path
            except Exception as e:
                print(f"Error copying image: {e}")
        
        # Add clone to data
        self.characters[steam_id].append(clone_data)
        
        # Save data
        self.data_manager.save_data(self.characters)
        
        # Update UI
        self.update_character_list()
        
        messagebox.showinfo("Success", f"Created clone of character with Sample #{sample_number}")
            
    def delete_character(self):
        """Delete the selected character."""
        selected_idx = self.char_listbox.curselection()
        if not selected_idx:
            messagebox.showinfo("Info", "Please select a character to delete.")
            return
            
        # Get all selected characters
        selected_chars = []
        for idx in selected_idx:
            selected_text = self.char_listbox.get(idx)
            if selected_text in self.char_lookup:
                selected_chars.append((selected_text, self.char_lookup[selected_text]))
        
        if not selected_chars:
            return
            
        # Confirm deletion
        confirm_message = f"Are you sure you want to delete {len(selected_chars)} character(s)?"
        if len(selected_chars) == 1:
            steam_id, char_idx = selected_chars[0][1]
            char = self.characters[steam_id][char_idx]
            confirm_message = f"Are you sure you want to delete character with Sample #{char.get('sample_number', 'N/A')}?"
            
        if messagebox.askyesno("Confirm Deletion", confirm_message):
            # Delete characters in reverse order to avoid index issues
            for _, (steam_id, char_idx) in sorted(selected_chars, key=lambda x: x[1][1], reverse=True):
                self.data_manager.delete_character(steam_id, char_idx)
                
            # Refresh data and UI
            self.characters = self.data_manager.characters
            self.update_character_list()
            
            # Clear display
            for widget in self.display_frame.winfo_children():
                widget.destroy()
                
            messagebox.showinfo("Success", f"{len(selected_chars)} character(s) deleted successfully!")
                
    def change_background(self):
        """Change the background image for the selected character."""
        selected_idx = self.char_listbox.curselection()
        if not selected_idx:
            messagebox.showinfo("Info", "Please select a character first.")
            return
            
        # Get the first selected character
        selected_text = self.char_listbox.get(selected_idx[0])
        if selected_text not in self.char_lookup:
            return
            
        steam_id, char_idx = self.char_lookup[selected_text]
        
        # Select new image
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")]
        )
        
        if not file_path:
            return
            
        try:
            # Copy image to implants folder
            steam_folder = os.path.join(self.config['base_directory'], steam_id)
            implants_folder = os.path.join(steam_folder, "implants")
            os.makedirs(implants_folder, exist_ok=True)
            
            image_name = os.path.basename(file_path)
            new_image_path = os.path.join(implants_folder, image_name)
            
            # Copy image
            import shutil
            shutil.copy2(file_path, new_image_path)
            
            # Update character data
            self.characters[steam_id][char_idx]["background_image"] = new_image_path
            self.data_manager.save_data(self.characters)
            
            # Update display
            self.update_display(self.characters[steam_id][char_idx])
            
            messagebox.showinfo("Success", "Background image updated successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update background image: {e}")
            
    def export_to_csv(self):
        """Export character data to CSV."""
        # Select output file
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        
        if not file_path:
            return
            
        # Export data
        if self.data_manager.export_to_csv(file_path):
            messagebox.showinfo("Success", f"Character data exported to {file_path} successfully!")
        else:
            messagebox.showerror("Error", "Failed to export character data.")
    
    def batch_export_characters(self):
        """Export selected characters to individual CSV files."""
        selected_indices = self.char_listbox.curselection()
        if not selected_indices:
            messagebox.showinfo("Batch Export", "Select at least one character to export.")
            return
        
        # Select output directory
        output_dir = filedialog.askdirectory(
            title="Select Output Directory for Character Exports"
        )
        
        if not output_dir:
            return
        
        # Export each selected character
        success_count = 0
        for idx in selected_indices:
            selected_text = self.char_listbox.get(idx)
            if selected_text in self.char_lookup:
                steam_id, char_idx = self.char_lookup[selected_text]
                char = self.characters[steam_id][char_idx]
                
                # Create character-specific filename
                sample_number = char.get("sample_number", "unknown")
                name = char.get("vernacular_id", "character").replace(" ", "_")
                filename = f"{sample_number}_{name}.csv"
                output_path = os.path.join(output_dir, filename)
                
                # Export single character
                try:
                    import csv
                    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                        fieldnames = [
                            'Steam ID', 'Sample Number', 'Vernacular ID', 'Gender', 
                            'Survival Quotient', 'Chibi Levels', 'Explorer Notes', 
                            'Comments', 'Image Path', 'Date Added', 'Is Clone', 'Clone Index'
                        ]
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerow({
                            'Steam ID': steam_id,
                            'Sample Number': char.get('sample_number', 'N/A'),
                            'Vernacular ID': char.get('vernacular_id', 'N/A'),
                            'Gender': char.get('gender', 'N/A'),
                            'Survival Quotient': ', '.join(char.get('survival_quotient', [])),
                            'Chibi Levels': char.get('chibi_levels', 'N/A'),
                            'Explorer Notes': ', '.join(char.get('explorer_notes', [])),
                            'Comments': char.get('comments', ''),
                            'Image Path': char.get('background_image', 'N/A'),
                            'Date Added': char.get('date_added', 'N/A'),
                            'Is Clone': 'Yes' if char.get('is_clone') else 'No',
                            'Clone Index': char.get('clone_index', 0)
                        })
                    success_count += 1
                except Exception as e:
                    print(f"Error exporting {filename}: {e}")
        
        messagebox.showinfo("Batch Export", f"Successfully exported {success_count} characters to {output_dir}")
    
    def compare_characters(self):
        """Compare selected characters."""
        selected_indices = self.char_listbox.curselection()
        if len(selected_indices) < 2:
            messagebox.showinfo("Compare", "Select at least 2 characters to compare.")
            return
        
        # Get character data
        characters = []
        for idx in selected_indices:
            selected_text = self.char_listbox.get(idx)
            if selected_text in self.char_lookup:
                steam_id, char_idx = self.char_lookup[selected_text]
                characters.append(self.characters[steam_id][char_idx])
        
        # Create comparison window
        compare_window = tk.Toplevel(self.root)
        compare_window.title("Character Comparison")
        compare_window.geometry("900x600")
        compare_window.configure(bg=self.root.cget("bg"))
        
        # Create scrollable frame
        canvas = tk.Canvas(compare_window, bg=self.root.cget("bg"))
        scrollbar = tk.Scrollbar(compare_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.root.cget("bg"))
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add comparison table
        fields = [
            ("Sample Number", "sample_number"),
            ("Name", "vernacular_id"),
            ("Gender", "gender"),
            ("Boss Kills", "survival_quotient"),
            ("Chibi Levels", "chibi_levels"),
            ("Explorer Notes", "explorer_notes"),
            ("Date Added", "date_added"),
            ("Is Clone", "is_clone")
        ]
        
        # Add header row
        header_frame = tk.Frame(scrollable_frame, bg=self.root.cget("bg"))
        header_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(header_frame, text="Field", width=15, anchor="w", 
                bg="#333333", fg="white", font=(self.config['font_family'], 10, "bold")
               ).pack(side="left", padx=2)
        
        for i, char in enumerate(characters):
            name = char.get("vernacular_id", f"Character {i+1}")
            tk.Label(header_frame, text=name, width=20, anchor="w",
                    bg="#333333", fg="white", font=(self.config['font_family'], 10, "bold")
                   ).pack(side="left", padx=2)
        
        # Add data rows
        for field_name, field_key in fields:
            row_frame = tk.Frame(scrollable_frame, bg=self.root.cget("bg"))
            row_frame.pack(fill="x", padx=10, pady=2)
            
            tk.Label(row_frame, text=field_name, width=15, anchor="w",
                    bg="#222222", fg="white").pack(side="left", padx=2)
            
            for char in characters:
                if field_key in ["survival_quotient", "explorer_notes"]:
                    # Handle lists
                    value = "\n".join(char.get(field_key, []))
                    text = tk.Text(row_frame, width=20, height=5, wrap=tk.WORD,
                                  bg="#222222", fg="white")
                    text.insert(tk.END, value)
                    text.config(state=tk.DISABLED)
                    text.pack(side="left", padx=2)
                elif field_key == "is_clone":
                    # Handle boolean
                    value = "Yes" if char.get(field_key) else "No"
                    tk.Label(row_frame, text=value, width=20, anchor="w",
                            bg="#222222", fg="white").pack(side="left", padx=2)
                else:
                    # Handle simple values
                    value = char.get(field_key, "N/A")
                    tk.Label(row_frame, text=str(value), width=20, anchor="w",
                            bg="#222222", fg="white").pack(side="left", padx=2)
        
        # Add close button
        tk.Button(
            compare_window,
            text="Close",
            command=compare_window.destroy
        ).pack(pady=10)
            
    def import_from_csv(self):
        """Import character data from CSV."""
        # Select input file
        file_path = filedialog.askopenfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        
        if not file_path:
            return
        
        # Ask if user wants to overwrite existing characters
        overwrite = messagebox.askyesno(
            "Import Options", 
            "Do you want to overwrite existing characters with the same Sample Number?",
            icon=messagebox.QUESTION
        )
        
        # Ask about clones
        allow_clones = messagebox.askyesno(
            "Import Options",
            "Allow duplicate Sample Numbers as clones?",
            icon=messagebox.QUESTION
        ) if not overwrite else False
        
        # Import data with overwrite option
        try:
            success_count, error_count, error_details = self.data_manager.import_from_csv(
                file_path, overwrite, allow_clones
            )
            
            if success_count > 0:
                # Refresh data and UI
                self.characters = self.data_manager.characters
                self.update_steam_dropdown()
                
                error_message = f"Successfully imported {success_count} characters!"
                if error_count > 0:
                    error_message += f"\n\nErrors: {error_count}"
                    if error_details and len(error_details) > 0:
                        error_message += "\n\nDetails:"
                        for detail in error_details[:5]:  # Show first 5 errors
                            error_message += f"\n• {detail}"
                        if len(error_details) > 5:
                            error_message += f"\n... and {len(error_details) - 5} more errors"
                
                messagebox.showinfo("Import Complete", error_message)
            else:
                error_message = "Failed to import characters from CSV."
                if error_details and len(error_details) > 0:
                    error_message += "\n\nDetails:"
                    for detail in error_details:
                        error_message += f"\n• {detail}"
                        
                messagebox.showerror("Import Failed", error_message)
        except ValueError as e:
            # Handle the specific error we're seeing
            if "too many values to unpack" in str(e):
                messagebox.showerror("Import Error", "There's a version mismatch between your CSV import functions. Please restart the application after updating all files.")
            else:
                messagebox.showerror("Import Failed", f"Value error: {e}")
        except Exception as e:
            messagebox.showerror("Import Failed", f"An error occurred: {e}")
    
    def export_csv_template(self):
        """Export a CSV template for importing character data."""
        # Select output file
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            initialfile="character_template.csv"
        )
        
        if not file_path:
            return
            
        # Create template
        if self.data_manager.create_csv_template(file_path):
            messagebox.showinfo("Template Exported", 
                               f"CSV template has been exported to:\n{file_path}\n\n"
                               f"You can fill this template and import it later.")
        else:
            messagebox.showerror("Export Failed", "Failed to export CSV template.")
            
    def add_steam_account(self):
        """Add a new Steam account."""
        steam_id = self.steam_entry.get().strip()
        if not steam_id:
            messagebox.showinfo("Info", "Please enter a Steam ID.")
            return
            
        if steam_id in self.characters:
            messagebox.showinfo("Info", f"Steam account {steam_id} already exists.")
            return
            
        # Add Steam account
        self.characters[steam_id] = []
        
        # Create directory structure
        steam_folder = os.path.join(self.config['base_directory'], steam_id)
        implants_folder = os.path.join(steam_folder, "implants")
        os.makedirs(implants_folder, exist_ok=True)
        
        # Save data
        self.data_manager.save_data(self.characters)
        
        # Update UI
        self.update_steam_dropdown()
        self.steam_entry.delete(0, tk.END)
        
        messagebox.showinfo("Success", f"Steam account {steam_id} added successfully!")
    
    def backup_data(self):
        """Create a full backup of all character data."""
        # Select output directory
        backup_dir = filedialog.askdirectory(
            title="Select Backup Directory"
        )
        
        if not backup_dir:
            return
        
        # Ask if user wants to include images
        include_images = messagebox.askyesno(
            "Backup Options",
            "Include character images in backup?\n\n"
            "Note: This may take longer if you have many images.",
            icon=messagebox.QUESTION
        )
        
        # Create backup
        success, backup_file, image_dir, copied_images = self.data_manager.backup_data(backup_dir, include_images)
        
        if success:
            messagebox.showinfo("Backup Complete", 
                              f"Backup created successfully at:\n{backup_file}\n\n"
                              f"Characters: {sum(len(chars) for chars in self.characters.values())}\n"
                              f"Images: {copied_images if include_images else 'Not included'}")
        else:
            messagebox.showerror("Backup Error", "Failed to create backup.")
    
    def restore_data(self):
        """Restore data from a backup file."""
        # Select backup file
        backup_file = filedialog.askopenfilename(
            title="Select Backup File to Restore",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        
        if not backup_file:
            return
        
        # Confirm restoration
        if not messagebox.askyesno("Confirm Restore", 
                                 "Restoring from backup will replace all current character data. Continue?",
                                 icon=messagebox.WARNING):
            return
        
        # Restore data
        if self.data_manager.restore_data(backup_file):
            # Refresh data and UI
            self.characters = self.data_manager.characters
            self.update_steam_dropdown()
            
            messagebox.showinfo("Restore Complete", 
                              f"Successfully restored {sum(len(chars) for chars in self.characters.values())} characters.")
        else:
            messagebox.showerror("Restore Error", "Failed to restore from backup.")
    
    def show_data_location(self):
        """Show where data is being stored."""
        info = self.data_manager.get_storage_location()
        
        info_text = f"Base Directory:\n{info['base_directory']}\n\nJSON Data File:\n{info['data_file']}"
        
        # Check if directory and file exist
        info_text += f"\n\nBase Directory exists: {info['base_dir_exists']}"
        info_text += f"\nJSON File exists: {info['data_file_exists']}"
        
        # List files in the directory if it exists
        if 'directory_contents' in info:
            files = info['directory_contents']
            info_text += f"\n\nFiles in directory ({len(files)}):"
            for file in files[:20]:  # Show first 20 files
                info_text += f"\n- {file}"
            
            if len(files) > 20:
                info_text += f"\n... and {len(files) - 20} more"
        
        # Show steam accounts
        if 'steam_accounts' in info and info['steam_accounts']:
            info_text += f"\n\nSteam accounts found:"
            for account in info['steam_accounts']:
                name = account['name']
                implant_count = account.get('implant_count', 0)
                info_text += f"\n- {name} ({implant_count} implants)"
        
        # Open the folder in File Explorer
        def open_folder():
            if info['base_dir_exists']:
                os.startfile(info['base_directory'])  # This works on Windows
            else:
                messagebox.showerror("Error", f"Directory does not exist: {info['base_directory']}")
        
        # Create dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Data Storage Location")
        dialog.geometry("500x400")
        dialog.configure(bg=self.root.cget("bg"))
        
        # Add text
        text = tk.Text(dialog, bg=self.root.cget("bg"), fg="white", wrap=tk.WORD)
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text.insert(tk.END, info_text)
        text.config(state=tk.DISABLED)
        
        # Add button to open folder
        tk.Button(
            dialog,
            text="Open Folder in Explorer",
            command=open_folder
        ).pack(pady=10)
        
    def scan_and_update_implants(self):
        """Scan and update implants from the directory structure."""
        count = self.data_manager.scan_and_import_all(self.ocr)
        
        if count > 0:
            # Refresh data and UI
            self.characters = self.data_manager.characters
            self.update_steam_dropdown()
            messagebox.showinfo("Import Complete", f"Imported {count} new character implants.")
        
    def run(self):
        """Run the application main loop."""
        self.root.mainloop()

# Entry point for standalone execution
if __name__ == "__main__":
    app = CharacterImplantApp()
    app.run()
