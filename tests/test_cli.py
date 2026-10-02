from kindle_summary_agent.cli import create_parser


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