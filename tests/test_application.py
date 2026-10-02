from unittest.mock import Mock, patch

import pytest

from kindle_summary_agent.app_config import AppConfig
from kindle_summary_agent.application import (
    build_publishers,
    build_sync_service,
)
from kindle_summary_agent.publishers.craft import CraftPublisher
from kindle_summary_agent.publishers.markdown import MarkdownPublisher


def create_config(
    enabled_publishers: list[str] | None = None,
) -> AppConfig:
    return AppConfig(
        readwise_token="readwise-token",
        openai_api_key="openai-key",
        enabled_publishers=(
            enabled_publishers
            if enabled_publishers is not None
            else ["markdown"]
        ),
        craft_api_url="https://example.craft.do",
        craft_folder_name="Base de conocimiento",
    )


def test_build_publishers_creates_markdown_publisher() -> None:
    config = create_config(
        enabled_publishers=[
            "markdown",
        ],
    )

    publishers = build_publishers(config)

    assert len(publishers) == 1
    assert isinstance(
        publishers[0],
        MarkdownPublisher,
    )


def test_build_publishers_creates_craft_publisher() -> None:
    config = create_config(
        enabled_publishers=[
            "craft",
        ],
    )

    publishers = build_publishers(config)

    assert len(publishers) == 1
    assert isinstance(
        publishers[0],
        CraftPublisher,
    )
    assert publishers[0].folder_name == "Base de conocimiento"
    assert (
        publishers[0].client.api_url
        == "https://example.craft.do"
    )


def test_build_publishers_supports_multiple_publishers() -> None:
    config = create_config(
        enabled_publishers=[
            "markdown",
            "craft",
        ],
    )

    publishers = build_publishers(config)

    assert len(publishers) == 2
    assert isinstance(
        publishers[0],
        MarkdownPublisher,
    )
    assert isinstance(
        publishers[1],
        CraftPublisher,
    )


def test_build_publishers_allows_empty_selection() -> None:
    config = create_config(
        enabled_publishers=[],
    )

    publishers = build_publishers(config)

    assert publishers == []


def test_build_publishers_requires_craft_api_url() -> None:
    config = AppConfig(
        readwise_token="readwise-token",
        openai_api_key="openai-key",
        enabled_publishers=[
            "craft",
        ],
        craft_api_url=None,
        craft_folder_name="Base de conocimiento",
    )

    with pytest.raises(
        ValueError,
        match="Craft is enabled but craft_api_url is missing",
    ):
        build_publishers(config)


def test_build_publishers_rejects_unknown_publisher() -> None:
    config = create_config(
        enabled_publishers=[
            "unknown",
        ],
    )

    with pytest.raises(
        ValueError,
        match="Unknown publisher: unknown",
    ):
        build_publishers(config)


@patch("kindle_summary_agent.application.SyncService")
@patch("kindle_summary_agent.application.BookDocumentBuilder")
@patch("kindle_summary_agent.application.Summarizer")
@patch("kindle_summary_agent.application.LLMClient")
@patch("kindle_summary_agent.application.ReadwiseClient")
@patch("kindle_summary_agent.application.build_publishers")
def test_build_sync_service_assembles_application(
    mock_build_publishers: Mock,
    mock_readwise_client_class: Mock,
    mock_llm_client_class: Mock,
    mock_summarizer_class: Mock,
    mock_document_builder_class: Mock,
    mock_sync_service_class: Mock,
) -> None:
    config = create_config(
        enabled_publishers=[
            "markdown",
            "craft",
        ],
    )

    publishers = [
        Mock(),
        Mock(),
    ]
    mock_build_publishers.return_value = publishers

    result = build_sync_service(config)

    mock_readwise_client_class.assert_called_once_with(
        token="readwise-token",
    )

    mock_llm_client_class.assert_called_once_with(
        api_key="openai-key",
    )

    mock_summarizer_class.assert_called_once_with(
        llm=mock_llm_client_class.return_value,
    )

    mock_document_builder_class.assert_called_once_with(
        summarizer=mock_summarizer_class.return_value,
    )

    mock_build_publishers.assert_called_once_with(config)

    mock_sync_service_class.assert_called_once_with(
        readwise_client=mock_readwise_client_class.return_value,
        document_builder=mock_document_builder_class.return_value,
        publishers=publishers,
    )

    assert result is mock_sync_service_class.return_value