# 🚀 Kindle Summary Agent

> **Turn your Kindle highlights into structured summaries automatically.**
>
> Read. Highlight. Let the agent do the rest.

Kindle Summary Agent is an open-source tool that transforms your Kindle highlights into structured AI-powered summaries and publishes them directly to your knowledge system.

Instead of manually exporting highlights, crafting prompts and organizing notes, simply read as you always do. Kindle Summary Agent automates everything that happens after you finish a book.

---

## ✨ Why Kindle Summary Agent?

Reading a great book should leave you with knowledge, not extra work.

Most readers end up following the same repetitive workflow:

- Export highlights from Readwise
- Copy and paste them into ChatGPT
- Write or tweak prompts
- Organize the generated content
- Save everything in a notes app

Kindle Summary Agent removes that entire process.

Your reading workflow becomes:

> **Read → Highlight → Done**

---

## ⚡ Features

- 📚 Import highlights directly from Readwise
- 🤖 Generate structured summaries using OpenAI
- 📝 Publish summaries to Craft
- 📄 Export Markdown files automatically
- 🔄 Synchronize only new or updated books
- 🔓 Fully open source

---

## 🏗️ How it works

```text
Kindle
   │
   ▼
Readwise
   │
   ▼
Kindle Summary Agent
   │
   ├── Downloads highlights
   ├── Generates a structured summary
   ├── Creates a local Markdown file
   └── Publishes the document to Craft
```

Every processed book produces:

- A local Markdown document.
- A Craft document, ready to browse and search.

---

# 🚀 Installation

## Requirements

Before getting started, make sure you have:

- Python 3.12 or later
- A Readwise account
- An OpenAI API key
- A Craft integration URL

Clone the repository:

```bash
git clone https://github.com/armesilla/armesilla-kindle-summary-agent.git
cd armesilla-kindle-summary-agent
```

Install the project:

```bash
pip install -e .
```

Or install it together with the development dependencies:

```bash
pip install -e ".[dev]"
```

---

# ⚙️ Configuration

The application is configured through environment variables.

An `.env.example` file is included in the repository as a reference.

> **Note**
>
> The current version does **not** load `.env` files automatically.
> Environment variables must be exported before running the application or loaded using an external tool.

Example:

```bash
export READWISE_TOKEN="..."
export OPENAI_API_KEY="..."
export CRAFT_API_URL="..."
export CRAFT_FOLDER_NAME="Base de conocimiento"
```

### Required variables

| Variable | Description |
|----------|-------------|
| `READWISE_TOKEN` | Readwise API token |
| `OPENAI_API_KEY` | OpenAI API key |
| `CRAFT_API_URL` | Craft integration URL |

### Optional variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CRAFT_FOLDER_NAME` | `Base de conocimiento` | Destination folder inside Craft |

---

# 🚀 Quick Start

Process all new or updated books:

```bash
python -m kindle_summary_agent.cli sync
```

Or generate the summary for a specific book:

```bash
python -m kindle_summary_agent.cli book --query "Atomic Habits"
```

The search is case-insensitive and supports partial title matching.

---

# 📚 Commands

## Sync new or updated books

```bash
python -m kindle_summary_agent.cli sync
```

This command:

- Validates your Readwise token.
- Detects books changed since the last successful synchronization.
- Downloads the latest highlights.
- Generates new structured summaries.
- Updates both the Markdown file and the Craft document.
- Saves the synchronization state.
---

## Process a single book

```bash
python -m kindle_summary_agent.cli book --query "Atomic Habits"
```

This command:

- Downloads your Readwise library.
- Finds the matching book.
- Generates a structured summary.
- Creates a local Markdown document.
- Creates or updates the corresponding Craft document.

If multiple books match the query, the application asks for a more specific title.

---

# 📄 Output

For every processed book, Kindle Summary Agent generates two outputs.

## Local Markdown

```
summaries/<book-title>.md
```

The Markdown document includes:

- Book information
- Structured summary
- Key ideas
- Key concepts
- Complete highlights
- Highlight notes (when available)

---

## Craft

A document is created or updated inside the configured Craft folder.

If a document with the same title already exists, its content is replaced.

If multiple documents with the same title exist inside the destination folder, the process stops to avoid updating the wrong document.

---

# 📂 Project Structure

```text
summaries/
    Atomic Habits.md
    Deep Work.md
    Thinking Fast and Slow.md
```

Each processed book generates one Markdown file.

---

# ❓ FAQ

### Do I need a Kindle?

Yes.

---

### Do I need Readwise?

Yes.

At the moment, Readwise is the only supported source for highlights.

---

### Which AI model is used?

The current version uses:

```
gpt-4.1-mini
```

The model selection is currently fixed in the source code.

---

### Is my data stored?

No.

The application processes your highlights and generates local Markdown files and Craft documents.

Your reading data is not stored by Kindle Summary Agent.

---

### Can I use only Markdown?

Not in the current version.

The current publishing workflow always generates both a local Markdown file and a Craft document.

---

# ⚠️ Current Limitations

This is the first public version of Kindle Summary Agent.

Current limitations include:

- `.env` files are not loaded automatically.
- OpenAI model selection is not configurable.
- Readwise is the only supported highlights provider.
- Only Markdown and Craft are currently supported as publishing destinations.

These areas are expected to evolve in future releases.

---

# 🤝 Contributing

Contributions are always welcome.

Whether you want to:

- Fix a bug
- Improve the documentation
- Suggest a feature
- Improve the generated summaries

feel free to open an Issue or submit a Pull Request.

---

# 📜 License

This project is released under the MIT License.

See the [LICENSE](LICENSE) file for details.

---

# ⭐ Support the project

If Kindle Summary Agent helps you get more value from your reading:

- ⭐ Star the repository
- 🐛 Report bugs
- 💡 Suggest improvements
- 🤝 Share it with other readers

Every contribution helps make the project better.

Happy reading! 📚