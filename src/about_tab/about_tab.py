"""About tab displaying application information."""
import customtkinter as ctk


class AboutTab:
    """Handles the About tab functionality."""

    def __init__(self, parent):
        """Initialize the About tab.

        Args:
            parent: The parent tabview widget
        """
        self.parent = parent
        self.setup_ui()

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

        # Description
        description_text = """
        This application allows you to test and compare responses
        from multiple Large Language Models (LLMs) simultaneously.

        The name references the parable of the blind men and an elephant,
        where each person perceives only part of the truth.
        Similarly, different LLMs may provide different perspectives
        on the same prompt.

        Features:
        • Compare up to 10 LLM responses side-by-side
        • Configurable model parameters
        • Secure API key management
        • Cross-platform compatibility
        """

        description_label = ctk.CTkLabel(about_frame,
                                        text=description_text,
                                        font=("Arial", 12),
                                        justify="center")
        description_label.pack(pady=30)

        # Footer
        footer_label = ctk.CTkLabel(about_frame,
                                   text="Built with Python 3.13 and CustomTkinter",
                                   font=("Arial", 10),
                                   text_color="gray")
        footer_label.pack(side="bottom", pady=10)
