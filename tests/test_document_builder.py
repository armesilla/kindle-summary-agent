from unittest.mock import Mock, patch

from kindle_summary_agent.clients.llm import SummaryOutput
from kindle_summary_agent.domain.models import Book, Highlight
from kindle_summary_agent.services.document_builder import BookDocumentBuilder


@patch("kindle_summary_agent.services.document_builder.Summarizer")
def test_build_creates_book_document(mock_summarizer_class: Mock) -> None:
    generated = SummaryOutput(
        summary="A generated summary.",
        key_ideas=[
            "Idea one",
            "Idea two",
        ],
        key_concepts=[
            "Concept one",
            "Concept two",
        ],
    )

    mock_summarizer = Mock()
    mock_summarizer.summarize.return_value = generated
    mock_summarizer_class.return_value = mock_summarizer

    book = Book(
        title="Atomic Habits",
        author="James Clear",
        highlights=[
            Highlight(text="Small habits matter."),
        ],
    )

    builder = BookDocumentBuilder()

    document = builder.build(book)

    mock_summarizer.summarize.assert_called_once_with(book)

    assert document.book is book
    assert document.summary == generated.summary
    assert document.key_ideas == generated.key_ideas
    assert document.key_concepts == generated.key_concepts


def test_uses_summarizer_passed_to_constructor() -> None:
    summarizer = Mock()

    builder = BookDocumentBuilder(
        summarizer=summarizer,
    )

    assert builder.summarizer is summarizer