"""Options tab for managing API keys."""
import os

import customtkinter as ctk
import yaml
from tkinter import messagebox

from src.logger import get_logger

logger = get_logger(__name__)

api_keys = {
    "openai": "",            
    "azure": "",
    "azure_endpoint": "",
    "azure_api_ver": "",
    "claude": ""
}


class APIKeyTab:
    """Handles the API key configuration tab functionality."""

    def __init__(self, parent):
        """Initialize the API key tab.

        Args:
            parent: The parent tabview widget
        """
        self.parent = parent
        
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
        self.create_entry_field(api_frame, "OpenAI API Key:", "openai", 0)

        # Claude API Key
        self.create_entry_field(api_frame, "Claude API Key:", "claude", 1)

        # Save button
        save_btn = ctk.CTkButton(self.parent, text="Save API Keys",
                                command=self.save_api_keys,
                                font=("Arial", 14), height=40)
        save_btn.pack(pady=20)


    def create_entry_field(self, parent, label_text, key_name, row, placeholder_text="Enter API key here...", show_hide_button = True):
        """Create an entry field with show/hide functionality.

        Args:
            parent: The parent frame widget
            label_text: Label text for the field
            key_name: Key name in the api_keys dictionary
            row: Grid row position
        """
        # Label
        label = ctk.CTkLabel(parent, text=label_text, font=("Calibri", 15, "bold"))
        label.grid(row=row, column=0, pady=15, padx=20, sticky="w")

        # Entry field (password style)
        entry = ctk.CTkEntry(parent, placeholder_text=placeholder_text,
                            show="*", width=400, height=35, font=("Calibri", 15))
        entry.grid(row=row, column=1, pady=15, padx=10, sticky="ew")
        entry.insert(0, api_keys[key_name])

        # Show/Hide button
        if show_hide_button:
            show_var = ctk.BooleanVar(value=False)

            def toggle_visibility():
                show_var.set(not show_var.get())
                if show_var.get():
                    entry.configure(show="")
                    show_btn.configure(text="Hide")
                else:
                    entry.configure(show="*")
                    show_btn.configure(text="Show")

            show_btn = ctk.CTkButton(parent, text="Show", command=toggle_visibility, width=80)
            show_btn.grid(row=row, column=2, pady=15, padx=10)

        # Store reference
        setattr(self, f"{key_name}_entry", entry)

        # Configure grid weights
        parent.grid_columnconfigure(1, weight=1)


    def save_api_keys(self):
        """Save API keys to config.yaml file."""
        api_keys["openai"] = self.openai_entry.get() # type: ignore
        api_keys["azure"] = self.azure_entry.get() # type: ignore
        api_keys["claude"] = self.claude_entry.get() # type:ignore

        config_file = self._get_config_path()
        try:
            config = {
                "api_keys": {
                    "openai": api_keys["openai"],
                    "azure": api_keys["azure"],
                    "claude": api_keys["claude"],
                }
            }
            with open(config_file, "w") as f:
                yaml.dump(config, f, default_flow_style=False)
            messagebox.showinfo("Success", "API keys saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save API keys: {str(e)}")


    def load_api_keys(self):
        """Load API keys from config.yaml file."""
        config_file = self._get_config_path()
        if os.path.exists(config_file):
            try:
                with open(config_file, "r") as f:
                    config = yaml.safe_load(f) or {}
                keys = config.get("api_keys", {})
                api_keys["openai"] = keys.get("openai", "") # type: ignore
                api_keys["azure"] = keys.get("azure", "") # type: ignore
                api_keys["claude"] = keys.get("claude", "") # type: ignore
                logger.info("API keys loaded from %s", config_file)
            except Exception as e:
                logger.error("Failed to load API keys: %s", e)
        else:
            logger.warning("No config.yaml file found at %s", config_file)


    def _get_config_path(self):
        """Get the path to the config.yaml file.

        Returns:
            str: Path to config.yaml in project root
        """
        # Go up from src/api_key_tab/ to project root
        return os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "config.yaml"
        )
