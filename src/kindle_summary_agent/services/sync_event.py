from dataclasses import dataclass


@dataclass(frozen=True)
class SyncEvent:
    event_type: str
    message: str
    book_title: str | None = None
    current_book: int | None = None
    total_books: int | None = None
    publisher_name: str | None = None