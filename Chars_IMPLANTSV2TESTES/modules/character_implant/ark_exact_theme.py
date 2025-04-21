import os
import tkinter as tk
from tkinter import ttk, font

class ARKExactTheme:
    """Applies an exact match to the desired ARK theme appearance."""
    
    def __init__(self, root, app):
        """Initialize the theme manager.
        
        Args:
            root (tk.Tk): The root Tkinter window
            app: The main application instance
        """
        self.root = root
        self.app = app
        
        # ARK theme color palette (exact match to the right side image)
        self.colors = {
            'bg': '#0a1820',              # Very dark blue background
            'panel_bg': '#0e2130',        # Dark blue panel background
            'panel_header': '#102638',    # Slightly lighter blue for headers
            'accent': '#2cc8de',          # Cyan accent
            'text': '#ffffff',            # White text
            'text_secondary': '#aaddee',  # Light blue-gray text
            'text_headers': '#2cc8de',    # Cyan headers
            'button_bg': '#1d3548',       # Dark blue button
            'button_delete': '#af3030',   # Red delete button
            'button_import': '#c88a00',   # Orange import button  
            'boss_alpha': '#ff0000',      # Red for Alpha bosses
            'boss_beta': '#ffa500',       # Orange for Beta bosses
            'boss_gamma': '#ffff00',      # Yellow for Gamma bosses
        }
        
        # Setup fonts
        self.setup_fonts()
        
        # Apply theme to the application
        self.apply_theme()
        
    def setup_fonts(self):
        """Set up fonts for the application."""
        # Default fonts to use
        self.fonts = {
            'title': ('Arial', 20, 'bold'),
            'header': ('Arial', 14, 'bold'),
            'subheader': ('Arial', 12, 'bold'),
            'normal': ('Arial', 10),
            'small': ('Arial', 9),
            'button': ('Arial', 10, 'bold'),
            'list': ('Arial', 10)
        }
        
    def apply_theme(self):
        """Apply the ARK theme to the application."""
        # Configure root window
        self.root.configure(bg=self.colors['bg'])
        self.root.title("ARK Character Implant Manager")
        
        # Replace the original update_display method to create the exact look
        self.enhance_character_display()
        
        # Apply theme to frames
        self.style_frames()
        
        # Style the control elements
        self.style_controls()
        
        # Style the character list
        self.style_character_list()
        
        # Style the buttons
        self.style_buttons()
        
        # Create a header
        self.create_header()
        
        # Create a status bar
        self.create_status_bar()
        
    def style_frames(self):
        """Style the main frames."""
        # Apply to all frames
        for frame_name in ['control_frame', 'display_frame', 'list_frame', 'button_frame']:
            if hasattr(self.app, frame_name):
                frame = getattr(self.app, frame_name)
                frame.configure(
                    bg=self.colors['bg'],
                    highlightbackground=self.colors['accent'],
                    highlightthickness=1
                )
                
    def style_controls(self):
        """Style the control elements."""
        # Style labels
        for widget in self.app.control_frame.winfo_children():
            if isinstance(widget, tk.Label):
                widget.configure(
                    fg=self.colors['text'],
                    bg=self.colors['bg'],
                    font=self.fonts['normal']
                )
        
        # Style entry widgets
        if hasattr(self.app, 'steam_entry'):
            self.app.steam_entry.configure(
                bg='#1d3548',
                fg=self.colors['text'],
                insertbackground=self.colors['text'],
                highlightbackground=self.colors['accent'],
                highlightthickness=1,
                font=self.fonts['normal']
            )
            
        # Style search elements if they exist
        if hasattr(self.app, 'search_var'):
            # Find search widgets
            for widget in self.app.root.winfo_children():
                if isinstance(widget, tk.Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, tk.Entry) and hasattr(child, 'textvariable'):
                            try:
                                if str(child.cget('textvariable')) == str(self.app.search_var):
                                    # Style the search entry
                                    child.configure(
                                        bg='#1d3548',
                                        fg=self.colors['text'],
                                        insertbackground=self.colors['text'],
                                        highlightbackground=self.colors['accent'],
                                        highlightthickness=1,
                                        font=self.fonts['normal']
                                    )
                            except:
                                pass
    
    def style_character_list(self):
        """Style the character list."""
        if hasattr(self.app, 'char_listbox'):
            self.app.char_listbox.configure(
                bg='#0e2130',
                fg=self.colors['text'],
                selectbackground='#1d3548',
                selectforeground=self.colors['text'],
                font=self.fonts['list'],
                borderwidth=1,
                highlightbackground=self.colors['accent'],
                highlightthickness=1
            )
            
            # Update the list to add alternating row colors
            self.enhance_char_list_display()
    
    def style_buttons(self):
        """Style the action buttons."""
        if hasattr(self.app, 'button_frame'):
            for widget in self.app.button_frame.winfo_children():
                if isinstance(widget, tk.Button):
                    button_text = widget.cget('text')
                    
                    # Choose button color based on function
                    if "Delete" in button_text:
                        bg_color = self.colors['button_delete']
                    elif "Import" in button_text:
                        bg_color = self.colors['button_import']
                    elif "Export" in button_text:
                        bg_color = '#1a7da8'  # Blue for export
                    elif "Clone" in button_text:
                        bg_color = '#238a9e'  # Teal for clone
                    elif "Compare" in button_text:
                        bg_color = '#1d6080'  # Dark blue for compare
                    elif "Select" in button_text:
                        bg_color = '#1d3548'  # Standard for select
                    elif "Change" in button_text:
                        bg_color = '#1d3548'  # Standard for change
                    elif "Show" in button_text:
                        bg_color = '#1d3548'  # Standard for show
                    else:
                        bg_color = self.colors['button_bg']
                    
                    # Configure the button
                    widget.configure(
                        bg=bg_color,
                        fg=self.colors['text'],
                        activebackground=self.add_brightness(bg_color, 30),
                        activeforeground=self.colors['text'],
                        font=self.fonts['button'],
                        borderwidth=1,
                        relief=tk.RAISED,
                        padx=10
                    )
                    
                    # Add hover effect
                    self.add_hover_effect(widget, bg_color)
    
    def add_hover_effect(self, widget, base_color):
        """Add hover effect to a widget."""
        hover_color = self.add_brightness(base_color, 30)
        
        def on_enter(e):
            widget.config(background=hover_color)
            
        def on_leave(e):
            widget.config(background=base_color)
            
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def add_brightness(self, color_hex, amount):
        """Add brightness to a hex color."""
        # Convert hex to RGB
        color_hex = color_hex.lstrip('#')
        r, g, b = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
        
        # Add brightness
        r = max(0, min(255, r + amount))
        g = max(0, min(255, g + amount))
        b = max(0, min(255, b + amount))
        
        # Convert back to hex
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def create_header(self):
        """Create a styled header for the application."""
        # Create header frame at the top
        header_frame = tk.Frame(self.root, bg='#071520', height=60)
        header_frame.pack(side=tk.TOP, fill=tk.X)
        
        # Add title
        title_label = tk.Label(
            header_frame,
            text="ARK CHARACTER IMPLANT MANAGER",
            font=('Arial', 20, 'bold'),
            fg='#00c8e6',
            bg='#071520'
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        # Store header for later reference
        self.header = header_frame
    
    def create_status_bar(self):
        """Create a status bar at the bottom of the window."""
        # Create status bar frame
        status_bar = tk.Frame(self.root, bg='#071520', height=20)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Status text on the left
        self.status_text = tk.StringVar(value="Ready")
        status_label = tk.Label(
            status_bar,
            textvariable=self.status_text,
            fg=self.colors['text'],
            bg='#071520',
            font=self.fonts['small'],
            anchor="w"
        )
        status_label.pack(side=tk.LEFT, padx=10)
        
        # Character count on the right
        self.char_count = tk.StringVar(value="No characters loaded")
        char_count_label = tk.Label(
            status_bar,
            textvariable=self.char_count,
            fg="#7aaad0",
            bg='#071520',
            font=self.fonts['small'],
            anchor="e"
        )
        char_count_label.pack(side=tk.RIGHT, padx=10)
        
        # Update character count when list changes
        def update_char_count(*args):
            steam_id = self.app.selected_steam.get()
            if steam_id and steam_id in self.app.characters:
                count = len(self.app.characters[steam_id])
                self.char_count.set(f"{count} characters in {steam_id}")
            else:
                self.char_count.set("No characters loaded")
        
        # Bind to selected_steam changes
        self.app.selected_steam.trace_add("write", update_char_count)
        
        # Store status bar
        self.status_bar = status_bar
    
    def enhance_character_display(self):
        """Completely replace the character display with a better version."""
        if hasattr(self.app, 'update_display'):
            # Store the original function
            original_update_display = self.app.update_display
            
            # Define our enhanced version that exactly matches the right image
            def enhanced_update_display(data):
                """Enhanced display function to match the right image."""
                # Clear previous widgets
                for widget in self.app.display_frame.winfo_children():
                    widget.destroy()
                
                # Create scrollable area
                canvas = tk.Canvas(
                    self.app.display_frame,
                    bg=self.colors['bg'],
                    highlightthickness=0
                )
                scrollbar = ttk.Scrollbar(
                    self.app.display_frame,
                    orient="vertical",
                    command=canvas.yview
                )
                
                scrollable_frame = tk.Frame(canvas, bg=self.colors['bg'])
                scrollable_frame.bind(
                    "<Configure>",
                    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
                )
                
                canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
                canvas.configure(yscrollcommand=scrollbar.set)
                
                canvas.pack(side="left", fill="both", expand=True)
                scrollbar.pack(side="right", fill="y")
                
                # Character title
                vernacular_id = data.get('vernacular_id', 'Unknown')
                sample_number = data.get('sample_number', 'N/A')
                
                title_label = tk.Label(
                    scrollable_frame,
                    text=f"{vernacular_id} - Sample #{sample_number}",
                    font=('Arial', 14, 'bold'),
                    fg='#2cc8de',
                    bg=self.colors['bg']
                )
                title_label.pack(anchor="nw", padx=10, pady=5)
                
                # Create two-column layout
                content_frame = tk.Frame(scrollable_frame, bg=self.colors['bg'])
                content_frame.pack(fill="both", expand=True, padx=10, pady=5)
                
                # Left column - Image
                left_column = tk.Frame(content_frame, bg=self.colors['bg'], width=400)
                left_column.pack(side="left", fill="both", expand=True, padx=5)
                
                # Right column - Info panels
                right_column = tk.Frame(content_frame, bg=self.colors['bg'], width=400)
                right_column.pack(side="right", fill="both", expand=True, padx=5)
                
                # Image panel
                if data.get('background_image') and os.path.exists(data.get('background_image')):
                    try:
                        from PIL import Image, ImageTk
                        img = Image.open(data.get('background_image'))
                        img = img.resize((400, 300), Image.LANCZOS)
                        photo = ImageTk.PhotoImage(img)
                        
                        img_panel = tk.Label(
                            left_column,
                            image=photo,
                            bg=self.colors['panel_bg'],
                            borderwidth=2,
                            relief="solid"
                        )
                        img_panel.image = photo  # Keep a reference
                        img_panel.pack(fill="both", expand=True, padx=5, pady=5)
                    except Exception as e:
                        print(f"Error loading image: {e}")
                        # Fallback if image can't be loaded
                        img_label = tk.Label(
                            left_column,
                            text="[Character Image]",
                            bg=self.colors['panel_bg'],
                            fg=self.colors['text'],
                            height=15
                        )
                        img_label.pack(fill="both", expand=True, padx=5, pady=5)
                else:
                    # No image available
                    img_label = tk.Label(
                        left_column,
                        text="[No Character Image]",
                        bg=self.colors['panel_bg'],
                        fg=self.colors['text'],
                        height=15
                    )
                    img_label.pack(fill="both", expand=True, padx=5, pady=5)
                
                # Character Info Panel
                info_panel = tk.LabelFrame(
                    right_column,
                    text="Character Information",
                    font=('Arial', 12, 'bold'),
                    fg='#2cc8de',
                    bg=self.colors['panel_bg'],
                    padx=10,
                    pady=10
                )
                info_panel.pack(fill="x", pady=5)
                
                # Gender info
                gender_label = tk.Label(
                    info_panel,
                    text="Gender:",
                    font=('Arial', 10),
                    fg=self.colors['text_secondary'],
                    bg=self.colors['panel_bg'],
                    anchor="w"
                )
                gender_label.grid(row=0, column=0, sticky="w", padx=5, pady=2)
                
                gender_value = tk.Label(
                    info_panel,
                    text=data.get('gender', 'N/A'),
                    font=('Arial', 10),
                    fg=self.colors['text'],
                    bg=self.colors['panel_bg'],
                    anchor="w"
                )
                gender_value.grid(row=0, column=1, sticky="w", padx=5, pady=2)
                
                # Date Added info
                date_label = tk.Label(
                    info_panel,
                    text="Date Added:",
                    font=('Arial', 10),
                    fg=self.colors['text_secondary'],
                    bg=self.colors['panel_bg'],
                    anchor="w"
                )
                date_label.grid(row=1, column=0, sticky="w", padx=5, pady=2)
                
                date_value = tk.Label(
                    info_panel,
                    text=data.get('date_added', 'N/A'),
                    font=('Arial', 10),
                    fg=self.colors['text'],
                    bg=self.colors['panel_bg'],
                    anchor="w"
                )
                date_value.grid(row=1, column=1, sticky="w", padx=5, pady=2)
                
                # Boss Kills Panel
                if data.get('survival_quotient'):
                    boss_panel = tk.LabelFrame(
                        right_column,
                        text="Boss Kills",
                        font=('Arial', 12, 'bold'),
                        fg='#2cc8de',
                        bg=self.colors['panel_bg'],
                        padx=10,
                        pady=10
                    )
                    boss_panel.pack(fill="x", pady=5)
                    
                    # Add each boss kill with color-coded indicator
                    for i, boss in enumerate(data.get('survival_quotient', [])):
                        boss_frame = tk.Frame(boss_panel, bg=self.colors['panel_bg'])
                        boss_frame.pack(fill="x", pady=2)
                        
                        # Color indicator based on difficulty
                        indicator_color = self.colors['boss_alpha']  # Default to Alpha (red)
                        if "Beta" in boss:
                            indicator_color = self.colors['boss_beta']
                        elif "Gamma" in boss:
                            indicator_color = self.colors['boss_gamma']
                        
                        # Create indicator
                        indicator = tk.Canvas(
                            boss_frame, 
                            width=10, 
                            height=10, 
                            bg=self.colors['panel_bg'],
                            highlightthickness=0
                        )
                        indicator.create_oval(2, 2, 10, 10, fill=indicator_color, outline="")
                        indicator.pack(side="left", padx=5)
                        
                        # Boss name
                        boss_label = tk.Label(
                            boss_frame,
                            text=boss,
                            font=('Arial', 10),
                            fg=self.colors['text'],
                            bg=self.colors['panel_bg'],
                            anchor="w"
                        )
                        boss_label.pack(side="left", padx=5)
                
                # Chibi Levels Panel
                chibi_panel = tk.LabelFrame(
                    right_column,
                    text="Chibi Levels",
                    font=('Arial', 12, 'bold'),
                    fg='#2cc8de',
                    bg=self.colors['panel_bg'],
                    padx=10,
                    pady=10
                )
                chibi_panel.pack(fill="x", pady=5)
                
                chibi_value = tk.Label(
                    chibi_panel,
                    text=data.get('chibi_levels', 'N/A'),
                    font=('Arial', 10),
                    fg=self.colors['text'],
                    bg=self.colors['panel_bg'],
                    anchor="w",
                    wraplength=380,
                    justify="left"
                )
                chibi_value.pack(anchor="w", padx=5, pady=2)
                
                # Explorer Notes Panel
                if data.get('explorer_notes'):
                    notes_panel = tk.LabelFrame(
                        scrollable_frame,
                        text="Explorer Notes Bonuses",
                        font=('Arial', 12, 'bold'),
                        fg='#2cc8de',
                        bg=self.colors['panel_bg'],
                        padx=10,
                        pady=10
                    )
                    notes_panel.pack(fill="x", padx=10, pady=5)
                    
                    for note in data.get('explorer_notes', []):
                        note_label = tk.Label(
                            notes_panel,
                            text=f"• {note}",
                            font=('Arial', 10),
                            fg=self.colors['text'],
                            bg=self.colors['panel_bg'],
                            anchor="w",
                            wraplength=780,
                            justify="left"
                        )
                        note_label.pack(anchor="w", padx=5, pady=2)
                
                # Comments Panel
                comments_panel = tk.LabelFrame(
                    scrollable_frame,
                    text="Comments",
                    font=('Arial', 12, 'bold'),
                    fg='#2cc8de',
                    bg=self.colors['panel_bg'],
                    padx=10,
                    pady=10
                )
                comments_panel.pack(fill="x", padx=10, pady=5)
                
                comments_text = tk.Text(
                    comments_panel,
                    height=4,
                    width=50,
                    bg='#0a1820',
                    fg=self.colors['text'],
                    font=('Arial', 10),
                    insertbackground=self.colors['text']
                )
                comments_text.pack(fill="x", pady=5)
                comments_text.insert(tk.END, data.get('comments', ''))
                
                # Save comments button
                def save_comments():
                    selected_idx = self.app.char_listbox.curselection()
                    if not selected_idx:
                        return
                        
                    selected_text = self.app.char_listbox.get(selected_idx[0])
                    if selected_text not in self.app.char_lookup:
                        return
                        
                    steam_id, char_idx = self.app.char_lookup[selected_text]
                    
                    # Update comments
                    self.app.characters[steam_id][char_idx]["comments"] = comments_text.get("1.0", tk.END).strip()
                    self.app.data_manager.save_data(self.app.characters)
                    
                    tk.messagebox.showinfo("Comments Saved", "Comments have been saved successfully!")
                    
                save_btn = tk.Button(
                    comments_panel,
                    text="Save Comments",
                    bg='#1d3548',
                    fg=self.colors['text'],
                    font=('Arial', 10),
                    command=save_comments,
                    padx=5
                )
                save_btn.pack(side="right", padx=5, pady=5)
                
                # Add hover effect to save button
                self.add_hover_effect(save_btn, '#1d3548')
            
            # Replace the original update_display function
            self.app.update_display = enhanced_update_display
    
    def enhance_char_list_display(self):
        """Enhance the character list with alternating row colors."""
        if hasattr(self.app, 'update_character_list'):
            # Store the original function
            original_update_list = self.app.update_character_list
            
            # Define our enhanced version
            def enhanced_update_list(event=None):
                # Call the original function first
                original_update_list(event)
                
                # Now enhance the listbox appearance
                if hasattr(self.app, 'char_listbox'):
                    listbox = self.app.char_listbox
                    
                    # Clear any existing tags
                    for i in range(listbox.size()):
                        listbox.itemconfig(i, {'bg': '#0e2130'})
                    
                    # Add alternating row colors and highlight clones
                    for i in range(listbox.size()):
                        item_text = listbox.get(i)
                        
                        # Apply alternating row colors
                        if i % 2 == 0:
                            listbox.itemconfig(i, {'bg': '#0e2130'})
                        else:
                            listbox.itemconfig(i, {'bg': '#122638'})
                        
                        # Highlight clones
                        if "(Clone)" in item_text:
                            listbox.itemconfig(i, {'fg': '#ffa600'})
            
            # Replace the original function
            self.app.update_character_list = enhanced_update_list
    
    def update_status(self, message):
        """Update the status bar message."""
        if hasattr(self, 'status_text'):
            self.status_text.set(message)
            self.root.update_idletasks()

def apply_exact_theme(root, app):
    """Apply an exact match to the ARK theme in the right image.
    
    Args:
        root (tk.Tk): The root Tkinter window
        app: The main application instance
        
    Returns:
        ARKExactTheme: Theme manager instance
    """
    # Create theme manager
    theme = ARKExactTheme(root, app)
    
    # Update status
    theme.update_status("ARK Theme applied successfully")
    
    return theme