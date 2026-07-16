from dataclasses import dataclass, field


@dataclass
class Highlight:
    text: str
    note: str | None = None
    location: str | None = None


@dataclass
class Book:
    title: str
    author: str | None = None
    highlights: list[Highlight] = field(default_factory=list)

    @property
    def highlight_count(self) -> int:
        return len(self.highlights)


@dataclass
class BookDocument:
    book: Book
    summary: str
    key_ideas: list[str] = field(default_factory=list)
    key_concepts: list[str] = field(default_factory=list)
