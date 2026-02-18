"""Main tab with LLM prompt input and dynamic columns for model comparison."""
import random
import threading
import time

import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from src.api_key_tab import api_keys
from src.logger import get_logger
from src.llm import (
    DisplayModel,
    get_anthropic_chat_models, 
    get_openai_chat_models,
    send_anthropic_prompt, 
    send_openai_prompt,
)


logger = get_logger(__name__)


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

        # Maps display string -> DisplayModel for lookup
        self.display_to_model: dict[str, DisplayModel] = {}
        self.dropdown_values: list[str] = ["Loading models..."]
        self.models_loaded = False

        # Callbacks invoked on the main thread when a column response arrives.
        # Signature: callback(col_index: int, response_text: str)
        self.response_callbacks: list = []

        self.setup_ui()
        self._load_models_async()


    def get_selected_model_id(self, column_index: int) -> str | None:
        """Return the model ID for the currently selected model in a column.

        Args:
            column_index: 0-based index into self.column_frames

        Returns:
            The model ID string, or None if not found.
        """
        selected = self.column_frames[column_index]["dropdown1"].get()
        model = self.display_to_model.get(selected)
        return model.id if model else None


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

        # Send prompt button (disabled until models finish loading)
        self.send_btn = ctk.CTkButton(self.parent, text="Send Prompt to All Models",
                                      command=self.send_all_prompts,
                                      font=("Arial", 12), height=40)
        self.send_btn.pack(pady=10, padx=10, fill="x")


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
                                    values=self.dropdown_values,
                                    state="readonly",
                                    width=250)
        dropdown1.set(self.dropdown_values[0])
        dropdown1.pack(pady=(0, 10), padx=10, fill="x")

        # Temperature entry
        temp_label = ctk.CTkLabel(column_frame, text="Temperature (0.0 - 1.5):")
        temp_label.pack(pady=(5, 2))

        temp_var = tk.StringVar(value="0.0")
        temp_entry = ctk.CTkEntry(column_frame, textvariable=temp_var, width=250)
        temp_entry.pack(pady=(0, 10), padx=10, fill="x")

        # Validate on every keystroke
        temp_var.trace_add("write", lambda *_: self._validate_temperature(temp_var))

        # Response textbox (read-only but copyable)
        response_label = ctk.CTkLabel(column_frame, text="Response:")
        response_label.pack(pady=(5, 2))

        response_textbox = ctk.CTkTextbox(column_frame, height=300, font=("Arial", 11))
        response_textbox.pack(pady=(0, 10), padx=10, fill="both", expand=True)

        # Insert placeholder text and make read-only
        response_textbox.insert("1.0",
                               "Response from model will appear here...\n\n"
                               "(This textbox is read-only but you can copy text from it)")
        response_textbox.configure(state="disabled")

        # Store reference
        self.column_frames.append({
            "frame": column_frame,
            "dropdown1": dropdown1,
            "temp_var": temp_var,
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


    def send_all_prompts(self):
        """Send the prompt to every column's selected model in parallel."""
        prompt_text = self.prompt_textbox.get("1.0", "end-1c").strip()
        if not prompt_text:
            messagebox.showwarning("Empty Prompt", "Please enter a prompt before sending.")
            return

        logger.info("Sending prompt to %d column(s)", len(self.column_frames))
        self.send_btn.configure(state="disabled")

        # Track how many columns are still pending so we can re-enable the button
        self._pending_count = len(self.column_frames)
        self._pending_lock = threading.Lock()

        for i, col in enumerate(self.column_frames):
            model_id = self.get_selected_model_id(i)
            if model_id is None:
                self._column_done(col, "[Error] No valid model selected.")
                continue

            model = self.display_to_model[col["dropdown1"].get()]
            temp_str = col["temp_var"].get()
            temperature = float(temp_str) if temp_str else 0.7

            # Show a loading indicator
            self._set_response_text(col["response"], "Sending request...")

            thread = threading.Thread(
                target=self._send_column_worker,
                args=(col, model, model_id, prompt_text, temperature),
                daemon=True,
            )
            thread.start()


    def _send_column_worker(
        self, col: dict, model: DisplayModel,
        model_id: str, prompt: str, temperature: float,
    ):
        """Background worker: send a prompt for one column with retry on rate-limit."""
        max_retries = 5
        api_key = (
            api_keys["claude"] if model.provider == "Anthropic"
            else api_keys["openai"]
        )
        send_fn = (
            send_anthropic_prompt if model.provider == "Anthropic"
            else send_openai_prompt
        )

        logger.info("[%s] Sending prompt (temperature=%.1f)", model_id, temperature)
        for attempt in range(max_retries):
            try:
                response_text = send_fn(api_key, model_id, prompt, temperature)
                logger.info("[%s] Response received", model_id)
                self._column_done(col, response_text)
                return
            except Exception as e:
                error_str = str(e).lower()
                is_rate_limit = "rate" in error_str or "429" in error_str
                if is_rate_limit and attempt < max_retries - 1:
                    backoff = random.uniform(1, 2 ** (attempt + 1))
                    logger.warning("[%s] Rate-limited, retrying in %.1fs (attempt %d/%d)", model_id, backoff, attempt + 1, max_retries)
                    time.sleep(backoff)
                else:
                    logger.error("[%s] Request failed: %s", model_id, e)
                    self._column_done(col, f"[Error] {e}")
                    return


    def _column_done(self, col: dict, text: str):
        """Schedule the response text update on the main thread and track completion."""
        self.parent.after(0, self._set_response_text, col["response"], text)
        for cb in self.response_callbacks:
            self.parent.after(0, cb, col["index"], text)
        with self._pending_lock:
            self._pending_count -= 1
            if self._pending_count <= 0:
                self.parent.after(0, lambda: self.send_btn.configure(state="normal"))


    def _reconfigure_column_grid(self):
        """Reconfigure grid weights to ensure columns resize properly."""
        # Reset all column weights and clear uniform groups
        for i in range(self.max_columns):
            self.columns_scroll_frame.grid_columnconfigure(i, weight=0, uniform="")
        # Set weights only for active columns
        for i in range(self.num_columns):
            self.columns_scroll_frame.grid_columnconfigure(i, weight=1, uniform="column")


    def _load_models_async(self):
        """Kick off model fetching in a background thread."""
        logger.info("Loading available models in background")
        self.send_btn.configure(state="disabled")
        thread = threading.Thread(target=self._fetch_models_thread, daemon=True)
        thread.start()


    def _fetch_models_thread(self):
        """Run in background thread: fetch models from APIs."""
        models: list[DisplayModel] = []

        # Fetch Anthropic models
        if api_keys.get("claude"):
            try:
                for m in get_anthropic_chat_models(api_keys["claude"]):
                    models.append(DisplayModel(
                        provider="Anthropic",
                        display_name=m.display_name,
                        id=m.id,
                    ))
            except Exception as e:
                logger.error("Failed to fetch Anthropic models: %s", e)

        # Fetch OpenAI models
        if api_keys.get("openai"):
            try:
                for m in get_openai_chat_models(api_keys["openai"]):
                    models.append(DisplayModel(
                        provider="OpenAI",
                        display_name=m.display_name,
                        id=m.id,
                    ))
            except Exception as e:
                logger.error("Failed to fetch OpenAI models: %s", e)

        # Schedule UI update on the main thread
        self.parent.after(0, self._on_models_loaded, models)


    def _on_models_loaded(self, models: list[DisplayModel]):
        """Called on the main thread once model fetching is complete."""
        # Build lookup: display string -> DisplayModel
        for model in models:
            label = self._model_label(model)
            self.display_to_model[label] = model

        self.dropdown_values = list(self.display_to_model.keys()) or ["No models available"]
        self.models_loaded = True
        logger.info("Loaded %d model(s)", len(self.display_to_model))

        # Update all existing column dropdowns with the loaded values
        for col in self.column_frames:
            col["dropdown1"].configure(values=self.dropdown_values)
            col["dropdown1"].set(self.dropdown_values[0])

        self.send_btn.configure(state="normal")


    @staticmethod
    def _model_label(model: DisplayModel) -> str:
        """Create a human-readable dropdown label for a model."""
        if model.display_name:
            return f"{model.provider}: {model.display_name} ({model.id})"
        return f"{model.provider}: {model.id}"


    @staticmethod
    def _set_response_text(textbox: ctk.CTkTextbox, text: str):
        """Replace the contents of a response textbox."""
        textbox.configure(state="normal")
        textbox.delete("1.0", "end")
        textbox.insert("1.0", text)
        textbox.configure(state="disabled")


    @staticmethod
    def _validate_temperature(var: tk.StringVar):
        """Clamp the temperature StringVar to valid input (0.0–1.5, max 1 decimal)."""
        value = var.get()

        # Allow empty field while user is typing
        if value == "":
            return

        # Strip anything that isn't a digit or a single dot
        cleaned = ""
        dot_seen = False
        for ch in value:
            if ch.isdigit():
                cleaned += ch
            elif ch == "." and not dot_seen:
                dot_seen = True
                cleaned += ch

        # Enforce at most one decimal place
        if "." in cleaned:
            integer_part, decimal_part = cleaned.split(".", 1)
            decimal_part = decimal_part[:1]
            cleaned = f"{integer_part}.{decimal_part}"

        # Clamp to 0.0–1.5 once we have a parseable number
        try:
            num = float(cleaned)
            if num > 1.5:
                cleaned = "1.5"
            elif num < 0:
                cleaned = "0.0"
        except ValueError:
            pass

        if cleaned != value:
            var.set(cleaned)