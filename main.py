from pathlib import Path
from utils.file_manager import FileManager
from utils.config_validator import validate_config
import tkinter as tk
from tkinter import filedialog, messagebox

class Application:
    def __init__(self):
        self.file_manager = FileManager()
        self.setup_gui()

    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("GEE Export UI")
        self.root.geometry("600x400")

        # File loading buttons
        tk.Button(self.root, text="Load Config", command=self.load_config).pack(pady=10)
        tk.Button(self.root, text="Load Auth File", command=self.load_auth).pack(pady=10)
        tk.Button(self.root, text="Load Target List", command=self.load_target).pack(pady=10)

        # Status labels
        self.config_status = tk.Label(self.root, text="Config: Not loaded")
        self.config_status.pack()
        self.auth_status = tk.Label(self.root, text="Auth: Not loaded")
        self.auth_status.pack()
        self.target_status = tk.Label(self.root, text="Target List: Not loaded")
        self.target_status.pack()

    def load_config(self):
        config_path = filedialog.askopenfilename(
            title="Select Config File",
            filetypes=[("YAML files", "*.yaml"), ("All files", "*.*")]
        )
        if config_path:
            if validate_config(config_path):
                if self.file_manager.load_config(config_path):
                    self.config_status.config(text="Config: Loaded ✓")
                    messagebox.showinfo("Success", "Configuration loaded successfully")
                else:
                    messagebox.showerror("Error", "Failed to load configuration")

    def load_auth(self):
        auth_path = filedialog.askopenfilename(
            title="Select Auth File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if auth_path:
            if self.file_manager.load_auth_file(auth_path):
                self.auth_status.config(text="Auth: Loaded ✓")
                messagebox.showinfo("Success", "Authentication file loaded successfully")
            else:
                messagebox.showerror("Error", "Failed to load authentication file")

    def load_target(self):
        target_path = filedialog.askopenfilename(
            title="Select Target List",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if target_path:
            if self.file_manager.load_target_list(target_path):
                self.target_status.config(text="Target List: Loaded ✓")
                messagebox.showinfo("Success", "Target list loaded successfully")
            else:
                messagebox.showerror("Error", "Failed to load target list")

    def run(self):
        self.root.mainloop()

def main():
    app = Application()
    app.run()

if __name__ == "__main__":
    main() 