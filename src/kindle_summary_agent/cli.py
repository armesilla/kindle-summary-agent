import argparse

from kindle_summary_agent.app_config import AppConfig
from kindle_summary_agent.application import build_sync_service
from kindle_summary_agent.clients.readwise import ReadwiseClient
from kindle_summary_agent.publishers.craft import CraftPublisher
from kindle_summary_agent.publishers.markdown import MarkdownPublisher
from kindle_summary_agent.services.document_builder import BookDocumentBuilder
from kindle_summary_agent.services.sync_event import SyncEvent


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="kindle-summary-agent",
        description=(
            "Genera documentos estructurados a partir de tus highlights "
            "de Readwise y los publica en Markdown y Craft."
        ),
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    book_parser = subparsers.add_parser(
        "book",
        help="Procesa un libro concreto.",
    )
    book_parser.add_argument(
        "--query",
        required=True,
        help="Texto que debe aparecer en el título del libro.",
    )

    subparsers.add_parser(
        "sync",
        help="Sincroniza los libros nuevos o modificados.",
    )

    return parser


def print_sync_event(event: SyncEvent) -> None:
    print(event.message)


def process_book(query: str) -> None:
    readwise_client = ReadwiseClient()

    if not readwise_client.validate():
        raise RuntimeError("Invalid Readwise token")

    books = readwise_client.get_books()

    matches = [
        book
        for book in books
        if query.casefold() in book.title.casefold()
    ]

    if not matches:
        raise RuntimeError(
            f"No se encontró ningún libro que contenga: {query}"
        )

    if len(matches) > 1:
        titles = "\n".join(
            f"- {book.title}"
            for book in matches
        )

        raise RuntimeError(
            "La búsqueda coincide con varios libros. "
            "Utiliza una consulta más específica:\n"
            f"{titles}"
        )

    book = matches[0]

    print("✅ Token de Readwise válido")
    print(f"📖 Libro seleccionado: {book.title}")
    print(f"📝 Highlights encontrados: {book.highlight_count}")
    print("🤖 Generando resumen estructurado...")

    document = BookDocumentBuilder().build(book)

    markdown_path = MarkdownPublisher().publish(document)
    print(f"✅ Markdown generado: {markdown_path}")

    craft_document = CraftPublisher().publish(document)
    print(
        "✅ Documento publicado en Craft: "
        f"{craft_document['title']}"
    )


def run_sync() -> None:
    config = AppConfig.from_environment()

    service = build_sync_service(
        config,
        progress_callback=print_sync_event,
    )

    if not service.readwise_client.validate():
        raise RuntimeError("Invalid Readwise token")

    print("✅ Token de Readwise válido")

    result = service.run()

    print(f"📚 Libros procesados: {result.processed_books}")


def main() -> None:
    parser = create_parser()
    arguments = parser.parse_args()

    if arguments.command == "book":
        process_book(arguments.query)
        return

    if arguments.command == "sync":
        run_sync()
        return

    parser.error("Comando no reconocido")


if __name__ == "__main__":
    main()