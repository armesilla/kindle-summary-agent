from kindle_summary_agent.domain.models import Book, BookDocument
from kindle_summary_agent.services.summarizer import Summarizer


class BookDocumentBuilder:
    def __init__(
        self,
        summarizer: Summarizer | None = None,
    ) -> None:
        self.summarizer = summarizer or Summarizer()

    def build(self, book: Book) -> BookDocument:
        generated = self.summarizer.summarize(book)

        return BookDocument(
            book=book,
            summary=generated.summary,
            key_ideas=generated.key_ideas,
            key_concepts=generated.key_concepts,
        )