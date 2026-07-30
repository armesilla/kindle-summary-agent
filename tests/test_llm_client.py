from unittest.mock import Mock, patch

import pytest

from kindle_summary_agent.clients.llm import LLMClient, SummaryOutput


def test_raises_error_when_openai_api_key_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(
        ValueError,
        match="Missing OPENAI_API_KEY",
    ):
        LLMClient()


@patch("kindle_summary_agent.clients.llm.OpenAI")
def test_creates_openai_client_with_environment_api_key(
    mock_openai_class: Mock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "OPENAI_API_KEY",
        "test-api-key",
    )

    client = LLMClient()

    mock_openai_class.assert_called_once_with(
        api_key="test-api-key",
    )

    assert client.client is mock_openai_class.return_value
    assert client.model == "gpt-4.1-mini"


@patch("kindle_summary_agent.clients.llm.OpenAI")
def test_uses_custom_model(
    mock_openai_class: Mock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "OPENAI_API_KEY",
        "test-api-key",
    )

    client = LLMClient(
        model="gpt-test-model",
    )

    assert client.model == "gpt-test-model"


@patch("kindle_summary_agent.clients.llm.OpenAI")
def test_generate_summary_returns_structured_output(
    mock_openai_class: Mock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "OPENAI_API_KEY",
        "test-api-key",
    )

    generated = SummaryOutput(
        summary="A structured summary.",
        key_ideas=[
            "Idea one",
            "Idea two",
        ],
        key_concepts=[
            "Concept one",
            "Concept two",
        ],
    )

    response = Mock()
    response.output_parsed = generated

    mock_openai_client = mock_openai_class.return_value
    mock_openai_client.responses.parse.return_value = response

    client = LLMClient(
        model="gpt-test-model",
    )

    result = client.generate_summary(
        "Test prompt",
    )

    mock_openai_client.responses.parse.assert_called_once_with(
        model="gpt-test-model",
        input="Test prompt",
        text_format=SummaryOutput,
    )

    assert result is generated


@patch("kindle_summary_agent.clients.llm.OpenAI")
def test_generate_summary_raises_error_when_output_is_missing(
    mock_openai_class: Mock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "OPENAI_API_KEY",
        "test-api-key",
    )

    response = Mock()
    response.output_parsed = None

    mock_openai_client = mock_openai_class.return_value
    mock_openai_client.responses.parse.return_value = response

    client = LLMClient()

    with pytest.raises(
        RuntimeError,
        match="The model did not return a structured summary",
    ):
        client.generate_summary(
            "Test prompt",
        )