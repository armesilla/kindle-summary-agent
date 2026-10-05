from datetime import datetime, timezone
from unittest.mock import Mock, call, patch

import pytest

from kindle_summary_agent.domain.models import Book, BookDocument, Highlight
from kindle_summary_agent.services.sync import SyncService
from kindle_summary_agent.services.sync_event import SyncEvent
from kindle_summary_agent.services.sync_result import SyncResult


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
    publisher = Mock()
    progress_callback = Mock()

    sync_state = Mock()
    sync_state.get_last_successful_sync.return_value = None

    service = SyncService(
        readwise_client=readwise_client,
        document_builder=document_builder,
        publishers=[
            publisher,
        ],
        sync_state=sync_state,
        progress_callback=progress_callback,
    )

    result = service.run()

    assert result == SyncResult(
        processed_books=0,
    )

    readwise_client.get_books.assert_called_once_with(
        updated_after=None,
    )

    sync_state.mark_successful_sync.assert_called_once_with(
        sync_started_at,
    )

    document_builder.build.assert_not_called()
    publisher.publish.assert_not_called()

    event_types = [
        event.args[0].event_type
        for event in progress_callback.call_args_list
    ]

    assert event_types == [
        "sync_started",
        "no_books",
    ]


@patch("kindle_summary_agent.services.sync.datetime")
def test_incremental_sync_with_no_books_uses_last_successful_date(
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

    progress_callback = Mock()

    sync_state = Mock()
    sync_state.get_last_successful_sync.return_value = (
        last_successful_sync
    )

    service = SyncService(
        readwise_client=readwise_client,
        document_builder=Mock(),
        publishers=[
            Mock(),
        ],
        sync_state=sync_state,
        progress_callback=progress_callback,
    )

    result = service.run()

    assert result == SyncResult(
        processed_books=0,
    )

    readwise_client.get_books.assert_called_once_with(
        updated_after=last_successful_sync,
    )

    first_event = progress_callback.call_args_list[0].args[0]

    assert first_event.event_type == "sync_started"
    assert last_successful_sync.isoformat() in first_event.message


@patch("kindle_summary_agent.services.sync.datetime")
def test_processes_and_publishes_all_changed_books(
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

    first_publisher = Mock()
    second_publisher = Mock()
    progress_callback = Mock()

    sync_state = Mock()
    sync_state.get_last_successful_sync.return_value = (
        last_successful_sync
    )

    service = SyncService(
        readwise_client=readwise_client,
        document_builder=document_builder,
        publishers=[
            first_publisher,
            second_publisher,
        ],
        sync_state=sync_state,
        progress_callback=progress_callback,
    )

    result = service.run()

    assert result == SyncResult(
        processed_books=2,
    )

    assert document_builder.build.call_args_list == [
        call(first_book),
        call(second_book),
    ]

    assert first_publisher.publish.call_args_list == [
        call(first_document),
        call(second_document),
    ]

    assert second_publisher.publish.call_args_list == [
        call(first_document),
        call(second_document),
    ]

    sync_state.mark_successful_sync.assert_called_once_with(
        sync_started_at,
    )

    events = [
        item.args[0]
        for item in progress_callback.call_args_list
    ]

    event_types = [
        event.event_type
        for event in events
    ]

    assert event_types == [
        "sync_started",
        "books_found",
        "book_started",
        "summary_started",
        "publisher_started",
        "publisher_completed",
        "publisher_started",
        "publisher_completed",
        "book_started",
        "summary_started",
        "publisher_started",
        "publisher_completed",
        "publisher_started",
        "publisher_completed",
        "sync_completed",
    ]

    book_events = [
        event
        for event in events
        if event.event_type == "book_started"
    ]

    assert book_events[0].book_title == "Atomic Habits"
    assert book_events[0].current_book == 1
    assert book_events[0].total_books == 2

    assert book_events[1].book_title == "Deep Work"
    assert book_events[1].current_book == 2
    assert book_events[1].total_books == 2


@patch("kindle_summary_agent.services.sync.datetime")
def test_uses_only_configured_publishers(
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

    selected_publisher = Mock()

    sync_state = Mock()
    sync_state.get_last_successful_sync.return_value = None

    service = SyncService(
        readwise_client=readwise_client,
        document_builder=document_builder,
        publishers=[
            selected_publisher,
        ],
        sync_state=sync_state,
    )

    result = service.run()

    assert result == SyncResult(
        processed_books=1,
    )

    selected_publisher.publish.assert_called_once_with(document)


def test_sync_service_can_run_without_progress_callback() -> None:
    readwise_client = Mock()
    readwise_client.get_books.return_value = []

    sync_state = Mock()
    sync_state.get_last_successful_sync.return_value = None

    service = SyncService(
        readwise_client=readwise_client,
        document_builder=Mock(),
        publishers=[],
        sync_state=sync_state,
        progress_callback=None,
    )

    result = service.run()

    assert result == SyncResult(
        processed_books=0,
    )


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

    successful_publisher = Mock()
    failing_publisher = Mock()
    failing_publisher.publish.side_effect = RuntimeError(
        "Publishing failed"
    )

    progress_callback = Mock()

    sync_state = Mock()
    sync_state.get_last_successful_sync.return_value = None

    service = SyncService(
        readwise_client=readwise_client,
        document_builder=document_builder,
        publishers=[
            successful_publisher,
            failing_publisher,
        ],
        sync_state=sync_state,
        progress_callback=progress_callback,
    )

    with pytest.raises(
        RuntimeError,
        match="Publishing failed",
    ):
        service.run()

    document_builder.build.assert_called_once_with(book)
    successful_publisher.publish.assert_called_once_with(document)
    failing_publisher.publish.assert_called_once_with(document)

    sync_state.mark_successful_sync.assert_not_called()