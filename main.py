from pathlib import Path
from utils.file_manager import FileManager
from utils.config_validator import validate_config
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from utils.config import config, Config
from utils.gee_helper import return_assets_size
import tkcalendar
from datetime import datetime








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
        self.config = config
        self.files_loaded = {
            'auth': False,
            'config': False,
            'target': False
        }
        self.available_folders = []
        self.setup_gui()

    def setup_gui(self):
        self.root.title("GEE Export UI")
        self.root.geometry("2048x1152")

        # Create main frame with two columns
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure columns to split the window
        main_frame.columnconfigure(0, weight=2)  # Left side (existing UI)
        main_frame.columnconfigure(1, weight=1)  # Right side (log frame)

        # Left Frame for existing UI
        left_frame = ttk.Frame(main_frame)
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Setup existing UI elements in left frame
        self.setup_file_loading_section(left_frame)

        # Right Frame for logs - made larger
        log_frame = ttk.LabelFrame(main_frame, text="Export Progress Log", padding="20")
        log_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(20, 0), pady=20, ipadx=20, ipady=20)
        
        # Configure log frame
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Add text widget for logs
        self.log_text = tk.Text(
            log_frame,
            wrap=tk.WORD,
            height=40,
            width=100,  # Doubled from 50 to 100
            state='disabled'
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Add scrollbar for log text
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        log_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.log_text.configure(yscrollcommand=log_scrollbar.set)

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

    # Update the status bar
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
            width=50,
            exportselection=0
        )
        self.folders_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # Add scrollbar for folders
        folders_scrollbar = ttk.Scrollbar(folders_frame, orient=tk.VERTICAL, command=self.folders_listbox.yview)
        folders_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.folders_listbox.configure(yscrollcommand=folders_scrollbar.set)

        # Initially disable listbox
        self.folders_listbox.config(state='disabled')

        # Add Source Information Frame
        source_info_frame = ttk.LabelFrame(parent, text="Source Information", padding="10")
        source_info_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Configure source info frame
        source_info_frame.columnconfigure(1, weight=1)
        source_info_frame.rowconfigure(1, weight=1)

        # Source Options List
        ttk.Label(source_info_frame, text="Available Sources:").grid(row=0, column=0, sticky=tk.W, padx=5)
        
        # Create listbox for sources with scrollbar
        self.sources_listbox = tk.Listbox(
            source_info_frame,
            selectmode=tk.SINGLE,
            height=3,
            width=30,
            exportselection=0
        )
        self.sources_listbox.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # Add scrollbar for sources
        sources_scrollbar = ttk.Scrollbar(source_info_frame, orient=tk.VERTICAL, command=self.sources_listbox.yview)
        sources_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.sources_listbox.configure(yscrollcommand=sources_scrollbar.set)
        
        # Source Details Text Area
        ttk.Label(source_info_frame, text="Source Details:").grid(row=0, column=2, sticky=tk.W, padx=5)
        
        self.source_info_text = tk.Text(
            source_info_frame,
            wrap=tk.WORD,
            height=6,
            width=50
        )
        self.source_info_text.grid(row=1, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # Add scrollbar for text area
        text_scrollbar = ttk.Scrollbar(source_info_frame, orient=tk.VERTICAL, command=self.source_info_text.yview)
        text_scrollbar.grid(row=1, column=3, sticky=(tk.N, tk.S))
        self.source_info_text.configure(yscrollcommand=text_scrollbar.set)
        
        # Make text read-only
        self.source_info_text.config(state='disabled')
        
        # Bind selection event
        self.sources_listbox.bind('<<ListboxSelect>>', self.on_source_select)

        # Add Shared Asset Information Frame below Source Information
        shared_asset_frame = ttk.LabelFrame(parent, text="Shared Asset Information", padding="10")
        shared_asset_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Configure shared asset frame
        shared_asset_frame.columnconfigure(0, weight=1)
        
        # Create text widget for shared asset info
        self.shared_asset_text = tk.Text(
            shared_asset_frame,
            wrap=tk.WORD,
            height=3,
            width=50,
            state='disabled'
        )
        self.shared_asset_text.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)

        # Add Target Comparison Results Frame
        target_comparison_frame = ttk.LabelFrame(parent, text="Target Comparison Results", padding="10")
        target_comparison_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Configure target comparison frame
        target_comparison_frame.columnconfigure(0, weight=1)
        
        # Create text widget for comparison results
        self.target_comparison_text = tk.Text(
            target_comparison_frame,
            wrap=tk.WORD,
            height=4,
            width=50,
            state='disabled'
        )
        self.target_comparison_text.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)

        # Add Time Selection Frame
        time_frame = ttk.LabelFrame(parent, text="Export Date Range", padding="10")
        time_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Start Date Row
        ttk.Label(time_frame, text="Start Date:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.start_date = ttk.Entry(time_frame, width=12)
        self.start_date.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(time_frame, text="Select Date", command=lambda: self.pick_date(self.start_date)).grid(
            row=0, column=2, padx=5, pady=5
        )
        
        # End Date Row
        ttk.Label(time_frame, text="End Date:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.end_date = ttk.Entry(time_frame, width=12)
        self.end_date.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(time_frame, text="Select Date", command=lambda: self.pick_date(self.end_date)).grid(
            row=1, column=2, padx=5, pady=5
        )

        # Start Export Button (moved to row 6)
        self.next_button = ttk.Button(
            parent, 
            text="Start to Export",
            command=self.proceed_to_next_step,
            state='disabled'
        )
        self.next_button.grid(row=6, column=0, columnspan=3, pady=20, sticky=(tk.E, tk.W))

    def pick_date(self, entry_widget):
        """Show date picker and update entry"""
        def set_date():
            date = cal.selection_get()
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, date.strftime('%Y-%m-%d'))
            top.destroy()

        top = tk.Toplevel(self.root)
        top.title("Select Date")
        
        # Make dialog modal
        top.transient(self.root)
        top.grab_set()
        
        # Add calendar
        cal = tkcalendar.Calendar(top,
                                 selectmode='day',
                                 date_pattern='y-mm-dd')
        cal.pack(padx=10, pady=10)
        
        # Add OK button
        ttk.Button(top, text="OK", command=set_date).pack(pady=5)
        
        # Center the dialog
        self.center_dialog(top)

    def update_source_list(self):
        """Update the source list from YAML configuration"""
        try:
            self.sources_listbox.delete(0, tk.END)
            
            if self.config and self.config.yaml_config and 'image_sources' in self.config.yaml_config:
                sources = self.config.get_image_sources()
                for source_type, source_info in sources.items():
                    source_name = source_info.get('source_name', source_type.upper())
                    self.sources_listbox.insert(tk.END, source_name)
                    
                # Select first source by default
                if self.sources_listbox.size() > 0:
                    self.sources_listbox.selection_set(0)
                    self.on_source_select(None)
                    
        except Exception as e:
            self.show_error("Error", f"Failed to update source list: {str(e)}")

    def on_source_select(self, event):
        """Handle source selection event"""
        try:
            selection = self.sources_listbox.curselection()
            if not selection:
                return
            
            # Get selected source type
            source_name = self.sources_listbox.get(selection[0])
            sources = self.config.get_image_sources()
            
            # Find source info by name
            source_info = None
            source_type = None
            for s_type, s_info in sources.items():
                if s_info.get('source_name') == source_name:
                    source_info = s_info
                    source_type = s_type
                    break
                    
            if source_info:
                # Update text area with source details
                self.source_info_text.config(state='normal')
                self.source_info_text.delete(1.0, tk.END)
                
                info_text = f"Source Type: {source_type.upper()}\n"
                info_text += f"Name: {self.config.get_source_name(source_type)}\n"
                info_text += f"Project Path: {self.config.get_project_path(source_type)}\n"
                info_text += f"Scale: {self.config.get_scale_meters(source_type)} meters\n"
                
                self.source_info_text.insert(tk.END, info_text)
                self.source_info_text.config(state='disabled')
                
        except Exception as e:
            self.show_error("Error", f"Failed to update source information: {str(e)}")

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
        """Update available folders from Google Drive"""
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
            
            # Store folder info as dictionary for easy lookup
            self.folder_info = {}
            for folder_with_id in self.available_folders:
                # Split folder name and ID
                folder_name = folder_with_id.split(" (")[0]
                self.folder_info[folder_name] = folder_with_id
                # Display only folder name in listbox
                self.folders_listbox.insert(tk.END, folder_name)
            
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
            try:
                from utils.config_validator import validate_config
                from utils.gee_helper import return_assets_size
                
                # Validate configuration file
                is_valid, error_message, yaml_content = validate_config(config_path)
                
                if not is_valid:
                    raise ValueError(error_message)
                
                # Load the config file into the config instance
                self.config = Config.load_from_yaml(config_path)
                
                # Update UI
                self.config_filename.config(text=Path(config_path).name)
                self.files_loaded['config'] = True
                self.target_button.config(state='normal')
                
                # Update source list and information
                self.update_source_list()
                
                # Update shared asset information
                self.update_shared_asset_info()
                
                # Update progress
                self.update_progress()
                self.update_status("Configuration loaded successfully")
                
            except Exception as e:
                self.show_error("Configuration Error", str(e))
                self.config_filename.config(text="No file selected")
                self.files_loaded['config'] = False
                self.target_button.config(state='disabled')

    def update_shared_asset_info(self):
        """Update shared asset information display"""
        self.update_status("Updating shared asset information...")
        try:
            if not self.file_manager.input_files or not self.file_manager.input_files.auth_file:
                return
            
            shared_asset_id = self.config.get_shared_assets_id()
            if not shared_asset_id:
                return
            
            # Get asset size using GEE helper
            auth_file_path = str(self.file_manager.input_files.auth_file)
            asset_size = return_assets_size(auth_file_path, shared_asset_id)
            
            # Update text widget with asset information
            self.shared_asset_text.config(state='normal')
            self.shared_asset_text.delete(1.0, tk.END)
            
            info_text = f"Shared Asset ID: {shared_asset_id}\n"
            info_text += f"Number of Features: {asset_size}\n"
            
            self.shared_asset_text.insert(tk.END, info_text)
            self.shared_asset_text.config(state='disabled')
            
            self.update_status("Shared asset information updated successfully")
            
        except Exception as e:
            self.show_error("Error", f"Failed to update shared asset information: {str(e)}")
            self.shared_asset_text.config(state='normal')
            self.shared_asset_text.delete(1.0, tk.END)
            self.shared_asset_text.insert(tk.END, "Failed to load shared asset information")
            self.shared_asset_text.config(state='disabled')



    def update_source_info(self):
        # Update source information display
        self.source_info_text.delete(1.0, tk.END)
        self.source_info_text.insert(tk.END, self.config.get_source_info_str())

        



    def load_target(self):
        target_path = filedialog.askopenfilename(
            title="Select Target Index List",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if target_path:
            try:
                # Update status
                self.update_status("Loading target list...")
                
                if self.file_manager.load_target_list(target_path):
                    self.target_filename.config(text=Path(target_path).name)
                    self.files_loaded['target'] = True
                    self.update_progress()
                    
                    # Get shared asset ID from config
                    shared_asset_id = self.config.get_shared_assets_id()
                    if not shared_asset_id:
                        raise ValueError("No shared asset ID found in config")
                    
                    # Update status
                    self.update_status("Comparing target list with shared asset...")
                    
                    # Get auth file path
                    auth_file_path = str(self.file_manager.input_files.auth_file)
                    
                    # Show loading message in comparison text
                    self.target_comparison_text.config(state='normal')
                    self.target_comparison_text.delete(1.0, tk.END)
                    self.target_comparison_text.insert(tk.END, "Comparing target list with shared asset...")
                    self.target_comparison_text.config(state='disabled')
                    
                    # Compare target with shared asset
                    from utils.gee_helper import compare_target_asset
                    comparison_result = compare_target_asset(
                        auth_file_path,
                        target_path,
                        shared_asset_id
                    )
                    
                    # Update comparison results
                    self.target_comparison_text.config(state='normal')
                    self.target_comparison_text.delete(1.0, tk.END)
                    self.target_comparison_text.insert(tk.END, comparison_result)
                    self.target_comparison_text.config(state='disabled')
                    
                    self.update_status("Target list loaded and compared successfully")

                    self.files_loaded['target'] = True
                    self.update_progress()
                    
                else:
                    raise ValueError("Failed to load target list")
                    
            except Exception as e:
                self.show_error("Error", str(e))
                self.target_filename.config(text="No file selected")
                self.files_loaded['target'] = False
                
                # Clear comparison results
                self.target_comparison_text.config(state='normal')
                self.target_comparison_text.delete(1.0, tk.END)
                self.target_comparison_text.insert(tk.END, "Failed to compare target list")
                self.target_comparison_text.config(state='disabled')



    def check_export_conditions(self):
        """
        Check if all conditions are satisfied to start the export
        Returns:
            bool: True if all conditions are met, False otherwise
        """
        try:
            # 1. Check if a folder is selected
            folder_selection = self.folders_listbox.curselection()
            if not folder_selection:
                self.show_error("Export Error", "Please select a destination folder from the available folders list")
                return False

            # 2. Check if a source is selected
            source_selection = self.sources_listbox.curselection()
            if not source_selection:
                self.show_error("Export Error", "Please select an image source from the available sources list")
                return False

            # 3. Check target comparison results
            comparison_text = self.target_comparison_text.get(1.0, tk.END).strip()
            if not comparison_text:
                self.show_error("Export Error", "No target comparison results available")
                return False

            # Parse the comparison results to get the match count
            try:
                # Extract the number of matches from the comparison text
                # Expected format: "Number of target values found in shared asset: X"
                for line in comparison_text.split('\n'):
                    if "found in shared asset:" in line:
                        match_count = int(line.split(':')[1].strip())
                        if match_count <= 0:
                            self.show_error("Export Error", 
                                "No matching features found between target list and shared asset")
                            return False
                        break
            except (ValueError, IndexError):
                self.show_error("Export Error", 
                    "Unable to determine the number of matching features")
                return False

            # 4. Check date selections
            start_date_str = self.start_date.get().strip()
            end_date_str = self.end_date.get().strip()

            # Check if dates are provided
            if not start_date_str or not end_date_str:
                self.show_error("Export Error", "Please select both start and end dates")
                return False

            try:
                from datetime import datetime
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

                # Check if dates are first day of month
                if start_date.day != 1:
                    self.show_error("Export Error", 
                        "Start date must be the first day of the month")
                    return False

                if end_date.day != 1:
                    self.show_error("Export Error", 
                        "End date must be the first day of the month")
                    return False

                # Check if end date is after start date
                if end_date <= start_date:
                    self.show_error("Export Error", 
                        "End date must be after start date")
                    return False

            except ValueError:
                self.show_error("Export Error", 
                    "Invalid date format. Please use YYYY-MM-DD format")
                return False

            # All conditions are satisfied
            print("All conditions are satisfied")
            return True

        except Exception as e:
            self.show_error("Export Error", f"Error checking export conditions: {str(e)}")
            return False











    

    def proceed_to_next_step(self):
        if self.check_export_conditions():
            try:
                # Get selected source type
                source_selection = self.sources_listbox.curselection()
                source_name = self.sources_listbox.get(source_selection[0])
                
                # Find source type from config based on source name
                source_type = None
                for s_type, s_info in self.config.get_image_sources().items():
                    if s_info.get('source_name') == source_name:
                        source_type = s_type
                        break
                
                if not source_type:
                    raise ValueError("Could not determine source type")

                # Get selected folder name only
                folder_selection = self.folders_listbox.curselection()
                folder_name = self.folders_listbox.get(folder_selection[0])  # This now gets just the name
                
                # Get full folder info for logging (optional)
                folder_with_id = self.folder_info.get(folder_name, folder_name)

                # Update log with full folder information
                self.update_log(f"Selected export folder: {folder_with_id}")
                
                # Get date range
                start_date = self.start_date.get().strip()
                end_date = self.end_date.get().strip()

                # Load and parse target indices from CSV file



                target_indices = self.file_manager.get_target_indices()
                
                if not target_indices:
                    raise ValueError("No target indices found in the CSV file")
                
                # Get auth file path (convert WindowsPath to string)
                auth_file = str(self.file_manager.input_files.auth_file)

                print(f"Initializing TifDownloader with parameters:")
                print(f"  config: {self.config}")
                print(f"  auth_file: {auth_file}")
                print(f"  target_indices: {target_indices}")
                print("--------------------------------")

                # Update status and log
                self.update_status(f"Initializing export for {source_type} imagery...")
                self.update_log(f"Starting export process for {source_type}")
                self.update_log(f"Date range: {start_date} to {end_date}")
                self.update_log(f"Target folder: {folder_name}")
                self.update_log(f"Number of indices: {len(target_indices)}")

                # Create TifDownloader instance with clean folder name
                from utils.tif_downloader import TifDownloader
                downloader = TifDownloader(
                    config=self.config,
                    auth_file=auth_file,
                    target_indices=target_indices,
                    start_date=start_date,
                    end_date=end_date,
                    source_type=source_type,
                    log_callback=self.update_log
                )

                # Initialize Earth Engine
                self.update_log("Initializing Earth Engine...")
                downloader.initialize_ee()

                # Start export in a separate thread
                import threading
                def export_thread():
                    try:
                        downloader.start_export(
                            start_date=start_date,
                            end_date=end_date,
                            source_type=source_type,
                            folder_name=folder_name,
                        )
                        self.update_status("Export completed successfully")
                        self.update_log("Export process has been completed successfully!")
                    except Exception as e:
                        self.update_status("Export failed")
                        self.update_log(f"Export failed: {str(e)}")
                        self.show_error("Export Error", str(e))

                thread = threading.Thread(target=export_thread)
                thread.daemon = True
                thread.start()

            except Exception as e:
                self.show_error("Export Error", f"Failed to start export: {str(e)}")
                self.update_status("Export failed to start")
                self.update_log(f"Failed to start export: {str(e)}")
        else:
            self.update_status("Export conditions not met")
            self.update_log("Export conditions not met - please check all requirements")

    # Add a new method to update the log
    def update_log(self, message):
        """Update the log text widget with a new message"""
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
        self.log_text.see(tk.END)  # Scroll to bottom
        self.log_text.config(state='disabled')

    def run(self):
        self.root.mainloop()

    def center_dialog(self, dialog):
        """Center the dialog window on the parent"""
        dialog.update_idletasks()
        
        # Get the window sizes and positions
        dw = dialog.winfo_reqwidth()
        dh = dialog.winfo_reqheight()
        pw = self.root.winfo_width()
        ph = self.root.winfo_height()
        px = self.root.winfo_rootx()
        py = self.root.winfo_rooty()
        
        # Calculate center position
        x = px + (pw - dw) // 2
        y = py + (ph - dh) // 2
        
        # Set the dialog position
        dialog.geometry(f"+{x}+{y}")







def main():
    app = Application()
    app.run()

if __name__ == "__main__":
    main() 