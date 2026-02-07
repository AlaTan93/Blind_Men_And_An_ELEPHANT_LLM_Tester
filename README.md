# Blind Men And An ELEPHANT - LLM Tester

Utilising ELEPHANT: Measuring and understanding social sycophancy in LLMs, the goal is to simultaneously test LLMs for sycophancy, and to score them via LLM-as-a-Judge and per human evaluation via UI.

## Progress

Still WIP. Not yet ready for use. UI is 95% done.

## Overview

This cross-platform GUI application allows you to compare responses from multiple Large Language Models (LLMs) side-by-side. The name references the parable of the blind men and an elephant, where each person perceives only part of the truth. Similarly, different LLMs may provide different perspectives on the same prompt.

## Features

- **Multi-Model Comparison**: Test up to 10 LLM responses simultaneously
- **Cross-Platform**: Built with Python 3.13 and CustomTkinter for Windows, macOS, and Linux

## Requirements

- Python 3.13
- uv (Python package manager)

## Installation

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd Blind_Men_And_An_ELEPHANT_LLM_Tester
   ```

2. Install dependencies using uv (uv will automatically create a virtual environment):
   ```bash
   uv sync
   ```

## Running the Application

To run the application:

Set up .env using .env.template.

```bash
uv run python main.py
```

## Usage

### Main Tab

1. **Enter Prompt**: Type your LLM prompt in the resizable text box at the top
2. **Manage Columns**: Use the "+ Add Column" and "- Remove Column" buttons to adjust the number of comparison columns (1-10)
3. **Configure Models**: For each column:
   - Select the model from the first dropdown
   - Set the temperature parameter from the second dropdown
4. **View Responses**: Model responses will appear in the text boxes below (these are read-only but you can copy text from them)

### Options Tab

1. Enter your API keys for:
   - OpenAI
   - Azure
   - Claude
2. Use the "Show" button to temporarily view the keys (they're hidden by default like passwords)
3. Click "Save API Keys" to persist your configuration

**Note**: API keys are stored locally in `config.json` and are excluded from git via `.gitignore`

### About Tab

View information about the application, including version and features.

## Project Structure

```
.
├── main.py           # Main application code
├── pyproject.toml    # Project dependencies and metadata
├── config.json       # API keys storage (created on first save, git-ignored)
├── .python-version   # Python version specification
└── README.md         # This file
```

## Development

This project uses:
- **Python 3.13**: Latest Python version
- **uv**: Fast Python package installer and resolver
- **CustomTkinter**: Modern UI framework built on tkinter

## License

See [LICENSE](LICENSE) file for details.
