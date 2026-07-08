from kindle_summary_agent.domain.models import Book, BookDocument
from kindle_summary_agent.services.summarizer import Summarizer


class BookDocumentBuilder:
    def __init__(self):
        self.summarizer = Summarizer()

    def build(self, book: Book) -> BookDocument:
        summary = self.summarizer.summarize(book)

        return BookDocument(
            book=book,
            summary=summary,
        )
