from kindle_summary_agent.clients.readwise import ReadwiseClient
from kindle_summary_agent.publishers.markdown import MarkdownPublisher
from kindle_summary_agent.services.document_builder import BookDocumentBuilder

BOOK_TO_TEST = (
    "Revolucionarios cibernéticos. Tecnología y política en el Chile de "
    "Salvador Allende"
)


def main() -> None:
    client = ReadwiseClient()

    if not client.validate():
        raise RuntimeError("Invalid Readwise token")

    books = client.get_books()
    builder = BookDocumentBuilder()
    publisher = MarkdownPublisher()

    print("✅ Readwise token válido")
    print(f"📚 Libros encontrados: {len(books)}")

    book = next(
        (book for book in books if "cibern" in book.title.casefold()),
        None,
    )

    if book is None:
        raise ValueError(f"No se encontró el libro: {BOOK_TO_TEST}")

    print(f"📖 Libro seleccionado: {book.title}")
    print(f"📝 Highlights encontrados: {book.highlight_count}")

    document = builder.build(book)
    path = publisher.publish(document)

    print(f"✅ Documento generado: {path}")


if __name__ == "__main__":
    main()
