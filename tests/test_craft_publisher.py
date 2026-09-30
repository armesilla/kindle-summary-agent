from unittest.mock import Mock

import pytest

from kindle_summary_agent.domain.models import Book, BookDocument, Highlight
from kindle_summary_agent.publishers.craft import CraftPublisher


def create_document() -> BookDocument:
    book = Book(
        title="Atomic Habits",
        author="James Clear",
        highlights=[
            Highlight(
                text="Small habits compound over time.",
                note="Important idea",
            ),
            Highlight(
                text="Environment shapes behavior.",
            ),
        ],
    )

    return BookDocument(
        book=book,
        summary="A structured summary based on the highlights.",
        key_ideas=[
            "Small improvements compound.",
            "Environment influences behavior.",
        ],
        key_concepts=[
            "Habits",
            "Environment",
        ],
    )


def test_creates_document_when_it_does_not_exist() -> None:
    client = Mock()
    client.find_folder_by_name.return_value = {
        "id": "folder-123",
        "name": "Base de conocimiento",
    }
    client.get_documents.return_value = []
    client.create_document.return_value = {
        "id": "document-123",
        "title": "Atomic Habits",
    }

    publisher = CraftPublisher(
        client=client,
        folder_name="Base de conocimiento",
    )

    document = create_document()

    result = publisher.publish(document)

    client.find_folder_by_name.assert_called_once_with(
        "Base de conocimiento",
    )
    client.get_documents.assert_called_once_with("folder-123")
    client.create_document.assert_called_once_with(
        title="Atomic Habits",
        folder_id="folder-123",
    )

    client.insert_markdown.assert_called_once()

    insert_call = client.insert_markdown.call_args

    assert insert_call.kwargs["document_id"] == "document-123"
    assert "## Información" in insert_call.kwargs["markdown"]
    assert "- Autor: James Clear" in insert_call.kwargs["markdown"]
    assert "- Highlights: 2" in insert_call.kwargs["markdown"]
    assert "## Resumen" in insert_call.kwargs["markdown"]
    assert "A structured summary based on the highlights." in (
        insert_call.kwargs["markdown"]
    )
    assert "- Small improvements compound." in insert_call.kwargs["markdown"]
    assert "- Environment influences behavior." in insert_call.kwargs["markdown"]
    assert "- Habits" in insert_call.kwargs["markdown"]
    assert "- Environment" in insert_call.kwargs["markdown"]
    assert "- Small habits compound over time." in insert_call.kwargs["markdown"]
    assert "  - Nota: Important idea" in insert_call.kwargs["markdown"]
    assert "- Environment shapes behavior." in insert_call.kwargs["markdown"]

    client.replace_document_content.assert_not_called()

    assert result == {
        "id": "document-123",
        "title": "Atomic Habits",
    }


def test_updates_existing_document() -> None:
    existing_document = {
        "id": "document-123",
        "title": "Atomic Habits",
    }

    client = Mock()
    client.find_folder_by_name.return_value = {
        "id": "folder-123",
        "name": "Base de conocimiento",
    }
    client.get_documents.return_value = [
        existing_document,
    ]

    publisher = CraftPublisher(
        client=client,
        folder_name="Base de conocimiento",
    )

    document = create_document()

    result = publisher.publish(document)

    client.replace_document_content.assert_called_once()

    replace_call = client.replace_document_content.call_args

    assert replace_call.kwargs["document_id"] == "document-123"
    assert "## Información" in replace_call.kwargs["markdown"]
    assert "## Resumen" in replace_call.kwargs["markdown"]
    assert "## Ideas principales" in replace_call.kwargs["markdown"]
    assert "## Conceptos clave" in replace_call.kwargs["markdown"]
    assert "## Highlights" in replace_call.kwargs["markdown"]

    client.create_document.assert_not_called()
    client.insert_markdown.assert_not_called()

    assert result is existing_document


def test_title_matching_is_case_insensitive() -> None:
    existing_document = {
        "id": "document-123",
        "title": "atomic habits",
    }

    client = Mock()
    client.find_folder_by_name.return_value = {
        "id": "folder-123",
        "name": "Base de conocimiento",
    }
    client.get_documents.return_value = [
        existing_document,
    ]

    publisher = CraftPublisher(
        client=client,
        folder_name="Base de conocimiento",
    )

    publisher.publish(create_document())

    client.replace_document_content.assert_called_once()
    client.create_document.assert_not_called()


def test_raises_error_when_folder_does_not_exist() -> None:
    client = Mock()
    client.find_folder_by_name.return_value = None

    publisher = CraftPublisher(
        client=client,
        folder_name="Missing folder",
    )

    with pytest.raises(
        RuntimeError,
        match="Craft folder not found: Missing folder",
    ):
        publisher.publish(create_document())

    client.get_documents.assert_not_called()
    client.create_document.assert_not_called()
    client.insert_markdown.assert_not_called()
    client.replace_document_content.assert_not_called()


def test_raises_error_when_multiple_documents_have_same_title() -> None:
    client = Mock()
    client.find_folder_by_name.return_value = {
        "id": "folder-123",
        "name": "Base de conocimiento",
    }
    client.get_documents.return_value = [
        {
            "id": "document-1",
            "title": "Atomic Habits",
        },
        {
            "id": "document-2",
            "title": "atomic habits",
        },
    ]

    publisher = CraftPublisher(
        client=client,
        folder_name="Base de conocimiento",
    )

    with pytest.raises(
        RuntimeError,
        match="Multiple Craft documents found with title: Atomic Habits",
    ):
        publisher.publish(create_document())

    client.create_document.assert_not_called()
    client.insert_markdown.assert_not_called()
    client.replace_document_content.assert_not_called()


def test_uses_unknown_author_when_author_is_missing() -> None:
    client = Mock()
    client.find_folder_by_name.return_value = {
        "id": "folder-123",
        "name": "Base de conocimiento",
    }
    client.get_documents.return_value = []
    client.create_document.return_value = {
        "id": "document-123",
        "title": "Book without author",
    }

    document = BookDocument(
        book=Book(
            title="Book without author",
            highlights=[
                Highlight(text="A useful highlight."),
            ],
        ),
        summary="Summary.",
    )

    publisher = CraftPublisher(
        client=client,
        folder_name="Base de conocimiento",
    )

    publisher.publish(document)

    markdown = client.insert_markdown.call_args.kwargs["markdown"]

    assert "- Autor: Desconocido" in markdown
    assert "- Highlights: 1" in markdown


def test_uses_folder_name_passed_to_constructor() -> None:
    client = Mock()

    publisher = CraftPublisher(
        client=client,
        folder_name="My Craft Folder",
    )

    assert publisher.folder_name == "My Craft Folder"