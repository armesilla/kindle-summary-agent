from dataclasses import dataclass


@dataclass
class SyncResult:
    processed_books: int