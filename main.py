from pathlib import Path
from utils.file_manager import FileManager
from utils.config_validator import validate_config
import tkinter as tk
from tkinter import ttk, filedialog, messagebox



# Define some hardcoded values for the config setting 
MAX_CONCURRENT_TASKS = 2000
TASK_CHECK_INTERVAL = 600






class CopyableMessageDialog:
    def __init__(self, parent, title, message, error=False):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Create and pack widgets
        frame = ttk.Frame(self.dialog, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Use Text widget instead of Label for copyable text
        self.text = tk.Text(frame, wrap=tk.WORD, height=5, width=50)
        self.text.grid(row=0, column=0, padx=5, pady=5)
        self.text.insert('1.0', message)
        self.text.config(state='disabled')  # Make read-only but still selectable
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.text.configure(yscrollcommand=scrollbar.set)
        
        # OK button
        btn = ttk.Button(frame, text="OK", command=self.dialog.destroy)
        btn.grid(row=1, column=0, columnspan=2, pady=10)
        
        # Set icon based on message type
        if error:
            self.dialog.iconbitmap('error')
        
        # Center the dialog on parent window
        self.center_dialog(parent)
        
    def center_dialog(self, parent):
        parent.update_idletasks()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        
        dw = self.dialog.winfo_reqwidth()
        dh = self.dialog.winfo_reqheight()
        
        x = px + (pw - dw) // 2
        y = py + (ph - dh) // 2
        
        self.dialog.geometry(f"+{x}+{y}")

class Application:
    def __init__(self):
        self.root = tk.Tk()
        self.file_manager = FileManager()
        self.files_loaded = {
            'auth': False,
            'config': False,
            'target': False
        }
        self.available_folders = []
        self.setup_gui()

    def setup_gui(self):
        self.root.title("GEE Export UI")
        self.root.geometry("1280x720")

        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # File Loading Section
        self.setup_file_loading_section(main_frame)
        
        # Next Step Button
        self.next_button = ttk.Button(
            main_frame, 
            text="Continue to Export Settings →",
            command=self.proceed_to_next_step,
            state='disabled'
        )
        self.next_button.grid(row=4, column=0, columnspan=3, pady=20)

        # Add status bar at the bottom
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(
            self.root, 
            textvariable=self.status_var, 
            relief=tk.SUNKEN, 
            anchor=tk.W,
            padding=(5, 2)
        )
        self.status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.status_var.set("Ready")

    def update_status(self, message):
        self.status_var.set(message)
        self.root.update()

    def setup_file_loading_section(self, parent):
        # Configure grid weights for resizing
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)  # Make folders frame expandable

        # File Loading Frame
        file_frame = ttk.LabelFrame(parent, text="File Loading Steps", padding="10")
        file_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)

        # Configure columns
        file_frame.columnconfigure(2, weight=1)  # Make filename column expandable

        # Step 1: Auth File
        ttk.Label(file_frame, text="Step 1: Load Google Cloud Authentication").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.auth_button = ttk.Button(file_frame, text="Load Auth File", command=self.load_auth)
        self.auth_button.grid(row=0, column=1, padx=5)
        self.auth_filename = ttk.Label(file_frame, text="No file selected")
        self.auth_filename.grid(row=0, column=2, sticky=(tk.W, tk.E), padx=5)

        # Step 2: Config File
        ttk.Label(file_frame, text="Step 2: Load Configuration File").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.config_button = ttk.Button(file_frame, text="Load Config", command=self.load_config, state='disabled')
        self.config_button.grid(row=1, column=1, padx=5)
        self.config_filename = ttk.Label(file_frame, text="No file selected")
        self.config_filename.grid(row=1, column=2, sticky=(tk.W, tk.E), padx=5)

        # Step 3: Target List
        ttk.Label(file_frame, text="Step 3: Load Target Index List").grid(row=2, column=0, sticky=tk.W, padx=5)
        self.target_button = ttk.Button(file_frame, text="Load Target List", command=self.load_target, state='disabled')
        self.target_button.grid(row=2, column=1, padx=5)
        self.target_filename = ttk.Label(file_frame, text="No file selected")
        self.target_filename.grid(row=2, column=2, sticky=(tk.W, tk.E), padx=5)

        # Add Folders Selection Frame
        folders_frame = ttk.LabelFrame(parent, text="Available Folders", padding="10")
        folders_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Configure folders frame for expansion
        folders_frame.grid_columnconfigure(0, weight=1)
        folders_frame.grid_rowconfigure(0, weight=1)
        
        # Create listbox for Drive folders with scrollbar
        self.folders_listbox = tk.Listbox(
            folders_frame, 
            selectmode=tk.SINGLE,
            height=10,  # Increased height since we removed assets listbox
            width=50
        )
        self.folders_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # Add scrollbar for folders
        folders_scrollbar = ttk.Scrollbar(folders_frame, orient=tk.VERTICAL, command=self.folders_listbox.yview)
        folders_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.folders_listbox.configure(yscrollcommand=folders_scrollbar.set)

        # Initially disable listbox
        self.folders_listbox.config(state='disabled')

    def update_progress(self):
        # Enable next button if all files are loaded
        if all(self.files_loaded.values()):
            self.next_button.config(state='normal')

    def show_error(self, title, message):
        CopyableMessageDialog(self.root, title, message, error=True)
        
    def show_info(self, title, message):
        CopyableMessageDialog(self.root, title, message, error=False)
        
    def show_warning(self, title, message):
        CopyableMessageDialog(self.root, title, message, error=False)

    def load_auth(self):
        auth_path = filedialog.askopenfilename(
            title="Select Google Cloud Auth File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if auth_path:
            try:
                # Update status for file selection
                self.update_status(f"Selected auth file: {Path(auth_path).name}")
                
                # First validate the JSON structure
                from utils.auth_validator import validate_auth_file, check_auth_file
                validate_auth_file(auth_path)
                
                # Update status for validation
                self.update_status("Validating authentication and checking access...")
                
                # Then check Drive and EE access
                if check_auth_file(auth_path):
                    if self.file_manager.load_auth_file(auth_path):
                        self.auth_filename.config(text=Path(auth_path).name)
                        self.files_loaded['auth'] = True
                        self.config_button.config(state='normal')
                        
                        # Update status for folder loading
                        self.update_status("Loading available folders from Google Drive...")
                        
                        # Update available folders
                        self.update_available_folders()
                        
                        self.update_progress()
                        self.update_status("Authentication complete - folders loaded successfully")
                    else:
                        self.update_status("Error: Failed to store authentication file")
                        self.show_error("Error", "Failed to store authentication file")
                else:
                    self.update_status("Error: Failed to validate access")
                    self.show_error("Error", "Failed to validate Google Drive or Earth Engine access")
            except ValueError as e:
                self.update_status(f"Error: {str(e)}")
                self.show_error("Error", str(e))
            except Exception as e:
                self.update_status(f"Error: Unexpected error during authentication")
                self.show_error("Error", f"Unexpected error during authentication: {str(e)}")

    def update_available_folders(self):
        try:
            # Clear existing items
            self.folders_listbox.delete(0, tk.END)
            
            # Enable listbox
            self.folders_listbox.config(state='normal')
            
            if not self.file_manager.input_files or not self.file_manager.input_files.auth_file:
                raise ValueError("Auth file not loaded in file manager")
                
            # Update status
            self.update_status("Retrieving folders...")
            
            # Get available folders from Google Drive
            from utils.auth_validator import return_all_folders_with_id
            auth_file_path = str(self.file_manager.input_files.auth_file)
            
            # Load Drive folders
            self.available_folders = return_all_folders_with_id(auth_file_path)
            for folder in self.available_folders:
                self.folders_listbox.insert(tk.END, folder)
            
            # Check folders
            if not self.available_folders:
                self.update_status("Warning: No Drive folders found")
                self.show_warning("Warning", "No Google Drive folders found")
            else:
                self.update_status("Folders loaded successfully")
                
        except Exception as e:
            self.update_status(f"Error: Failed to load folders")
            self.show_error("Error", f"Failed to load folders: {str(e)}")
            self.folders_listbox.config(state='disabled')

    def get_selected_folders(self):
        # Get selected folder
        folder_selection = self.folders_listbox.curselection()
        
        if folder_selection:
            return [self.available_folders[folder_selection[0]]]
        return []

    def load_config(self):
        config_path = filedialog.askopenfilename(
            title="Select Config File",
            filetypes=[("YAML files", "*.yaml"), ("All files", "*.*")]
        )
        if config_path:
            if validate_config(config_path):
                if self.file_manager.load_config(config_path):
                    self.config_filename.config(text=Path(config_path).name)
                    self.files_loaded['config'] = True
                    self.target_button.config(state='normal')
                    self.update_progress()
                    self.show_info("Success", "Configuration loaded successfully")
                else:
                    self.show_error("Error", "Failed to load configuration")

    def load_target(self):
        target_path = filedialog.askopenfilename(
            title="Select Target Index List",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if target_path:
            if self.file_manager.load_target_list(target_path):
                self.target_filename.config(text=Path(target_path).name)
                self.files_loaded['target'] = True
                self.update_progress()
                self.show_info("Success", "Target list loaded successfully")
            else:
                self.show_error("Error", "Failed to load target list")

    def proceed_to_next_step(self):
        # Check if folders are selected
        selected_folders = self.get_selected_folders()
        if not selected_folders:
            self.show_warning("Warning", "Please select at least one folder")
            return
            
        # Store selected folders in file_manager for later use
        self.file_manager.selected_folders = selected_folders
        
        self.show_info("Next Step", f"Selected folders: {', '.join(selected_folders)}\nProceeding to export settings...")
        # TODO: Implement transition to export settings screen

    def run(self):
        self.root.mainloop()

def main():
    app = Application()
    app.run()

if __name__ == "__main__":
    main() 