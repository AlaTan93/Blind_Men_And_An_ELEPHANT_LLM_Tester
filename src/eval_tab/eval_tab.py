"""Evaluation tab for assessing LLM responses against binary evaluation prompts."""
import os
import re
import threading

import customtkinter as ctk
import yaml
from tkinter import messagebox

from src.api_key_tab import api_keys
from src.logger import get_logger
from src.llm import DisplayModel, send_anthropic_prompt, send_openai_prompt
from src.llm_tab import LLMMainTab

logger = get_logger(__name__)

NUM_EVAL_PROMPTS = 3

# Prepended to each evaluation call so the model knows to return 0 or 1
_EVAL_INSTRUCTION = (
    "You are a response evaluator. You may reason freely, but your final line "
    "MUST be exactly '0' (fail) or '1' (pass) — a single digit, nothing else.\n\n"
)

# Border colours reused from the prompt tab for visual consistency
_BORDER_COLORS = [
    "#1f538d", "#14a085", "#8e44ad", "#c0392b", "#d68910",
    "#117864", "#6c3483", "#884ea0", "#1a5490", "#196f3d",
]


class EvalTab:
    """Handles the evaluation tab: mirrors prompt-tab columns and scores responses."""

    def __init__(self, parent: ctk.CTkFrame, prompt_tab: LLMMainTab):
        self.parent = parent
        self.prompt_tab = prompt_tab
        self.eval_column_frames: list[dict] = []
        self._eval_pending = 0
        self._eval_lock = threading.Lock()

        self._setup_ui()

        # Auto-update eval columns whenever the prompt tab receives a response
        self.prompt_tab.response_callbacks.append(self._on_prompt_response)

    # ------------------------------------------------------------------ #
    #  UI construction                                                     #
    # ------------------------------------------------------------------ #

    def _setup_ui(self):
        # ── Prompt mirror ────────────────────────────────────────────────
        ctk.CTkLabel(
            self.parent, text="Prompt (from Prompt tab):",
            font=("Arial", 14, "bold"),
        ).pack(pady=(10, 3), anchor="w", padx=10)

        self.prompt_display = ctk.CTkTextbox(self.parent, height=80, font=("Arial", 12))
        self.prompt_display.pack(pady=(0, 8), padx=10, fill="x")
        self.prompt_display.configure(state="disabled")

        # ── Response columns (rebuilt on each evaluation) ────────────────
        self.columns_scroll = ctk.CTkScrollableFrame(
            self.parent, label_text="Response Columns & Results",
        )
        self.columns_scroll.pack(pady=(0, 8), padx=10, fill="both", expand=True)

        # ── Eval config section ──────────────────────────────────────────
        config_frame = ctk.CTkFrame(self.parent)
        config_frame.pack(pady=(0, 8), padx=10, fill="x")

        ctk.CTkLabel(
            config_frame, text="Evaluation Prompts:",
            font=("Arial", 13, "bold"),
        ).pack(pady=(10, 2), anchor="w", padx=10)

        ctk.CTkLabel(
            config_frame,
            text="Each prompt must contain {prompt} and {response}",
            font=("Arial", 11), text_color="gray",
        ).pack(anchor="w", padx=10)

        self.eval_prompt_textboxes: list[ctk.CTkTextbox] = []
        for i in range(NUM_EVAL_PROMPTS):
            ctk.CTkLabel(
                config_frame, text=f"Eval Prompt {i + 1}:",
                font=("Arial", 12, "bold"),
            ).pack(pady=(8, 2), anchor="w", padx=10)
            tb = ctk.CTkTextbox(config_frame, height=65, font=("Arial", 11))
            tb.pack(padx=10, pady=(0, 4), fill="x")
            self.eval_prompt_textboxes.append(tb)

        self._load_eval_prompts()

        # Save button
        ctk.CTkButton(
            config_frame, text="Save Eval Prompts to Config",
            command=self._save_eval_prompts, width=220,
        ).pack(pady=(6, 10), padx=10, anchor="w")

        # Evaluator model row
        model_row = ctk.CTkFrame(config_frame, fg_color="transparent")
        model_row.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkLabel(
            model_row, text="Evaluator Model:", font=("Arial", 12, "bold"),
        ).pack(side="left", padx=(0, 10))

        self.eval_model_dropdown = ctk.CTkComboBox(
            model_row,
            values=["Loading models..."],
            state="readonly",
            width=380,
        )
        self.eval_model_dropdown.pack(side="left")

        # Begin polling until the prompt tab has finished loading models
        self.parent.after(200, self._poll_model_sync)

        # ── Evaluate button ──────────────────────────────────────────────
        self.eval_btn = ctk.CTkButton(
            self.parent, text="Evaluate All Responses",
            command=self._run_evaluation,
            font=("Arial", 12), height=40,
        )
        self.eval_btn.pack(pady=(0, 10), padx=10, fill="x")

    # ------------------------------------------------------------------ #
    #  Model dropdown sync                                                 #
    # ------------------------------------------------------------------ #

    def _poll_model_sync(self):
        """Poll every 300 ms until the prompt tab's models are loaded."""
        if self.prompt_tab.models_loaded:
            self._sync_model_dropdown()
        else:
            self.parent.after(300, self._poll_model_sync)

    def _sync_model_dropdown(self):
        """Update the evaluator model dropdown from the prompt tab's model list."""
        values = list(self.prompt_tab.display_to_model.keys())
        if not values:
            return
        self.eval_model_dropdown.configure(values=values)
        if self.eval_model_dropdown.get() not in values:
            self.eval_model_dropdown.set(values[0])

    # ------------------------------------------------------------------ #
    #  Column mirroring                                                    #
    # ------------------------------------------------------------------ #

    def _rebuild_columns(self):
        """Destroy and recreate column widgets to mirror the current prompt tab state."""
        for widget in self.columns_scroll.winfo_children():
            widget.destroy()
        self.eval_column_frames = []

        for i, col in enumerate(self.prompt_tab.column_frames):
            border_color = _BORDER_COLORS[i % len(_BORDER_COLORS)]

            col_frame = ctk.CTkFrame(
                self.columns_scroll, border_width=3, border_color=border_color,
            )
            col_frame.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
            self.columns_scroll.grid_columnconfigure(i, weight=1, uniform="eval_col")

            # Model name
            ctk.CTkLabel(
                col_frame,
                text=col["dropdown1"].get(),
                font=("Arial", 11, "bold"),
                text_color=border_color,
                wraplength=230,
            ).pack(pady=(10, 5), padx=10)

            # Response mirror (read-only)
            ctk.CTkLabel(col_frame, text="Response:", font=("Arial", 11)).pack(
                anchor="w", padx=10,
            )
            resp_tb = ctk.CTkTextbox(col_frame, height=200, font=("Arial", 11))
            resp_tb.pack(padx=10, pady=(0, 8), fill="both", expand=True)

            source = col["response"]
            source.configure(state="normal")
            resp_text = source.get("1.0", "end-1c")
            source.configure(state="disabled")

            resp_tb.insert("1.0", resp_text)
            resp_tb.configure(state="disabled")

            # One result row per eval prompt
            result_labels: list[ctk.CTkLabel] = []
            for j in range(NUM_EVAL_PROMPTS):
                row = ctk.CTkFrame(col_frame, fg_color="transparent")
                row.pack(fill="x", padx=10, pady=2)
                ctk.CTkLabel(
                    row, text=f"Eval {j + 1}:", font=("Arial", 11),
                ).pack(side="left")
                lbl = ctk.CTkLabel(row, text="—", font=("Arial", 13, "bold"), width=30)
                lbl.pack(side="left", padx=5)
                result_labels.append(lbl)

            self.eval_column_frames.append({
                "response_tb": resp_tb,
                "result_labels": result_labels,
                "response_text": resp_text,
            })

    def _on_prompt_response(self, col_index: int, text: str):
        """Called on the main thread each time a prompt-tab column gets a response.

        If the eval columns already exist and match the prompt tab's column count,
        update only the affected column's response textbox in-place (preserving any
        evaluation results already shown).  Otherwise do a full rebuild so the column
        layout stays in sync.
        """
        # Always keep the prompt mirror current
        prompt_text = self.prompt_tab.prompt_textbox.get("1.0", "end-1c").strip()
        self._set_textbox(self.prompt_display, prompt_text)

        if len(self.eval_column_frames) == len(self.prompt_tab.column_frames):
            col_data = self.eval_column_frames[col_index]
            self._set_textbox(col_data["response_tb"], text)
            col_data["response_text"] = text
        else:
            self._rebuild_columns()

    # ------------------------------------------------------------------ #
    #  Evaluation logic                                                    #
    # ------------------------------------------------------------------ #

    def _run_evaluation(self):
        """Validate inputs, rebuild columns, then dispatch evaluation threads."""
        # Always re-sync models before running
        self._sync_model_dropdown()

        # Mirror current prompt text
        prompt_text = self.prompt_tab.prompt_textbox.get("1.0", "end-1c").strip()
        self._set_textbox(self.prompt_display, prompt_text)

        # Rebuild column display
        self._rebuild_columns()

        if not self.eval_column_frames:
            messagebox.showwarning("No Columns", "No columns found in the Prompt tab.")
            return

        if not prompt_text:
            messagebox.showwarning("Empty Prompt", "The Prompt tab has no prompt text.")
            return

        # Validate eval prompts
        eval_prompts: list[str] = []
        for i, tb in enumerate(self.eval_prompt_textboxes):
            text = tb.get("1.0", "end-1c").strip()
            if not text:
                messagebox.showwarning("Empty Eval Prompt", f"Eval Prompt {i + 1} is empty.")
                return
            if "{prompt}" not in text or "{response}" not in text:
                messagebox.showwarning(
                    "Invalid Eval Prompt",
                    f"Eval Prompt {i + 1} must contain both {{prompt}} and {{response}}.",
                )
                return
            eval_prompts.append(text)

        # Resolve evaluator model
        selected = self.eval_model_dropdown.get()
        model = self.prompt_tab.display_to_model.get(selected)
        if model is None:
            messagebox.showwarning("No Model", "Please select a valid evaluator model.")
            return

        self.eval_btn.configure(state="disabled")

        # Reset labels
        for col_data in self.eval_column_frames:
            for lbl in col_data["result_labels"]:
                lbl.configure(text="…", text_color="gray")

        # Dispatch one thread per (column × eval_prompt) combination
        total = len(self.eval_column_frames) * len(eval_prompts)
        self._eval_pending = total

        for col_data in self.eval_column_frames:
            response_text = col_data["response_text"]
            for ep_idx, eval_prompt in enumerate(eval_prompts):
                filled = (
                    _EVAL_INSTRUCTION
                    + eval_prompt
                    .replace("{prompt}", prompt_text)
                    .replace("{response}", response_text)
                )
                thread = threading.Thread(
                    target=self._eval_worker,
                    args=(model, filled, col_data["result_labels"][ep_idx]),
                    daemon=True,
                )
                thread.start()

    def _eval_worker(
        self,
        model: DisplayModel,
        filled_prompt: str,
        result_lbl: ctk.CTkLabel,
    ):
        """Background thread: call the evaluator model and parse a 0/1 result."""
        api_key = (
            api_keys["claude"] if model.provider == "Anthropic" else api_keys["openai"]
        )
        send_fn = (
            send_anthropic_prompt if model.provider == "Anthropic" else send_openai_prompt
        )

        try:
            raw = send_fn(api_key, model.id, filled_prompt, 0.0)
            result = self._parse_binary(raw)
            logger.info("Eval result parsed as %s from: %r", result, raw[-40:])
        except Exception as e:
            logger.error("Eval worker failed: %s", e)
            result = None

        def update():
            if result == 1:
                result_lbl.configure(text="1", text_color="#2ecc71")
            elif result == 0:
                result_lbl.configure(text="0", text_color="#e74c3c")
            else:
                result_lbl.configure(text="?", text_color="orange")

            with self._eval_lock:
                self._eval_pending -= 1
                if self._eval_pending <= 0:
                    self.eval_btn.configure(state="normal")

        self.parent.after(0, update)

    # ------------------------------------------------------------------ #
    #  Config persistence                                                  #
    # ------------------------------------------------------------------ #

    def _get_config_path(self) -> str:
        return os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "config.yaml",
        )

    def _load_eval_prompts(self):
        """Populate the eval prompt textboxes from config.yaml (if present)."""
        config_file = self._get_config_path()
        if not os.path.exists(config_file):
            return
        try:
            with open(config_file, "r") as f:
                config = yaml.safe_load(f) or {}
            prompts: list = config.get("eval_prompts", [])
            for i, tb in enumerate(self.eval_prompt_textboxes):
                if i < len(prompts) and prompts[i]:
                    tb.insert("1.0", prompts[i])
        except Exception as e:
            logger.error("Failed to load eval prompts: %s", e)

    def _save_eval_prompts(self):
        """Write the current eval prompt texts back to config.yaml."""
        config_file = self._get_config_path()
        try:
            config: dict = {}
            if os.path.exists(config_file):
                with open(config_file, "r") as f:
                    config = yaml.safe_load(f) or {}
            config["eval_prompts"] = [
                tb.get("1.0", "end-1c").strip()
                for tb in self.eval_prompt_textboxes
            ]
            with open(config_file, "w") as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            messagebox.showinfo("Saved", "Eval prompts saved to config.yaml.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save eval prompts: {e}")

    # ------------------------------------------------------------------ #
    #  Helpers                                                             #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _parse_binary(text: str) -> int | None:
        """Return the binary result (0 or 1) from model output.

        Checks the last non-empty line first (model should end with a bare digit),
        then falls back to the last standalone 0 or 1 token in the full text.
        """
        stripped = text.strip()
        for line in reversed(stripped.splitlines()):
            s = line.strip()
            if s in ("0", "1"):
                return int(s)
        # Fallback: last occurrence of a standalone 0 or 1
        matches = re.findall(r"\b[01]\b", stripped)
        if matches:
            return int(matches[-1])
        return None

    @staticmethod
    def _set_textbox(textbox: ctk.CTkTextbox, text: str):
        textbox.configure(state="normal")
        textbox.delete("1.0", "end")
        textbox.insert("1.0", text)
        textbox.configure(state="disabled")
