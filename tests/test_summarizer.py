from unittest.mock import Mock, patch

from kindle_summary_agent.clients.llm import SummaryOutput
from kindle_summary_agent.domain.models import Book, Highlight
from kindle_summary_agent.services.summarizer import Summarizer


@patch("kindle_summary_agent.services.summarizer.LLMClient")
def test_summarize_builds_prompt_and_returns_generated_output(
    mock_llm_client_class: Mock,
) -> None:
    generated = SummaryOutput(
        summary="A structured summary.",
        key_ideas=[
            "Small habits compound.",
            "Environment influences behavior.",
        ],
        key_concepts=[
            "Habits",
            "Environment",
        ],
    )

    mock_llm = Mock()
    mock_llm.generate_summary.return_value = generated
    mock_llm_client_class.return_value = mock_llm

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

    summarizer = Summarizer()

    result = summarizer.summarize(book)

    mock_llm.generate_summary.assert_called_once()

    prompt = mock_llm.generate_summary.call_args.args[0]

    assert "Título: Atomic Habits" in prompt
    assert "Autor: James Clear" in prompt
    assert "- Small habits compound over time." in prompt
    assert "Nota del lector: Important idea" in prompt
    assert "- Environment shapes behavior." in prompt

    assert result is generated


@patch("kindle_summary_agent.services.summarizer.LLMClient")
def test_summarize_uses_unknown_author_when_author_is_missing(
    mock_llm_client_class: Mock,
) -> None:
    generated = SummaryOutput(
        summary="Summary.",
        key_ideas=[],
        key_concepts=[],
    )

    mock_llm = Mock()
    mock_llm.generate_summary.return_value = generated
    mock_llm_client_class.return_value = mock_llm

    book = Book(
        title="Book without author",
        highlights=[
            Highlight(text="A useful highlight."),
        ],
    )

    summarizer = Summarizer()

    summarizer.summarize(book)

    prompt = mock_llm.generate_summary.call_args.args[0]

    assert "Título: Book without author" in prompt
    assert "Autor: Desconocido" in prompt


@patch("kindle_summary_agent.services.summarizer.LLMClient")
def test_summarize_ignores_empty_highlights(
    mock_llm_client_class: Mock,
) -> None:
    generated = SummaryOutput(
        summary="Summary.",
        key_ideas=[],
        key_concepts=[],
    )

    mock_llm = Mock()
    mock_llm.generate_summary.return_value = generated
    mock_llm_client_class.return_value = mock_llm

    book = Book(
        title="Test Book",
        author="Test Author",
        highlights=[
            Highlight(text=""),
            Highlight(text="Visible highlight."),
        ],
    )

    summarizer = Summarizer()

    summarizer.summarize(book)

    prompt = mock_llm.generate_summary.call_args.args[0]

    assert "- Visible highlight." in prompt
    assert "\n- \n" not in prompt


@patch("kindle_summary_agent.services.summarizer.LLMClient")
def test_summarizer_loads_expected_prompt_template(
    mock_llm_client_class: Mock,
) -> None:
    mock_llm_client_class.return_value = Mock()

    summarizer = Summarizer()

    assert (
        "Genera un resumen fiel, objetivo y estructurado"
        in summarizer.prompt_template
    )
    assert "{title}" in summarizer.prompt_template
    assert "{author}" in summarizer.prompt_template


def test_uses_llm_passed_to_constructor() -> None:
    llm = Mock()

    summarizer = Summarizer(
        llm=llm,
    )

    assert summarizer.llm is llm