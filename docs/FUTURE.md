# Future

This document collects ideas intentionally postponed after the first public release.

The purpose is to preserve the architectural direction of the project without increasing the scope of version 1.x.

Nothing in this document is committed to a specific release.

---

# Guiding principles

Before implementing any new feature, ask:

- Does it improve the current experience?
- Does it preserve the architecture?
- Can it be implemented as a new component?
- Is it really necessary?

If the answer to any of these questions is **no**, the idea should be reconsidered.

---

# Architecture

## Dependency injection

Allow dependency injection in components that currently instantiate their own collaborators.

Examples:

- BookDocumentBuilder
- Summarizer

Benefits:

- Easier testing
- Better extensibility
- Consistent dependency injection

---

## Prompt loader

Current implementation loads prompts directly from disk.

Potential improvement:

```text
PromptLoader
    ├── summary.md
    ├── linkedin.md
    ├── substack.md
    └── reflection.md
```

Benefits:

- Cleaner code
- Easier prompt versioning
- Multiple prompt types

---

## Renderer abstraction

Current publishers generate Markdown internally.

Future architecture:

```text
BookDocument
        │
        ▼
MarkdownRenderer
        │
        ▼
Markdown
        │
 ┌──────┴────────┐
 ▼               ▼
Markdown     Craft
```

This avoids duplicated rendering logic.

---

## Configurable LLM

Current model:

- gpt-4.1-mini

Future:

- configuration through environment variables
- multiple providers
- local models

---

# Importers

Current implementation:

- Readwise

Possible future importers:

- Kindle Clippings
- Kobo
- Apple Books
- CSV
- Generic highlight import

The domain should remain independent from any importer.

---

# Publishers

Current publishers:

- Markdown
- Craft

Possible future publishers:

- Notion
- Obsidian
- Logseq
- HTML
- PDF

Publishers should only consume BookDocument objects.

---

# AI improvements

Possible future improvements:

- Better prompt engineering
- Better concept extraction
- Better duplicate detection
- Improved summaries for books with many highlights
- Metadata extraction
- Topic clustering

---

# User experience

Potential improvements:

- Automatic .env loading
- Better CLI output
- Progress bars
- Cost estimation
- Processing statistics
- Better logging

---

# Packaging

Future improvements:

- Publish on PyPI
- Homebrew formula
- Docker image

---

# Content Engine

Version 2 introduces a new layer built on top of BookDocument.

The Content Engine should consume structured knowledge rather than raw highlights.

Potential outputs:

- Personal reflections
- Substack articles
- LinkedIn posts
- Conference notes
- Podcast outlines

This functionality intentionally remains outside version 1.x.

---

# Lessons learned during V1

## Freeze the architecture early

One of the most valuable decisions of the project.

It allowed the final iterations to focus on:

- quality
- tests
- documentation
- developer experience

instead of continuously changing the design.

---

## Separate the domain from integrations

Readwise, OpenAI and Craft are implementations.

The domain represents knowledge.

This separation proved to be the correct architectural decision.

---

## Prompts are code

Prompts deserve the same treatment as source code:

- versioned
- reviewed
- tested
- documented

---

## Test behaviour, not implementation

Tests should verify what the application does.

Avoid testing internal implementation details.

---

## Finish V1 before designing V2

Publishing a stable version is more valuable than implementing unfinished ideas.

Future improvements should be driven by real user feedback.

---

# Final note

The success of version 1.0 is not measured by the number of features.

It is measured by having a clean architecture, a stable codebase and a project that other developers can understand, use and extend.