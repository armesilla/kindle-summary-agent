from collections.abc import Callable
from datetime import datetime, timezone

from kindle_summary_agent.clients.readwise import ReadwiseClient
from kindle_summary_agent.publishers.base import Publisher
from kindle_summary_agent.publishers.craft import CraftPublisher
from kindle_summary_agent.publishers.markdown import MarkdownPublisher
from kindle_summary_agent.services.document_builder import BookDocumentBuilder
from kindle_summary_agent.services.sync_event import SyncEvent
from kindle_summary_agent.services.sync_result import SyncResult
from kindle_summary_agent.services.sync_state import SyncState


ProgressCallback = Callable[[SyncEvent], None]


class SyncService:
    def __init__(
        self,
        readwise_client: ReadwiseClient | None = None,
        document_builder: BookDocumentBuilder | None = None,
        publishers: list[Publisher] | None = None,
        sync_state: SyncState | None = None,
        progress_callback: ProgressCallback | None = None,
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
        self.progress_callback = progress_callback

    def run(self) -> SyncResult:
        sync_started_at = datetime.now(timezone.utc)
        last_successful_sync = self.sync_state.get_last_successful_sync()

        if last_successful_sync is None:
            self._emit(
                SyncEvent(
                    event_type="sync_started",
                    message=(
                        "🔄 Primera sincronización: "
                        "se procesarán todos los libros"
                    ),
                )
            )
        else:
            self._emit(
                SyncEvent(
                    event_type="sync_started",
                    message=(
                        "🔄 Sincronización incremental desde: "
                        f"{last_successful_sync.isoformat()}"
                    ),
                )
            )

        books = self.readwise_client.get_books(
            updated_after=last_successful_sync,
        )

        if not books:
            self._emit(
                SyncEvent(
                    event_type="no_books",
                    message="✅ No hay libros nuevos o modificados",
                )
            )

            self.sync_state.mark_successful_sync(sync_started_at)

            return SyncResult(
                processed_books=0,
            )

        total_books = len(books)

        self._emit(
            SyncEvent(
                event_type="books_found",
                message=f"📚 Libros que se procesarán: {total_books}",
                total_books=total_books,
            )
        )

        for index, book in enumerate(books, start=1):
            self._emit(
                SyncEvent(
                    event_type="book_started",
                    message=f"📖 [{index}/{total_books}] {book.title}",
                    book_title=book.title,
                    current_book=index,
                    total_books=total_books,
                )
            )

            self._emit(
                SyncEvent(
                    event_type="summary_started",
                    message=(
                        f"🤖 Generando resumen de "
                        f"{book.title}..."
                    ),
                    book_title=book.title,
                    current_book=index,
                    total_books=total_books,
                )
            )

            document = self.document_builder.build(book)

            for publisher in self.publishers:
                publisher_name = publisher.__class__.__name__

                self._emit(
                    SyncEvent(
                        event_type="publisher_started",
                        message=(
                            f"📤 Publicando en "
                            f"{publisher_name}..."
                        ),
                        book_title=book.title,
                        current_book=index,
                        total_books=total_books,
                        publisher_name=publisher_name,
                    )
                )

                publisher.publish(document)

                self._emit(
                    SyncEvent(
                        event_type="publisher_completed",
                        message=f"✅ {publisher_name}",
                        book_title=book.title,
                        current_book=index,
                        total_books=total_books,
                        publisher_name=publisher_name,
                    )
                )

        self.sync_state.mark_successful_sync(sync_started_at)

        self._emit(
            SyncEvent(
                event_type="sync_completed",
                message="✅ Sincronización completada correctamente",
                total_books=total_books,
            )
        )

        return SyncResult(
            processed_books=total_books,
        )

    def _emit(self, event: SyncEvent) -> None:
        if self.progress_callback is not None:
            self.progress_callback(event)