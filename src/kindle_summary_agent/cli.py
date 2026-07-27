from kindle_summary_agent.clients.readwise import ReadwiseClient
from kindle_summary_agent.publishers.craft import CraftPublisher
from kindle_summary_agent.publishers.markdown import MarkdownPublisher
from kindle_summary_agent.services.document_builder import BookDocumentBuilder

BOOK_QUERY = "cibern"


def main() -> None:
    readwise_client = ReadwiseClient()

    if not readwise_client.validate():
        raise RuntimeError("Invalid Readwise token")

    books = readwise_client.get_books()

    print("✅ Token de Readwise válido")
    print(f"📚 Libros encontrados: {len(books)}")

    book = next(
        (book for book in books if BOOK_QUERY.casefold() in book.title.casefold()),
        None,
    )

    if book is None:
        raise RuntimeError(f"No se encontró ningún libro que contenga: {BOOK_QUERY}")

    print(f"📖 Libro seleccionado: {book.title}")
    print(f"📝 Highlights encontrados: {book.highlight_count}")
    print("🤖 Generando resumen estructurado...")

    document_builder = BookDocumentBuilder()
    document = document_builder.build(book)

    markdown_publisher = MarkdownPublisher()
    markdown_path = markdown_publisher.publish(document)

    print(f"✅ Markdown generado: {markdown_path}")

    craft_publisher = CraftPublisher()
    craft_document = craft_publisher.publish(document)

    print(f"✅ Documento publicado en Craft: {craft_document['title']}")


if __name__ == "__main__":
    main()
