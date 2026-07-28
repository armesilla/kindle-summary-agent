from datetime import datetime, timezone

from kindle_summary_agent.clients.readwise import ReadwiseClient
from kindle_summary_agent.publishers.craft import CraftPublisher
from kindle_summary_agent.publishers.markdown import MarkdownPublisher
from kindle_summary_agent.services.document_builder import BookDocumentBuilder
from kindle_summary_agent.services.sync_state import SyncState


class SyncService:
    def __init__(
        self,
        readwise_client: ReadwiseClient | None = None,
        document_builder: BookDocumentBuilder | None = None,
        markdown_publisher: MarkdownPublisher | None = None,
        craft_publisher: CraftPublisher | None = None,
        sync_state: SyncState | None = None,
    ) -> None:
        self.readwise_client = readwise_client or ReadwiseClient()
        self.document_builder = document_builder or BookDocumentBuilder()
        self.markdown_publisher = markdown_publisher or MarkdownPublisher()
        self.craft_publisher = craft_publisher or CraftPublisher()
        self.sync_state = sync_state or SyncState()

    def run(self) -> int:
        sync_started_at = datetime.now(timezone.utc)
        last_successful_sync = self.sync_state.get_last_successful_sync()

        if last_successful_sync is None:
            print("🔄 Primera sincronización: se procesarán todos los libros")
        else:
            print(
                "🔄 Sincronización incremental desde: "
                f"{last_successful_sync.isoformat()}"
            )

        books = self.readwise_client.get_books(
            updated_after=last_successful_sync,
        )

        if not books:
            print("✅ No hay libros nuevos o modificados")
            self.sync_state.mark_successful_sync(sync_started_at)
            return 0

        print(f"📚 Libros que se procesarán: {len(books)}")

        for index, book in enumerate(books, start=1):
            print()
            print(f"📖 [{index}/{len(books)}] {book.title}")
            print(f"📝 Highlights: {book.highlight_count}")
            print("🤖 Generando resumen...")

            document = self.document_builder.build(book)

            markdown_path = self.markdown_publisher.publish(document)
            print(f"✅ Markdown: {markdown_path}")

            craft_document = self.craft_publisher.publish(document)
            print(f"✅ Craft: {craft_document['title']}")

        self.sync_state.mark_successful_sync(sync_started_at)

        print()
        print("✅ Sincronización completada correctamente")

        return len(books)
