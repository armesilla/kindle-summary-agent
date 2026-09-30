from unittest.mock import patch

import pytest

from kindle_summary_agent.clients.craft import CraftClient


def test_raises_error_when_craft_api_url_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("CRAFT_API_URL", raising=False)

    with pytest.raises(
        ValueError,
        match="Missing CRAFT_API_URL",
    ):
        CraftClient()


def test_uses_api_url_passed_to_constructor() -> None:
    client = CraftClient(
        api_url="https://example.craft.do/",
    )

    assert client.api_url == "https://example.craft.do"


@patch.dict(
    "os.environ",
    {
        "CRAFT_API_URL": "https://environment.craft.do/",
    },
)
def test_uses_api_url_from_environment() -> None:
    client = CraftClient()

    assert client.api_url == "https://environment.craft.do"