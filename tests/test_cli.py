from unittest.mock import Mock, patch

from kindle_summary_agent.app_config import AppConfig
from kindle_summary_agent.cli import (
    create_parser,
    run_sync,
)
from kindle_summary_agent.services.sync_result import SyncResult


def test_parser_accepts_sync_command() -> None:
    parser = create_parser()

    arguments = parser.parse_args(
        [
            "sync",
        ]
    )

    assert arguments.command == "sync"


def test_parser_accepts_book_command_with_query() -> None:
    parser = create_parser()

    arguments = parser.parse_args(
        [
            "book",
            "--query",
            "Atomic Habits",
        ]
    )

    assert arguments.command == "book"
    assert arguments.query == "Atomic Habits"


@patch("kindle_summary_agent.cli.build_sync_service")
@patch("kindle_summary_agent.cli.AppConfig.from_environment")
def test_run_sync_uses_shared_application_assembly(
    mock_from_environment: Mock,
    mock_build_sync_service: Mock,
    capsys,
) -> None:
    config = AppConfig(
        readwise_token="readwise-token",
        openai_api_key="openai-key",
        enabled_publishers=[
            "markdown",
            "craft",
        ],
        craft_api_url="https://example.craft.do",
        craft_folder_name="Base de conocimiento",
    )

    mock_from_environment.return_value = config

    service = Mock()
    service.readwise_client.validate.return_value = True
    service.run.return_value = SyncResult(
        processed_books=2,
    )

    mock_build_sync_service.return_value = service

    run_sync()

    mock_from_environment.assert_called_once_with()
    mock_build_sync_service.assert_called_once_with(config)
    service.readwise_client.validate.assert_called_once_with()
    service.run.assert_called_once_with()

    output = capsys.readouterr().out

    assert "Token de Readwise válido" in output
    assert "Libros procesados: 2" in output


@patch("kindle_summary_agent.cli.build_sync_service")
@patch("kindle_summary_agent.cli.AppConfig.from_environment")
def test_run_sync_raises_error_when_readwise_token_is_invalid(
    mock_from_environment: Mock,
    mock_build_sync_service: Mock,
) -> None:
    config = AppConfig(
        readwise_token="readwise-token",
        openai_api_key="openai-key",
        enabled_publishers=[
            "markdown",
            "craft",
        ],
        craft_api_url="https://example.craft.do",
        craft_folder_name="Base de conocimiento",
    )

    mock_from_environment.return_value = config

    service = Mock()
    service.readwise_client.validate.return_value = False

    mock_build_sync_service.return_value = service

    try:
        run_sync()
    except RuntimeError as error:
        assert str(error) == "Invalid Readwise token"
    else:
        raise AssertionError(
            "run_sync() should raise RuntimeError"
        )

    service.run.assert_not_called()