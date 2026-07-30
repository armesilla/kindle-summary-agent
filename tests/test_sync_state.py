import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from kindle_summary_agent.services.sync_state import SyncState


def test_returns_none_when_state_file_does_not_exist(tmp_path: Path) -> None:
    state = SyncState(state_path=str(tmp_path / "sync.json"))

    assert state.get_last_successful_sync() is None


def test_mark_successful_sync_creates_state_file(tmp_path: Path) -> None:
    state_path = tmp_path / "sync.json"
    state = SyncState(state_path=str(state_path))

    timestamp = datetime(
        2026,
        7,
        30,
        8,
        0,
        tzinfo=timezone.utc,
    )

    returned = state.mark_successful_sync(timestamp)

    assert returned == timestamp
    assert state_path.exists()

    data = json.loads(state_path.read_text(encoding="utf-8"))

    assert data == {
        "last_successful_sync": timestamp.isoformat(),
    }


def test_reads_last_successful_sync(tmp_path: Path) -> None:
    timestamp = datetime(
        2026,
        7,
        30,
        8,
        0,
        tzinfo=timezone.utc,
    )

    state_path = tmp_path / "sync.json"

    state_path.write_text(
        json.dumps(
            {
                "last_successful_sync": timestamp.isoformat(),
            }
        ),
        encoding="utf-8",
    )

    state = SyncState(state_path=str(state_path))

    assert state.get_last_successful_sync() == timestamp


def test_clear_removes_state_file(tmp_path: Path) -> None:
    state_path = tmp_path / "sync.json"

    state_path.write_text(
        "{}",
        encoding="utf-8",
    )

    state = SyncState(state_path=str(state_path))

    state.clear()

    assert not state_path.exists()


def test_invalid_json_raises_runtime_error(tmp_path: Path) -> None:
    state_path = tmp_path / "sync.json"

    state_path.write_text(
        "{invalid json",
        encoding="utf-8",
    )

    state = SyncState(state_path=str(state_path))

    with pytest.raises(RuntimeError, match="Invalid JSON"):
        state.get_last_successful_sync()


def test_invalid_date_raises_runtime_error(tmp_path: Path) -> None:
    state_path = tmp_path / "sync.json"

    state_path.write_text(
        json.dumps(
            {
                "last_successful_sync": "not-a-date",
            }
        ),
        encoding="utf-8",
    )

    state = SyncState(state_path=str(state_path))

    with pytest.raises(RuntimeError, match="Invalid synchronization date"):
        state.get_last_successful_sync()


def test_naive_datetime_is_converted_to_utc(tmp_path: Path) -> None:
    timestamp = datetime(
        2026,
        7,
        30,
        8,
        0,
    )

    state = SyncState(state_path=str(tmp_path / "sync.json"))

    state.mark_successful_sync(timestamp)

    loaded = state.get_last_successful_sync()

    assert loaded == datetime(
        2026,
        7,
        30,
        8,
        0,
        tzinfo=timezone.utc,
    )