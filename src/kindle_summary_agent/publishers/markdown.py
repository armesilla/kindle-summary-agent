from pathlib import Path

from kindle_summary_agent.domain.models import BookDocument


class MarkdownPublisher:
    def __init__(self, output_dir: str = "summaries"):
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

        highlights = "\n".join(
            f"- {highlight.text}" for highlight in book.highlights if highlight.text
        )

        return f"""# {book.title}

## Información

- Autor: {book.author or "Desconocido"}
- Highlights: {book.highlight_count}

## Resumen de mis notas

{document.summary}

## Highlights

{highlights}
"""

    def _safe_filename(self, name: str) -> str:
        invalid_chars = '<>:"/\\|?*'
        filename = name

        for char in invalid_chars:
            filename = filename.replace(char, "-")

        return filename.strip()