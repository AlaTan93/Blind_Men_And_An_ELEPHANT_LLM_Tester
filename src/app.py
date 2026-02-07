"""Main application class for LLM Tester."""
import customtkinter as ctk

from .llm_tab import LLMMainTab
from .api_key_tab import APIKeyTab
from .about_tab import AboutTab


class LLMTesterApp(ctk.CTk):
    """Main application window for LLM Tester."""

    def __init__(self):
        """Initialize the application."""
        super().__init__()

        # Configure window
        self.title("LLM Tester - Blind Men and an Elephant")
        self.geometry("1200x800")

        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Create tabview
        self.tabview = ctk.CTkTabview(self, width=1180, height=780)
        self.tabview.pack(padx=10, pady=10, fill="both", expand=True)

        # Add tabs
        self.tabview.add("Main")
        self.tabview.add("Options")
        self.tabview.add("About")

        # Setup each tab with its respective module
        self.main_tab = LLMMainTab(self.tabview.tab("Main"))
        self.options_tab = APIKeyTab(self.tabview.tab("Options"))
        self.about_tab = AboutTab(self.tabview.tab("About"))
