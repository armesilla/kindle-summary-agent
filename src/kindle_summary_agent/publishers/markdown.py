from pathlib import Path

from kindle_summary_agent.domain.models import BookDocument, Highlight


class MarkdownPublisher:
    def __init__(self, output_dir: str = "summaries") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def publish(self, document: BookDocument) -> Path:
        filename = self._safe_filename(document.book.title)
        path = self.output_dir / f"{filename}.md"

        content = self._render(document)
        path.write_text(content, encoding="utf-8")

        return path

    def _render(self, document: BookDocument) -> str:
        book = document.book

        key_ideas = "\n".join(f"- {idea}" for idea in document.key_ideas)

        key_concepts = "\n".join(f"- {concept}" for concept in document.key_concepts)

        highlights = "\n".join(
            self._render_highlight(highlight)
            for highlight in book.highlights
            if highlight.text
        )

        return f"""# {book.title}

## Información

- Autor: {book.author or "Desconocido"}
- Highlights: {book.highlight_count}

## Resumen

{document.summary}

## Ideas principales

{key_ideas}

## Conceptos clave

{key_concepts}

## Highlights

{highlights}
"""

    def _render_highlight(self, highlight: Highlight) -> str:
        content = f"- {highlight.text}"

        if highlight.note:
            content += f"\n  - Nota: {highlight.note}"

        return content

    def _safe_filename(self, name: str) -> str:
        invalid_chars = '<>:"/\\|?*'
        filename = name

        for char in invalid_chars:
            filename = filename.replace(char, "-")

        return filename.strip()
