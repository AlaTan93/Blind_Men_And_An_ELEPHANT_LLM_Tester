"""Options tab for managing API keys."""
import customtkinter as ctk
from tkinter import messagebox
import json
import os


class APIKeyTab:
    """Handles the API key configuration tab functionality."""

    def __init__(self, parent):
        """Initialize the API key tab.

        Args:
            parent: The parent tabview widget
        """
        self.parent = parent
        self.api_keys = {
            "openai": "",
            "azure": "",
            "claude": ""
        }
        self.load_api_keys()
        self.setup_ui()

    def setup_ui(self):
        """Setup the options tab UI with API key fields."""
        # Title
        title_label = ctk.CTkLabel(self.parent, text="API Keys Configuration",
                                   font=("Arial", 18, "bold"))
        title_label.pack(pady=20)

        # Container frame for API keys
        api_frame = ctk.CTkFrame(self.parent)
        api_frame.pack(pady=20, padx=50, fill="both", expand=True)

        # OpenAI API Key
        self.create_api_key_field(api_frame, "OpenAI API Key:", "openai", 0)

        # Azure API Key
        self.create_api_key_field(api_frame, "Azure API Key:", "azure", 1)

        # Claude API Key
        self.create_api_key_field(api_frame, "Claude API Key:", "claude", 2)

        # Save button
        save_btn = ctk.CTkButton(self.parent, text="Save API Keys",
                                command=self.save_api_keys,
                                font=("Arial", 14), height=40)
        save_btn.pack(pady=20)

    def create_api_key_field(self, parent, label_text, key_name, row):
        """Create an API key input field with show/hide functionality.

        Args:
            parent: The parent frame widget
            label_text: Label text for the field
            key_name: Key name in the api_keys dictionary
            row: Grid row position
        """
        # Label
        label = ctk.CTkLabel(parent, text=label_text, font=("Arial", 12, "bold"))
        label.grid(row=row, column=0, pady=15, padx=20, sticky="w")

        # Entry field (password style)
        entry = ctk.CTkEntry(parent, placeholder_text="Enter API key here...",
                            show="*", width=400, height=35, font=("Arial", 11))
        entry.grid(row=row, column=1, pady=15, padx=10, sticky="ew")
        entry.insert(0, self.api_keys[key_name])

        # Show/Hide button
        show_var = ctk.BooleanVar(value=False)

        def toggle_visibility():
            if show_var.get():
                entry.configure(show="")
                show_btn.configure(text="Hide")
            else:
                entry.configure(show="*")
                show_btn.configure(text="Show")
            show_var.set(not show_var.get())

        show_btn = ctk.CTkButton(parent, text="Show", command=toggle_visibility, width=80)
        show_btn.grid(row=row, column=2, pady=15, padx=10)

        # Store reference
        setattr(self, f"{key_name}_entry", entry)

        # Configure grid weights
        parent.grid_columnconfigure(1, weight=1)

    def save_api_keys(self):
        """Save API keys to file."""
        self.api_keys["openai"] = self.openai_entry.get()
        self.api_keys["azure"] = self.azure_entry.get()
        self.api_keys["claude"] = self.claude_entry.get()

        # Save to file in project root
        config_file = self._get_config_path()
        try:
            with open(config_file, "w") as f:
                json.dump(self.api_keys, f, indent=2)
            messagebox.showinfo("Success", "API keys saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save API keys: {str(e)}")

    def load_api_keys(self):
        """Load API keys from file."""
        config_file = self._get_config_path()
        if os.path.exists(config_file):
            try:
                with open(config_file, "r") as f:
                    self.api_keys = json.load(f)
            except Exception as e:
                print(f"Failed to load API keys: {str(e)}")

    def _get_config_path(self):
        """Get the path to the config file.

        Returns:
            str: Path to config.json in project root
        """
        # Go up from src/api_key_tab/ to project root
        return os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "config.json"
        )
