from datetime import datetime, timezone

from kindle_summary_agent.clients.readwise import ReadwiseClient
from kindle_summary_agent.publishers.base import Publisher
from kindle_summary_agent.publishers.craft import CraftPublisher
from kindle_summary_agent.publishers.markdown import MarkdownPublisher
from kindle_summary_agent.services.document_builder import BookDocumentBuilder
from kindle_summary_agent.services.sync_result import SyncResult
from kindle_summary_agent.services.sync_state import SyncState


class SyncService:
    def __init__(
        self,
        readwise_client: ReadwiseClient | None = None,
        document_builder: BookDocumentBuilder | None = None,
        publishers: list[Publisher] | None = None,
        sync_state: SyncState | None = None,
    ) -> None:
        self.readwise_client = readwise_client or ReadwiseClient()
        self.document_builder = document_builder or BookDocumentBuilder()

        if publishers is None:
            self.publishers = [
                MarkdownPublisher(),
                CraftPublisher(),
            ]
        else:
            self.publishers = publishers

        self.sync_state = sync_state or SyncState()

    def run(self) -> SyncResult:
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

            return SyncResult(
                processed_books=0,
            )

        print(f"📚 Libros que se procesarán: {len(books)}")

        for index, book in enumerate(books, start=1):
            print()
            print(f"📖 [{index}/{len(books)}] {book.title}")
            print(f"📝 Highlights: {book.highlight_count}")
            print("🤖 Generando resumen...")

            document = self.document_builder.build(book)

            for publisher in self.publishers:
                result = publisher.publish(document)
                publisher_name = publisher.__class__.__name__
                print(f"✅ {publisher_name}: {result}")

        self.sync_state.mark_successful_sync(sync_started_at)

        print()
        print("✅ Sincronización completada correctamente")

        return SyncResult(
            processed_books=len(books),
        )