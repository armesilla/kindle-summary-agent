# Architecture

## Objective

Kindle Summary Agent transforms reading highlights into structured knowledge documents.

The core logic is independent from both the source of the highlights and the final publishing destination.

The current implementation supports:

- Readwise as importer
- OpenAI as LLM provider
- Markdown as output
- Craft as output

The architecture is designed to support future importers, LLM providers, and publishers without changing the core domain.

---

# Architecture overview

```text
Importer
    │
    ▼
Book
    │
    ▼
BookDocumentBuilder
    │
    ▼
Summarizer
    │
    ▼
BookDocument
    │
    ├── MarkdownPublisher
    └── CraftPublisher
```

`BookDocument` is the central object of the application.

It contains the structured knowledge generated from a book and can be sent to multiple publishers.

---

# Project structure

```text
src/
└── kindle_summary_agent/
    ├── clients/
    ├── domain/
    ├── prompts/
    ├── publishers/
    ├── services/
    ├── cli.py
    └── config.py
```

---

# Responsibilities

## `clients/`

Clients communicate with external services.

They are responsible for:

- making HTTP or SDK calls;
- handling external API responses;
- converting external data into formats understood by the application.

They must not contain business logic.

Current clients:

- `ReadwiseClient`
- `LLMClient`
- `CraftClient`

---

## `domain/`

The domain contains the core data models of the project.

Current models:

- `Highlight`
- `Book`
- `BookDocument`

Domain models:

- do not know about external APIs;
- do not know about publishers;
- do not know about the command-line interface;
- do not depend on Craft, Readwise, OpenAI, or Markdown.

---

## `services/`

Services contain the application logic and coordinate the main workflow.

Current services:

- `Summarizer`
- `BookDocumentBuilder`
- `SyncService`
- `SyncState`

Services may depend on domain models and external clients, but the domain must never depend on services.

---

## `publishers/`

Publishers transform a `BookDocument` into a concrete destination.

Current publishers:

- `MarkdownPublisher`
- `CraftPublisher`

Publishers do not generate knowledge.

They only render and publish an already completed `BookDocument`.

Future publishers may include:

- Notion
- Obsidian
- HTML
- Logseq
- other knowledge-management tools

Adding a new publisher should not require changing the domain models or the summarization workflow.

---

## `prompts/`

Prompts contain the instructions used by the LLM.

They are stored outside Python code so they can be:

- reviewed independently;
- versioned;
- improved without changing application logic;
- reused by future LLM providers.

---

## `cli.py`

The command-line interface is the user-facing entry point.

It is responsible for:

- parsing commands and arguments;
- invoking application services;
- displaying progress and errors.

It must not contain external API logic or summarization logic.

---

## `config.py`

Configuration centralizes environment-dependent values such as:

- API credentials;
- Craft folder name;
- future model or language settings.

Secrets must never be committed to the repository.

---

# Importers

An importer converts an external reading source into the domain models used by the application.

Current importer:

- Readwise

Possible future importers:

- Kindle Clippings
- Kobo
- Apple Books
- CSV
- other highlight-export formats

A new importer should produce `Book` and `Highlight` objects without requiring changes to publishers or domain models.

---

# Publishers

A publisher receives a completed `BookDocument` and sends it to a destination.

```text
BookDocument
    │
    ├── Markdown
    ├── Craft
    ├── Notion
    ├── Obsidian
    └── other destinations
```

The destination must not influence how the summary is generated.

---

# Extensibility

The project is designed around interchangeable components.

Current implementations:

- Importer
  - Readwise
- LLM provider
  - OpenAI
- Publishers
  - Markdown
  - Craft

Future integrations should be added as new components whenever possible.

Examples:

- a new importer should convert its source into `Book`;
- a new LLM provider should implement the same generation responsibility;
- a new publisher should consume `BookDocument`.

---

# Principles

## 1. Single responsibility

Each module should have one clear responsibility.

External API access, business logic, rendering, and user interaction must remain separated.

---

## 2. Domain independence

The domain must not depend on:

- Readwise;
- OpenAI;
- Craft;
- Markdown;
- the CLI.

---

## 3. Publisher agnosticism

The application generates a `BookDocument`, not a Craft document or a Markdown file.

The final destination is selected only at the publishing stage.

---

## 4. Importer agnosticism

Readwise is the first importer, not the definition of the domain.

Future sources must be able to produce the same `Book` and `Highlight` models.

---

## 5. LLM agnosticism

The project currently uses OpenAI, but the summarization workflow should not depend permanently on a single provider.

---

## 6. Knowledge first

The project generates structured knowledge.

Files and documents are only representations of that knowledge.

---

## 7. Safe synchronization

The synchronization state is updated only after the entire workflow completes successfully.

A failure in Readwise, the LLM, Markdown, or Craft must not cause unprocessed changes to be skipped in the next run.

---

# Main workflow

```text
Read source
    │
    ▼
Create Book models
    │
    ▼
Generate structured summary
    │
    ▼
Create BookDocument
    │
    ├── Publish to Markdown
    └── Publish to Craft
    │
    ▼
Save successful synchronization state
```

---

# Dependency direction

Dependencies should move inward toward the domain.

```text
CLI
 └── Services
      ├── Clients
      ├── Publishers
      └── Domain

Clients
 └── Domain

Publishers
 └── Domain

Domain
 └── No project-layer dependencies
```

The domain layer must remain the most independent part of the project.

---

# Golden rule

Whenever possible, a new feature should be implemented by adding a new component rather than modifying existing components.

Examples:

- add `NotionPublisher` instead of changing `BookDocument`;
- add `KoboImporter` instead of changing `ReadwiseClient`;
- add another LLM client instead of changing publisher logic.

---

# Architecture freeze

The main architecture for version 1.0 is frozen.

Before the first stable release:

- folder responsibilities should not change;
- domain models should not change unless a defect requires it;
- new functionality should not expand the scope of version 1.0;
- architectural ideas for future versions should be recorded in the roadmap.

**Architecture status:** Frozen for version 1.0