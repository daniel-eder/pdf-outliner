<!--
SPDX-FileCopyrightText: 2025 Daniel Eder

SPDX-License-Identifier: CC0-1.0
-->

# pdf-outliner

AI-powered PDF outliner that automatically detects headings in PDF documents and adds bookmarks (table of contents) based on the document structure.

## 🌟 Features

- **Intelligent Heading Detection**: Uses LLM technology to identify document headings and their hierarchical structure
- **Automatic Bookmark Creation**: Generates a navigable table of contents in the PDF
- **Flexible Model Support**: Works with any LiteLLM-compatible model (OpenAI, Anthropic, local models, etc.)
- **Command-Line Interface**: Simple CLI for easy integration into workflows
- **Hierarchical Structure**: Preserves heading levels (H1, H2, H3, etc.) in the bookmark tree
- **Page-Accurate**: Links bookmarks to the exact page where headings appear

## 📦 Installation

This project uses [uv](https://github.com/astral-sh/uv) for fast, reliable Python package management.

### Install from GitHub

```bash
# Install directly from GitHub
uv pip install git+https://github.com/daniel-eder/pdf-outliner.git
```

### Install from source

```bash
# Clone and install for development
git clone https://github.com/daniel-eder/pdf-outliner.git
cd pdf-outliner
uv sync
```

### Run without installation

You can also run the tool directly from GitHub with `uvx`:

```bash
# Run directly without installing
uvx --from git+https://github.com/daniel-eder/pdf-outliner.git pdf-outliner input.pdf
```

## 🚀 Usage

### Basic Usage

```bash
pdf-outliner input.pdf
```

This will:
1. Analyze `input.pdf` to detect headings
2. Generate bookmarks based on the structure
3. Save the result as `input_outlined.pdf`

### Advanced Options

```bash
# Specify output file
pdf-outliner input.pdf -o output.pdf

# Use a different model
pdf-outliner input.pdf -m gpt-4o

# Display the detected outline in console
pdf-outliner input.pdf --show-outline

# Combine options
pdf-outliner document.pdf -o bookmarked.pdf -m claude-3-5-sonnet-20241022 --show-outline
```

### CLI Options

- `input_pdf`: Path to the input PDF file (required)
- `-o, --output`: Output PDF file path (default: `input_outlined.pdf`)
- `-m, --model`: LiteLLM model to use (default: `gpt-4o-mini`)
- `--show-outline`: Print the detected outline to console

## ⚙️ Configuration

The tool uses [LiteLLM](https://github.com/BerriAI/litellm) for AI model integration, which supports multiple providers. You need to configure API keys and settings.

### Method 1: Environment File (.env)

Create a `.env` file in your project directory:

```env
# OpenAI
OPENAI_API_KEY=sk-...

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Azure OpenAI
AZURE_API_KEY=...
AZURE_API_BASE=https://...
AZURE_API_VERSION=2024-02-15-preview

# Default model (optional)
DEFAULT_MODEL=gpt-4o-mini
```

### Method 2: Environment Variables

Set environment variables in your shell:

```powershell
# PowerShell
$env:OPENAI_API_KEY="sk-..."
$env:DEFAULT_MODEL="gpt-4o-mini"
```

```bash
# Bash/Zsh (Linux/Mac)
export OPENAI_API_KEY="sk-..."
export DEFAULT_MODEL="gpt-4o-mini"
```

### Method 3: CLI Argument

Pass the model directly via command line:

```bash
pdf-outliner input.pdf -m gpt-4o
```

### Supported Models

Any model supported by LiteLLM works, including:

- **OpenAI**: `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo`, `gpt-3.5-turbo`
- **Anthropic**: `claude-3-5-sonnet-20241022`, `claude-3-opus-20240229`
- **Azure OpenAI**: `azure/<deployment-name>`
- **Local models**: `ollama/llama3`, `ollama/mistral`
- And many more...

See [LiteLLM documentation](https://docs.litellm.ai/docs/providers) for the full list.

## 📄 Licensing

This project uses [REUSE](https://reuse.software/) for clear and comprehensive licensing information, following the [FSFE REUSE specification](https://reuse.software/spec/).

### License Information

All files contain SPDX license headers for easy identification. To check compliance:

```bash
uvx reuse lint
```

## 🛠️ Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/daniel-eder/pdf-outliner.git
cd pdf-outliner

# Sync dependencies and install in editable mode
uv sync

# Run from source
uv run pdf-outliner input.pdf
# or
uv run python -m pdf_outliner.cli input.pdf
```

## 📚 How It Works

1. **Text Extraction**: Extracts text from each page of the PDF using `pypdf`
2. **AI Analysis**: Sends the document to an LLM with instructions to identify headings, their levels, and page numbers
3. **Structured Output**: Uses JSON mode and Pydantic validation to ensure reliable output
4. **Bookmark Generation**: Creates a hierarchical bookmark structure in the PDF using `pypdf`
5. **Output**: Saves a new PDF with the complete bookmark tree

## ⚠️ Limitations

- Large documents may be truncated (50,000 character limit) to fit within model context windows
- Accuracy depends on the chosen LLM model and document structure clarity
- Complex layouts or scanned documents may produce less accurate results
