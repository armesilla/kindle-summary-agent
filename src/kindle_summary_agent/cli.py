from kindle_summary_agent.clients.readwise import ReadwiseClient
from kindle_summary_agent.publishers.markdown import MarkdownPublisher
from kindle_summary_agent.services.document_builder import BookDocumentBuilder


def main() -> None:
    client = ReadwiseClient()

    if not client.validate():
        raise RuntimeError("Invalid Readwise token")

    books = client.get_books()
    builder = BookDocumentBuilder()
    publisher = MarkdownPublisher()

    print("✅ Readwise token válido")
    print(f"📚 Libros encontrados: {len(books)}")

    for book in books[:5]:
        document = builder.build(book)
        path = publisher.publish(document)
        print(f"📝 Generado: {path}")


if __name__ == "__main__":
    main()
