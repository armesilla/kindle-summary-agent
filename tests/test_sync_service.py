from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock, call, patch

import pytest

from kindle_summary_agent.domain.models import Book, BookDocument, Highlight
from kindle_summary_agent.services.sync import SyncService


def create_book(
    title: str = "Atomic Habits",
) -> Book:
    return Book(
        title=title,
        author="James Clear",
        highlights=[
            Highlight(
                text="Small habits compound over time.",
            ),
        ],
    )


def create_document(
    book: Book,
) -> BookDocument:
    return BookDocument(
        book=book,
        summary="A structured summary.",
        key_ideas=[
            "Small improvements compound.",
        ],
        key_concepts=[
            "Habits",
        ],
    )


@patch("kindle_summary_agent.services.sync.datetime")
def test_first_sync_with_no_books_updates_state(
    mock_datetime: Mock,
    capsys: pytest.CaptureFixture[str],
) -> None:
    sync_started_at = datetime(
        2026,
        7,
        30,
        16,
        0,
        tzinfo=timezone.utc,
    )
    mock_datetime.now.return_value = sync_started_at

    readwise_client = Mock()
    readwise_client.get_books.return_value = []

    document_builder = Mock()
    markdown_publisher = Mock()
    craft_publisher = Mock()

    sync_state = Mock()
    sync_state.get_last_successful_sync.return_value = None

    service = SyncService(
        readwise_client=readwise_client,
        document_builder=document_builder,
        markdown_publisher=markdown_publisher,
        craft_publisher=craft_publisher,
        sync_state=sync_state,
    )

    result = service.run()

    assert result == 0

    readwise_client.get_books.assert_called_once_with(
        updated_after=None,
    )
    sync_state.mark_successful_sync.assert_called_once_with(
        sync_started_at,
    )

    document_builder.build.assert_not_called()
    markdown_publisher.publish.assert_not_called()
    craft_publisher.publish.assert_not_called()

    output = capsys.readouterr().out

    assert "Primera sincronización" in output
    assert "No hay libros nuevos o modificados" in output


@patch("kindle_summary_agent.services.sync.datetime")
def test_incremental_sync_with_no_books_uses_last_successful_date(
    mock_datetime: Mock,
    capsys: pytest.CaptureFixture[str],
) -> None:
    sync_started_at = datetime(
        2026,
        7,
        30,
        16,
        0,
        tzinfo=timezone.utc,
    )
    last_successful_sync = datetime(
        2026,
        7,
        29,
        12,
        30,
        tzinfo=timezone.utc,
    )

    mock_datetime.now.return_value = sync_started_at

    readwise_client = Mock()
    readwise_client.get_books.return_value = []

    sync_state = Mock()
    sync_state.get_last_successful_sync.return_value = last_successful_sync

    service = SyncService(
        readwise_client=readwise_client,
        document_builder=Mock(),
        markdown_publisher=Mock(),
        craft_publisher=Mock(),
        sync_state=sync_state,
    )

    result = service.run()

    assert result == 0

    readwise_client.get_books.assert_called_once_with(
        updated_after=last_successful_sync,
    )
    sync_state.mark_successful_sync.assert_called_once_with(
        sync_started_at,
    )

    output = capsys.readouterr().out

    assert "Sincronización incremental desde:" in output
    assert last_successful_sync.isoformat() in output


@patch("kindle_summary_agent.services.sync.datetime")
def test_processes_and_publishes_all_changed_books(
    mock_datetime: Mock,
    capsys: pytest.CaptureFixture[str],
) -> None:
    sync_started_at = datetime(
        2026,
        7,
        30,
        16,
        0,
        tzinfo=timezone.utc,
    )
    last_successful_sync = datetime(
        2026,
        7,
        29,
        12,
        30,
        tzinfo=timezone.utc,
    )

    mock_datetime.now.return_value = sync_started_at

    first_book = create_book(
        title="Atomic Habits",
    )
    second_book = create_book(
        title="Deep Work",
    )

    first_document = create_document(first_book)
    second_document = create_document(second_book)

    readwise_client = Mock()
    readwise_client.get_books.return_value = [
        first_book,
        second_book,
    ]

    document_builder = Mock()
    document_builder.build.side_effect = [
        first_document,
        second_document,
    ]

    markdown_publisher = Mock()
    markdown_publisher.publish.side_effect = [
        Path("summaries/Atomic Habits.md"),
        Path("summaries/Deep Work.md"),
    ]

    craft_publisher = Mock()
    craft_publisher.publish.side_effect = [
        {
            "id": "craft-1",
            "title": "Atomic Habits",
        },
        {
            "id": "craft-2",
            "title": "Deep Work",
        },
    ]

    sync_state = Mock()
    sync_state.get_last_successful_sync.return_value = last_successful_sync

    service = SyncService(
        readwise_client=readwise_client,
        document_builder=document_builder,
        markdown_publisher=markdown_publisher,
        craft_publisher=craft_publisher,
        sync_state=sync_state,
    )

    result = service.run()

    assert result == 2

    readwise_client.get_books.assert_called_once_with(
        updated_after=last_successful_sync,
    )

    assert document_builder.build.call_args_list == [
        call(first_book),
        call(second_book),
    ]

    assert markdown_publisher.publish.call_args_list == [
        call(first_document),
        call(second_document),
    ]

    assert craft_publisher.publish.call_args_list == [
        call(first_document),
        call(second_document),
    ]

    sync_state.mark_successful_sync.assert_called_once_with(
        sync_started_at,
    )

    output = capsys.readouterr().out

    assert "Libros que se procesarán: 2" in output
    assert "[1/2] Atomic Habits" in output
    assert "[2/2] Deep Work" in output
    assert "Sincronización completada correctamente" in output


@patch("kindle_summary_agent.services.sync.datetime")
def test_does_not_update_state_when_publishing_fails(
    mock_datetime: Mock,
) -> None:
    sync_started_at = datetime(
        2026,
        7,
        30,
        16,
        0,
        tzinfo=timezone.utc,
    )
    mock_datetime.now.return_value = sync_started_at

    book = create_book()
    document = create_document(book)

    readwise_client = Mock()
    readwise_client.get_books.return_value = [
        book,
    ]

    document_builder = Mock()
    document_builder.build.return_value = document

    markdown_publisher = Mock()
    markdown_publisher.publish.return_value = Path(
        "summaries/Atomic Habits.md"
    )

    craft_publisher = Mock()
    craft_publisher.publish.side_effect = RuntimeError(
        "Craft publishing failed"
    )

    sync_state = Mock()
    sync_state.get_last_successful_sync.return_value = None

    service = SyncService(
        readwise_client=readwise_client,
        document_builder=document_builder,
        markdown_publisher=markdown_publisher,
        craft_publisher=craft_publisher,
        sync_state=sync_state,
    )

    with pytest.raises(
        RuntimeError,
        match="Craft publishing failed",
    ):
        service.run()

    document_builder.build.assert_called_once_with(book)
    markdown_publisher.publish.assert_called_once_with(document)
    craft_publisher.publish.assert_called_once_with(document)

    sync_state.mark_successful_sync.assert_not_called()