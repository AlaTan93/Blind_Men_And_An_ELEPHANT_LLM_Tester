"""Main tab with LLM prompt input and dynamic columns for model comparison."""
import customtkinter as ctk
from tkinter import messagebox


class LLMMainTab:
    """Handles the main tab functionality for LLM testing."""

    def __init__(self, parent):
        """Initialize the main tab.

        Args:
            parent: The parent tabview widget
        """
        self.parent = parent
        self.num_columns = 1
        self.max_columns = 10
        self.min_columns = 1
        self.column_frames = []

        self.setup_ui()

    def setup_ui(self):
        """Setup the main tab UI with prompt input and dynamic columns."""
        # Prompt input section
        prompt_label = ctk.CTkLabel(self.parent, text="LLM Prompt:", font=("Arial", 14, "bold"))
        prompt_label.pack(pady=(10, 5), anchor="w", padx=10)

        # Resizable text box for prompt
        self.prompt_textbox = ctk.CTkTextbox(self.parent, height=150, font=("Arial", 12))
        self.prompt_textbox.pack(pady=(0, 10), padx=10, fill="both")

        # Column control section
        control_frame = ctk.CTkFrame(self.parent)
        control_frame.pack(pady=10, padx=10, fill="x")

        columns_label = ctk.CTkLabel(control_frame, text=f"Columns: {self.num_columns}",
                                     font=("Arial", 12))
        columns_label.pack(side="left", padx=10)
        self.columns_label = columns_label

        add_column_btn = ctk.CTkButton(control_frame, text="+ Add Column",
                                       command=self.add_column, width=120)
        add_column_btn.pack(side="left", padx=5)

        remove_column_btn = ctk.CTkButton(control_frame, text="- Remove Column",
                                          command=self.remove_column, width=120)
        remove_column_btn.pack(side="left", padx=5)

        # Scrollable frame for columns
        self.columns_scroll_frame = ctk.CTkScrollableFrame(self.parent,
                                                           label_text="Response Columns")
        self.columns_scroll_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # Create initial column
        self.create_column(0)

        # Print data button at the bottom
        print_data_btn = ctk.CTkButton(self.parent, text="Print All Data to Console",
                                       command=self.print_all_data,
                                       font=("Arial", 12), height=40)
        print_data_btn.pack(pady=10, padx=10, fill="x")

    def create_column(self, index: int):
        """Create a single column with dropdowns and text box.

        Args:
            index: The column index (0-based)
        """
        # Define alternating border colors for visual differentiation
        border_colors = ["#1f538d", "#14a085", "#8e44ad", "#c0392b", "#d68910",
                        "#117864", "#6c3483", "#884ea0", "#1a5490", "#196f3d"]
        border_color = border_colors[index % len(border_colors)]

        # Column frame with colored border for differentiation
        column_frame = ctk.CTkFrame(self.columns_scroll_frame, border_width=3,
                                   border_color=border_color)
        column_frame.grid(row=0, column=index, padx=10, pady=10, sticky="nsew")

        # Configure grid weight for resizing
        self.columns_scroll_frame.grid_columnconfigure(index, weight=1, uniform="column")

        # Column header with color indicator
        header_label = ctk.CTkLabel(column_frame, text=f"Column {index + 1}",
                                    font=("Arial", 14, "bold"),
                                    text_color=border_color)
        header_label.pack(pady=10)

        # First dropdown
        dropdown1_label = ctk.CTkLabel(column_frame, text="Model:")
        dropdown1_label.pack(pady=(5, 2))

        dropdown1 = ctk.CTkComboBox(column_frame,
                                    values=["GPT-4", "GPT-3.5", "Claude-3", "Claude-2", "Other"],
                                    state="readonly")
        dropdown1.set("GPT-4")
        dropdown1.pack(pady=(0, 10), padx=10, fill="x")

        # Second dropdown
        dropdown2_label = ctk.CTkLabel(column_frame, text="Temperature:")
        dropdown2_label.pack(pady=(5, 2))

        dropdown2 = ctk.CTkComboBox(column_frame,
                                    values=["0.0", "0.5", "0.7", "1.0", "1.5"],
                                    state="readonly")
        dropdown2.set("0.7")
        dropdown2.pack(pady=(0, 10), padx=10, fill="x")

        # Response textbox (read-only but copyable)
        response_label = ctk.CTkLabel(column_frame, text="Response:")
        response_label.pack(pady=(5, 2))

        response_textbox = ctk.CTkTextbox(column_frame, height=300, font=("Arial", 11))
        response_textbox.pack(pady=(0, 10), padx=10, fill="both", expand=True)

        # Insert placeholder text
        response_textbox.insert("1.0",
                               f"Response from model will appear here...\n\n"
                               f"(This textbox is read-only but you can copy text from it)")

        # Store reference
        self.column_frames.append({
            "frame": column_frame,
            "dropdown1": dropdown1,
            "dropdown2": dropdown2,
            "response": response_textbox,
            "index": index
        })

    def add_column(self):
        """Add a new column."""
        if self.num_columns < self.max_columns:
            self.num_columns += 1
            self.create_column(self.num_columns - 1)
            self.columns_label.configure(text=f"Columns: {self.num_columns}")
            self._reconfigure_column_grid()
        else:
            messagebox.showwarning("Maximum Columns",
                                  f"Maximum of {self.max_columns} columns allowed.")

    def remove_column(self):
        """Remove the last column."""
        if self.num_columns > self.min_columns:
            last_column = self.column_frames.pop()
            last_column["frame"].destroy()
            self.num_columns -= 1
            self.columns_label.configure(text=f"Columns: {self.num_columns}")
            self._reconfigure_column_grid()
        else:
            messagebox.showwarning("Minimum Columns",
                                  f"Minimum of {self.min_columns} column required.")

    def _reconfigure_column_grid(self):
        """Reconfigure grid weights to ensure columns resize properly."""
        # Reset all column weights and clear uniform groups
        for i in range(self.max_columns):
            self.columns_scroll_frame.grid_columnconfigure(i, weight=0, uniform="")
        # Set weights only for active columns
        for i in range(self.num_columns):
            self.columns_scroll_frame.grid_columnconfigure(i, weight=1, uniform="column")

    def print_all_data(self):
        """Print all data from the main tab to console."""
        print("\n" + "="*80)
        print("LLM TESTER - DATA DUMP")
        print("="*80)

        # Print prompt
        prompt_text = self.prompt_textbox.get("1.0", "end-1c")
        print(f"\nPROMPT:")
        print(f"{'-'*80}")
        print(prompt_text)
        print(f"{'-'*80}\n")

        # Print data for each column
        for i, column_data in enumerate(self.column_frames, 1):
            print(f"\nCOLUMN {i}:")
            print(f"{'-'*80}")
            print(f"  Model: {column_data['dropdown1'].get()}")
            print(f"  Temperature: {column_data['dropdown2'].get()}")
            print(f"  Response:")
            response_text = column_data['response'].get("1.0", "end-1c")
            # Indent response text
            for line in response_text.split('\n'):
                print(f"    {line}")
            print(f"{'-'*80}")

        print("\n" + "="*80)
        print(f"Total Columns: {self.num_columns}")
        print("="*80 + "\n")
