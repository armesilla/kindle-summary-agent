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