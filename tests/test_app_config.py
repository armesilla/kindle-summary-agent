import pytest

from kindle_summary_agent.app_config import AppConfig


def test_app_config_stores_required_values() -> None:
    config = AppConfig(
        readwise_token="readwise-token",
        openai_api_key="openai-key",
    )

    assert config.readwise_token == "readwise-token"
    assert config.openai_api_key == "openai-key"


def test_app_config_uses_empty_publishers_by_default() -> None:
    config = AppConfig(
        readwise_token="readwise-token",
        openai_api_key="openai-key",
    )

    assert config.enabled_publishers == []


def test_app_config_accepts_optional_craft_configuration() -> None:
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

    assert config.enabled_publishers == [
        "markdown",
        "craft",
    ]
    assert config.craft_api_url == "https://example.craft.do"
    assert config.craft_folder_name == "Base de conocimiento"


def test_from_environment_builds_config(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "READWISE_TOKEN",
        "environment-readwise-token",
    )
    monkeypatch.setenv(
        "OPENAI_API_KEY",
        "environment-openai-key",
    )
    monkeypatch.setenv(
        "CRAFT_API_URL",
        "https://environment.craft.do",
    )
    monkeypatch.setenv(
        "CRAFT_FOLDER_NAME",
        "My Craft Folder",
    )

    config = AppConfig.from_environment()

    assert config.readwise_token == "environment-readwise-token"
    assert config.openai_api_key == "environment-openai-key"
    assert config.enabled_publishers == [
        "markdown",
        "craft",
    ]
    assert config.craft_api_url == "https://environment.craft.do"
    assert config.craft_folder_name == "My Craft Folder"


def test_from_environment_uses_default_craft_folder(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "READWISE_TOKEN",
        "readwise-token",
    )
    monkeypatch.setenv(
        "OPENAI_API_KEY",
        "openai-key",
    )
    monkeypatch.setenv(
        "CRAFT_API_URL",
        "https://example.craft.do",
    )
    monkeypatch.delenv(
        "CRAFT_FOLDER_NAME",
        raising=False,
    )

    config = AppConfig.from_environment()

    assert config.craft_folder_name == "Base de conocimiento"


def test_from_environment_requires_readwise_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv(
        "READWISE_TOKEN",
        raising=False,
    )
    monkeypatch.setenv(
        "OPENAI_API_KEY",
        "openai-key",
    )
    monkeypatch.setenv(
        "CRAFT_API_URL",
        "https://example.craft.do",
    )

    with pytest.raises(
        ValueError,
        match="Missing READWISE_TOKEN",
    ):
        AppConfig.from_environment()


def test_from_environment_requires_openai_api_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "READWISE_TOKEN",
        "readwise-token",
    )
    monkeypatch.delenv(
        "OPENAI_API_KEY",
        raising=False,
    )
    monkeypatch.setenv(
        "CRAFT_API_URL",
        "https://example.craft.do",
    )

    with pytest.raises(
        ValueError,
        match="Missing OPENAI_API_KEY",
    ):
        AppConfig.from_environment()


def test_from_environment_requires_craft_api_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "READWISE_TOKEN",
        "readwise-token",
    )
    monkeypatch.setenv(
        "OPENAI_API_KEY",
        "openai-key",
    )
    monkeypatch.delenv(
        "CRAFT_API_URL",
        raising=False,
    )

    with pytest.raises(
        ValueError,
        match="Missing CRAFT_API_URL",
    ):
        AppConfig.from_environment()