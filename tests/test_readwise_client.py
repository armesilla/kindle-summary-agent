from datetime import datetime, timezone
from unittest.mock import Mock, call, patch

import pytest

from kindle_summary_agent.clients.readwise import BASE_URL, ReadwiseClient


def test_raises_error_when_token_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("READWISE_TOKEN", raising=False)

    with pytest.raises(
        ValueError,
        match="Missing READWISE_TOKEN",
    ):
        ReadwiseClient()


def test_uses_token_passed_to_constructor() -> None:
    client = ReadwiseClient(token="test-token")

    assert client.token == "test-token"
    assert client.headers == {
        "Authorization": "Token test-token",
    }


def test_uses_token_from_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "READWISE_TOKEN",
        "environment-token",
    )

    client = ReadwiseClient()

    assert client.token == "environment-token"
    assert client.headers == {
        "Authorization": "Token environment-token",
    }


@patch("kindle_summary_agent.clients.readwise.requests.get")
def test_validate_returns_true_for_status_204(
    mock_get: Mock,
) -> None:
    response = Mock()
    response.status_code = 204
    mock_get.return_value = response

    client = ReadwiseClient(token="test-token")

    result = client.validate()

    assert result is True

    mock_get.assert_called_once_with(
        f"{BASE_URL}/auth/",
        headers={
            "Authorization": "Token test-token",
        },
        timeout=30,
    )


@patch("kindle_summary_agent.clients.readwise.requests.get")
def test_validate_returns_false_for_other_status(
    mock_get: Mock,
) -> None:
    response = Mock()
    response.status_code = 401
    mock_get.return_value = response

    client = ReadwiseClient(token="test-token")

    result = client.validate()

    assert result is False


def test_extract_book_ids_removes_duplicates_and_sorts() -> None:
    client = ReadwiseClient(token="test-token")

    items = [
        {
            "user_book_id": 20,
        },
        {
            "user_book_id": "10",
        },
        {
            "id": 30,
        },
        {
            "user_book_id": 20,
        },
        {},
    ]

    result = client._extract_book_ids(items)

    assert result == [
        10,
        20,
        30,
    ]


def test_normalize_location_returns_none_for_none() -> None:
    client = ReadwiseClient(token="test-token")

    assert client._normalize_location(None) is None


@pytest.mark.parametrize(
    ("location", "expected"),
    [
        (123, "123"),
        ("Page 42", "Page 42"),
        (4.5, "4.5"),
    ],
)
def test_normalize_location_converts_value_to_string(
    location: object,
    expected: str,
) -> None:
    client = ReadwiseClient(token="test-token")

    assert client._normalize_location(location) == expected


def test_parse_books_creates_domain_models() -> None:
    client = ReadwiseClient(token="test-token")

    items = [
        {
            "title": "Atomic Habits",
            "author": "James Clear",
            "highlights": [
                {
                    "text": "Small habits compound over time.",
                    "note": "Important idea",
                    "location": 123,
                    "is_deleted": False,
                },
                {
                    "text": "Environment shapes behavior.",
                    "location": "Page 42",
                },
            ],
        },
    ]

    books = client._parse_books(items)

    assert len(books) == 1

    book = books[0]

    assert book.title == "Atomic Habits"
    assert book.author == "James Clear"
    assert book.highlight_count == 2

    first_highlight = book.highlights[0]

    assert first_highlight.text == "Small habits compound over time."
    assert first_highlight.note == "Important idea"
    assert first_highlight.location == "123"

    second_highlight = book.highlights[1]

    assert second_highlight.text == "Environment shapes behavior."
    assert second_highlight.note is None
    assert second_highlight.location == "Page 42"


def test_parse_books_ignores_deleted_highlights() -> None:
    client = ReadwiseClient(token="test-token")

    items = [
        {
            "title": "Atomic Habits",
            "highlights": [
                {
                    "text": "Visible highlight.",
                    "is_deleted": False,
                },
                {
                    "text": "Deleted highlight.",
                    "is_deleted": True,
                },
            ],
        },
    ]

    books = client._parse_books(items)

    assert books[0].highlight_count == 1
    assert books[0].highlights[0].text == "Visible highlight."


def test_parse_books_uses_untitled_when_title_is_missing() -> None:
    client = ReadwiseClient(token="test-token")

    books = client._parse_books(
        [
            {
                "title": None,
                "author": None,
                "highlights": [],
            },
        ]
    )

    assert books[0].title == "Untitled"
    assert books[0].author is None
    assert books[0].highlights == []


@patch("kindle_summary_agent.clients.readwise.requests.get")
def test_export_returns_results_from_all_pages(
    mock_get: Mock,
) -> None:
    first_response = Mock()
    first_response.json.return_value = {
        "results": [
            {
                "id": 1,
            },
        ],
        "nextPageCursor": "next-page",
    }

    second_response = Mock()
    second_response.json.return_value = {
        "results": [
            {
                "id": 2,
            },
        ],
        "nextPageCursor": None,
    }

    mock_get.side_effect = [
        first_response,
        second_response,
    ]

    client = ReadwiseClient(token="test-token")

    result = client._export()

    assert result == [
        {
            "id": 1,
        },
        {
            "id": 2,
        },
    ]

    assert mock_get.call_args_list == [
        call(
            f"{BASE_URL}/export/",
            headers={
                "Authorization": "Token test-token",
            },
            params={},
            timeout=30,
        ),
        call(
            f"{BASE_URL}/export/",
            headers={
                "Authorization": "Token test-token",
            },
            params={
                "pageCursor": "next-page",
            },
            timeout=30,
        ),
    ]

    first_response.raise_for_status.assert_called_once_with()
    second_response.raise_for_status.assert_called_once_with()


@patch("kindle_summary_agent.clients.readwise.requests.get")
def test_export_sends_all_optional_parameters(
    mock_get: Mock,
) -> None:
    response = Mock()
    response.json.return_value = {
        "results": [],
        "nextPageCursor": None,
    }
    mock_get.return_value = response

    client = ReadwiseClient(token="test-token")

    updated_after = datetime(
        2026,
        7,
        30,
        8,
        0,
        tzinfo=timezone.utc,
    )

    client._export(
        updated_after=updated_after,
        book_ids=[
            10,
            20,
        ],
        include_deleted=True,
    )

    mock_get.assert_called_once_with(
        f"{BASE_URL}/export/",
        headers={
            "Authorization": "Token test-token",
        },
        params={
            "updatedAfter": updated_after.isoformat(),
            "ids": "10,20",
            "includeDeleted": "true",
        },
        timeout=30,
    )


def test_get_books_performs_full_export_when_date_is_missing() -> None:
    client = ReadwiseClient(token="test-token")

    exported_items = [
        {
            "title": "Atomic Habits",
            "author": "James Clear",
            "highlights": [],
        },
    ]

    client._export = Mock(return_value=exported_items)
    client._parse_books = Mock(return_value=["parsed-book"])

    result = client.get_books()

    assert result == [
        "parsed-book",
    ]

    client._export.assert_called_once_with()
    client._parse_books.assert_called_once_with(exported_items)


def test_incremental_sync_returns_empty_list_when_nothing_changed() -> None:
    client = ReadwiseClient(token="test-token")

    updated_after = datetime(
        2026,
        7,
        30,
        8,
        0,
        tzinfo=timezone.utc,
    )

    client._export = Mock(return_value=[])
    client._extract_book_ids = Mock(return_value=[])

    result = client.get_books(
        updated_after=updated_after,
    )

    assert result == []

    client._export.assert_called_once_with(
        updated_after=updated_after,
        include_deleted=True,
    )
    client._extract_book_ids.assert_called_once_with([])


def test_incremental_sync_downloads_complete_changed_books() -> None:
    client = ReadwiseClient(token="test-token")

    updated_after = datetime(
        2026,
        7,
        30,
        8,
        0,
        tzinfo=timezone.utc,
    )

    changed_items = [
        {
            "user_book_id": 20,
        },
        {
            "user_book_id": 10,
        },
    ]

    complete_items = [
        {
            "title": "Atomic Habits",
            "author": "James Clear",
            "highlights": [
                {
                    "text": "Complete highlight.",
                },
            ],
        },
    ]

    client._export = Mock(
        side_effect=[
            changed_items,
            complete_items,
        ]
    )
    client._extract_book_ids = Mock(
        return_value=[
            10,
            20,
        ]
    )
    client._parse_books = Mock(
        return_value=[
            "parsed-book",
        ]
    )

    result = client.get_books(
        updated_after=updated_after,
    )

    assert result == [
        "parsed-book",
    ]

    assert client._export.call_args_list == [
        call(
            updated_after=updated_after,
            include_deleted=True,
        ),
        call(
            book_ids=[
                10,
                20,
            ],
        ),
    ]

    client._extract_book_ids.assert_called_once_with(changed_items)
    client._parse_books.assert_called_once_with(complete_items)