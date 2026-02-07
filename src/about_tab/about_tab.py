"""About tab displaying application information."""
import customtkinter as ctk
import webbrowser
import subprocess
import sys
from tkinter import messagebox


class AboutTab:
    """Handles the About tab functionality."""

    def __init__(self, parent):
        """Initialize the About tab.

        Args:
            parent: The parent tabview widget
        """
        self.parent = parent
        self.setup_ui()

    def open_url(self, url):
        """Open URL in browser with cross-platform support.

        Args:
            url: The URL to open
        """
        try:
            if sys.platform == "linux":
                # Use xdg-open on Linux for better compatibility
                subprocess.Popen(["xdg-open", url])
            else:
                # Use webbrowser for Windows and macOS
                webbrowser.open(url)
        except Exception as e:
            messagebox.showwarning("Web browser cannot be opened")

    def setup_ui(self):
        """Setup the about tab UI."""
        # Container frame
        about_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        about_frame.pack(expand=True, fill="both", padx=50, pady=50)

        # Title
        title_label = ctk.CTkLabel(about_frame,
                                   text="LLM Tester",
                                   font=("Arial", 28, "bold"))
        title_label.pack(pady=20)

        # Subtitle
        subtitle_label = ctk.CTkLabel(about_frame,
                                     text="Blind Men and an Elephant",
                                     font=("Arial", 18))
        subtitle_label.pack(pady=10)

        # Version
        version_label = ctk.CTkLabel(about_frame,
                                    text="Version 0.1.0",
                                    font=("Arial", 14))
        version_label.pack(pady=10)

        # Description - Part 1
        description_text_1 = """
        This application allows you to test and compare responses
        from multiple Large Language Models (LLMs) simultaneously.

        The name references the parable of the blind men and an elephant,
        and the paper titled: ELEPHANT: Measuring and understanding social sycophancy in LLMs"""

        description_label_1 = ctk.CTkLabel(about_frame,
                                          text=description_text_1,
                                          font=("Arial", 12),
                                          justify="center")
        description_label_1.pack(pady=(10, 0))

        # Clickable URL
        url = "https://arxiv.org/abs/2505.13995v2"
        url_label = ctk.CTkLabel(about_frame,
                                 text=url,
                                 font=("Arial", 12, "underline"),
                                 text_color="#1f6aa5",
                                 cursor="hand2")
        url_label.pack(pady=5)
        url_label.bind("<Button-1>", lambda e: self.open_url(url))

        # Footer
        footer_label = ctk.CTkLabel(about_frame,
                                   text="Built with Python 3.13 and CustomTkinter",
                                   font=("Arial", 10),
                                   text_color="gray")
        footer_label.pack(side="bottom", pady=10)
