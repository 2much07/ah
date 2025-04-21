import os
import json
import shutil
from datetime import datetime

class CharacterDataManager:
    """Manages character implant data storage and retrieval."""
    
    def __init__(self, base_directory=None, data_file=None):
        """Initialize the data manager.
        
        Args:
            base_directory (str, optional): Base directory for character data
            data_file (str, optional): JSON file path for data storage
        """
        # Set default paths if not provided
        self.base_directory = base_directory or os.path.join(os.path.expanduser("~"), "ARK_AssistantV2", "data", "character_implants")
        self.data_file = data_file or os.path.join(self.base_directory, "characters.json")
        
        # Ensure directories exist
        os.makedirs(self.base_directory, exist_ok=True)
        
        # Initialize character data
        self.characters = self.load_data()
    
    def load_data(self, reset=False):
        """Load character data from JSON file.
        
        Args:
            reset (bool): Whether to reset the data file
            
        Returns:
            dict: Character data
        """
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
        """Save character data to JSON file.
        
        Args:
            data (dict, optional): Data to save, defaults to self.characters
        """
        with open(self.data_file, "w", encoding="utf-8") as file:
            json.dump(data or self.characters, file, indent=4)
    
    def add_character(self, steam_id, character_data, implant_image_path=None):
        """Add a character to a Steam account.
        
        Args:
            steam_id (str): Steam account ID
            character_data (dict): Character data
            implant_image_path (str, optional): Path to implant image to copy
            
        Returns:
            dict: Updated character data
        """
        # Ensure Steam account exists
        if steam_id not in self.characters:
            self.characters[steam_id] = []
            
        # Create Steam account folder structure if it doesn't exist
        steam_folder = os.path.join(self.base_directory, steam_id)
        implants_folder = os.path.join(steam_folder, "implants")
        os.makedirs(implants_folder, exist_ok=True)
        
        # Copy implant image if provided
        if implant_image_path and os.path.exists(implant_image_path):
            image_name = os.path.basename(implant_image_path)
            new_image_path = os.path.join(implants_folder, image_name)
            
            # Copy instead of move to preserve original
            shutil.copy2(implant_image_path, new_image_path)
            
            # Update image path in character data
            character_data["background_image"] = new_image_path
        
        # Add timestamp if not present
        if "date_added" not in character_data:
            character_data["date_added"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Add character to data
        self.characters[steam_id].append(character_data)
        
        # Save updated data
        self.save_data()
        
        return character_data
    
    def get_character(self, steam_id, index):
        """Get a character by index from a Steam account.
        
        Args:
            steam_id (str): Steam account ID
            index (int): Character index
            
        Returns:
            dict: Character data or None if not found
        """
        if steam_id in self.characters and 0 <= index < len(self.characters[steam_id]):
            return self.characters[steam_id][index]
        return None
    
    def delete_character(self, steam_id, index):
        """Delete a character from a Steam account.
        
        Args:
            steam_id (str): Steam account ID
            index (int): Character index
            
        Returns:
            bool: True if successful, False otherwise
        """
        if steam_id in self.characters and 0 <= index < len(self.characters[steam_id]):
            del self.characters[steam_id][index]
            self.save_data()
            return True
        return False
    
    def update_character(self, steam_id, index, updated_data):
        """Update a character's data.
        
        Args:
            steam_id (str): Steam account ID
            index (int): Character index
            updated_data (dict): Updated character data
            
        Returns:
            dict: Updated character data or None if not found
        """
        if steam_id in self.characters and 0 <= index < len(self.characters[steam_id]):
            self.characters[steam_id][index].update(updated_data)
            self.save_data()
            return self.characters[steam_id][index]
        return None
    
    def get_all_steam_ids(self):
        """Get all Steam account IDs.
        
        Returns:
            list: List of Steam account IDs
        """
        return list(self.characters.keys())
    
    def scan_and_import_all(self, ocr_handler):
        """Scan and import all implant images from the directory structure.
        
        Args:
            ocr_handler: OCR handler object with extract_implant_data method
            
        Returns:
            int: Number of new characters imported
        """
        import_count = 0
        
        for steam_id in os.listdir(self.base_directory):
            steam_folder = os.path.join(self.base_directory, steam_id)
            implants_folder = os.path.join(steam_folder, "implants")
            
            if not os.path.isdir(steam_folder) or not os.path.isdir(implants_folder):
                continue
                
            if steam_id not in self.characters:
                self.characters[steam_id] = []
                
            # Get existing sample numbers to avoid duplicates
            existing_samples = {
                char.get("sample_number") 
                for char in self.characters[steam_id] 
                if char.get("sample_number")
            }
            
            for image_name in os.listdir(implants_folder):
                image_path = os.path.join(implants_folder, image_name)
                
                if not os.path.isfile(image_path) or not image_name.lower().endswith((".png", ".jpg", ".jpeg")):
                    continue
                    
                try:
                    char_data = ocr_handler.extract_implant_data(image_path)
                    
                    if not char_data.get("sample_number") or char_data["sample_number"] in existing_samples:
                        continue
                        
                    self.characters[steam_id].append(char_data)
                    existing_samples.add(char_data["sample_number"])
                    import_count += 1
                except Exception as e:
                    print(f"Error processing {image_path}: {e}")
                    
        if import_count > 0:
            self.save_data()
            
        return import_count
    
    def export_to_csv(self, output_path):
        """Export all character data to CSV.
        
        Args:
            output_path (str): Path to save CSV file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            import csv
            
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'Steam ID', 'Sample Number', 'Vernacular ID', 'Gender', 
                    'Survival Quotient', 'Chibi Levels', 'Explorer Notes', 
                    'Comments', 'Image Path', 'Date Added'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for steam_id, characters in self.characters.items():
                    for char in characters:
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
                            'Date Added': char.get('date_added', 'N/A')
                        })
            
            return True
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False
            
    def import_from_csv(self, file_path, overwrite=False):
        """Import character data from a CSV file with overwrite option.
        
        Args:
            file_path (str): Path to the CSV file
            overwrite (bool): Whether to overwrite existing characters
            
        Returns:
            tuple: (success_count, error_count, error_details)
        """
        try:
            import csv
            print(f"Attempting to import from: {file_path}")
            error_details = []
            
            if not os.path.exists(file_path):
                error_details.append(f"File does not exist: {file_path}")
                return (0, 1, error_details)
                
            success_count = 0
            error_count = 0
            
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                try:
                    # Check basic CSV format
                    preview = csvfile.read(1024)
                    csvfile.seek(0)  # Reset file pointer to beginning
                    
                    if ',' not in preview:
                        error_details.append("File doesn't appear to be a valid CSV (no commas found)")
                        return (0, 1, error_details)
                    
                    # Try to read with csv module
                    reader = csv.DictReader(csvfile)
                    
                    # Print headers to debug
                    headers = reader.fieldnames if reader.fieldnames else []
                    print(f"CSV Headers: {headers}")
                    
                    # Check if expected headers are present
                    required_headers = ['Steam ID', 'Sample Number']
                    missing_headers = [h for h in required_headers if h not in headers]
                    if missing_headers:
                        error_details.append(f"Missing required headers: {', '.join(missing_headers)}")
                        return (0, 1, error_details)
                    
                    # Process rows
                    row_number = 1
                    for row in reader:
                        row_number += 1
                        try:
                            steam_id = row.get('Steam ID')
                            if not steam_id:
                                error_details.append(f"Row {row_number}: No Steam ID found")
                                error_count += 1
                                continue
                            
                            sample_number = row.get('Sample Number')
                            if not sample_number or sample_number == 'N/A':
                                error_details.append(f"Row {row_number}: No valid Sample Number")
                                error_count += 1
                                continue
                            
                            # Ensure Steam account exists
                            if steam_id not in self.characters:
                                self.characters[steam_id] = []
                                
                            # Create Steam account folder structure
                            steam_folder = os.path.join(self.base_directory, steam_id)
                            implants_folder = os.path.join(steam_folder, "implants")
                            os.makedirs(implants_folder, exist_ok=True)
                            
                            # Create character data
                            char_data = {
                                "sample_number": sample_number,
                                "vernacular_id": row.get('Vernacular ID', 'N/A'),
                                "gender": row.get('Gender', 'N/A'),
                                "survival_quotient": row.get('Survival Quotient', '').split(', ') if row.get('Survival Quotient') else [],
                                "chibi_levels": row.get('Chibi Levels', 'N/A'),
                                "explorer_notes": row.get('Explorer Notes', '').split(', ') if row.get('Explorer Notes') else [],
                                "comments": row.get('Comments', ''),
                                "background_image": row.get('Image Path', 'N/A'),
                                "date_added": row.get('Date Added', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                            }
                            
                            # Check if character with this sample number already exists
                            exists = False
                            for i, char in enumerate(self.characters[steam_id]):
                                if char.get("sample_number") == sample_number:
                                    if overwrite:
                                        # Replace the existing character
                                        self.characters[steam_id][i] = char_data
                                        success_count += 1
                                    else:
                                        error_details.append(f"Row {row_number}: Character with Sample Number {sample_number} already exists")
                                        error_count += 1
                                    exists = True
                                    break
                            
                            if not exists:
                                self.characters[steam_id].append(char_data)
                                success_count += 1
                        except Exception as e:
                            error_details.append(f"Row {row_number}: {str(e)}")
                            error_count += 1
                    
                    # Save data
                    if success_count > 0:
                        self.save_data()
                    
                    return (success_count, error_count, error_details)
                    
                except csv.Error as e:
                    error_details.append(f"CSV parsing error: {str(e)}")
                    return (0, 1, error_details)
            
        except Exception as e:
            import traceback
            trace = traceback.format_exc()
            return (0, 1, [f"Error importing from CSV: {str(e)}", trace])
            
    def create_csv_template(self, output_path):
        """Create a template CSV file for importing characters with better examples."""
        try:
            import csv
            
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'Steam ID', 'Sample Number', 'Vernacular ID', 'Gender', 
                    'Survival Quotient', 'Chibi Levels', 'Explorer Notes', 
                    'Comments', 'Image Path', 'Date Added'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                # Add an example row
                writer.writerow({
                    'Steam ID': 'mysteamid',  # Use a simple Steam ID for the example
                    'Sample Number': '123456789',
                    'Vernacular ID': 'Example Character',
                    'Gender': 'M',
                    'Survival Quotient': 'Alpha Broodmother, Alpha Megapithecus',
                    'Chibi Levels': 'Chibi-Dino Level-Ups: 2, Max Level: +2',
                    'Explorer Notes': 'All Explorer Notes found +10 Max Levels, All Scorched Earth notes',
                    'Comments': 'This is an example character',
                    'Image Path': '',
                    'Date Added': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                
                # Add a second example with minimal data
                writer.writerow({
                    'Steam ID': 'mysteamid',
                    'Sample Number': '987654321',
                    'Vernacular ID': 'Minimal Example',
                    'Gender': 'F',
                    'Survival Quotient': '',
                    'Chibi Levels': '',
                    'Explorer Notes': '',
                    'Comments': 'Only required fields filled',
                    'Image Path': '',
                    'Date Added': ''
                })
            
            return True
        except Exception as e:
            print(f"Error creating CSV template: {e}")
            return False