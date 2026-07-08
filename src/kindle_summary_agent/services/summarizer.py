from pathlib import Path

from kindle_summary_agent.domain.models import Book

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "summary.md"


class Summarizer:
    def __init__(self):
        self.prompt_template = PROMPT_PATH.read_text(encoding="utf-8")

    def summarize(self, book: Book) -> str:
        highlights = "\n".join(
            f"- {highlight.text}" for highlight in book.highlights if highlight.text
        )

        prompt = self.prompt_template.format(
            title=book.title,
            author=book.author or "Desconocido",
            highlights=highlights,
        )

        return self._fake_ai_response(prompt)

    def _fake_ai_response(self, prompt: str) -> str:
        return (
            "Resumen pendiente de generar con IA. "
            "El prompt ya está preparado correctamente."
        )
