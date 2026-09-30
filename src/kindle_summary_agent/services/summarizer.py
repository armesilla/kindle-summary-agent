from pathlib import Path

from kindle_summary_agent.clients.llm import LLMClient, SummaryOutput
from kindle_summary_agent.domain.models import Book

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "summary.md"


class Summarizer:
    def __init__(
        self,
        llm: LLMClient | None = None,
    ) -> None:
        self.prompt_template = PROMPT_PATH.read_text(encoding="utf-8")
        self.llm = llm or LLMClient()

    def summarize(self, book: Book) -> SummaryOutput:
        highlights = "\n".join(
            self._render_highlight(highlight)
            for highlight in book.highlights
            if highlight.text
        )

        prompt = self.prompt_template.format(
            title=book.title,
            author=book.author or "Desconocido",
            highlights=highlights,
        )

        return self.llm.generate_summary(prompt)

    def _render_highlight(self, highlight) -> str:
        content = f"- {highlight.text}"

        if highlight.note:
            content += f"\n  Nota del lector: {highlight.note}"

        return content