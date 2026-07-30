from pathlib import Path

from kindle_summary_agent.domain.models import Book, BookDocument, Highlight
from kindle_summary_agent.publishers.markdown import MarkdownPublisher


def test_markdown_publisher_creates_expected_file(tmp_path: Path) -> None:
    book = Book(
        title="Atomic Habits",
        author="James Clear",
        highlights=[
            Highlight(
                text="Small habits compound over time.",
                note="Useful idea",
            ),
            Highlight(
                text="Environment shapes behavior.",
            ),
        ],
    )

    document = BookDocument(
        book=book,
        summary="A summary based on the selected highlights.",
        key_ideas=[
            "Small improvements compound.",
            "Environment influences behavior.",
        ],
        key_concepts=[
            "Habits",
            "Environment",
        ],
    )

    publisher = MarkdownPublisher(output_dir=str(tmp_path))

    path = publisher.publish(document)

    assert path == tmp_path / "Atomic Habits.md"
    assert path.exists()

    content = path.read_text(encoding="utf-8")

    assert "# Atomic Habits" in content
    assert "- Autor: James Clear" in content
    assert "- Highlights: 2" in content

    assert "## Resumen" in content
    assert "A summary based on the selected highlights." in content

    assert "## Ideas principales" in content
    assert "- Small improvements compound." in content
    assert "- Environment influences behavior." in content

    assert "## Conceptos clave" in content
    assert "- Habits" in content
    assert "- Environment" in content

    assert "## Highlights" in content
    assert "- Small habits compound over time." in content
    assert "  - Nota: Useful idea" in content
    assert "- Environment shapes behavior." in content


def test_markdown_publisher_replaces_invalid_filename_characters(
    tmp_path: Path,
) -> None:
    book = Book(
        title='A title: with / invalid * characters?',
    )

    document = BookDocument(
        book=book,
        summary="Summary.",
    )

    publisher = MarkdownPublisher(output_dir=str(tmp_path))

    path = publisher.publish(document)

    assert path == tmp_path / "A title- with - invalid - characters-.md"
    assert path.exists()


def test_markdown_publisher_uses_unknown_author_when_missing(
    tmp_path: Path,
) -> None:
    book = Book(
        title="Book without author",
        highlights=[
            Highlight(text="A highlight."),
        ],
    )

    document = BookDocument(
        book=book,
        summary="Summary.",
    )

    publisher = MarkdownPublisher(output_dir=str(tmp_path))

    path = publisher.publish(document)
    content = path.read_text(encoding="utf-8")

    assert "- Autor: Desconocido" in content