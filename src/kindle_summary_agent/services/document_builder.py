from kindle_summary_agent.domain.models import Book, BookDocument


class BookDocumentBuilder:
    def build(self, book: Book) -> BookDocument:
        summary = "Resumen pendiente de generar con IA."

        return BookDocument(
            book=book,
            summary=summary,
        )