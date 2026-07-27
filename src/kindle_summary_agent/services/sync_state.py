import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class SyncState:
    def __init__(self, state_path: str = ".state/sync.json") -> None:
        self.state_path = Path(state_path)

    def get_last_successful_sync(self) -> datetime | None:
        data = self._read()

        value = data.get("last_successful_sync")

        if not value:
            return None

        try:
            parsed = datetime.fromisoformat(str(value))
        except ValueError as error:
            raise RuntimeError(
                f"Invalid synchronization date in {self.state_path}"
            ) from error

        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)

        return parsed.astimezone(timezone.utc)

    def mark_successful_sync(
        self,
        synchronized_at: datetime | None = None,
    ) -> datetime:
        timestamp = synchronized_at or datetime.now(timezone.utc)

        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)

        timestamp = timestamp.astimezone(timezone.utc)

        self._write(
            {
                "last_successful_sync": timestamp.isoformat(),
            }
        )

        return timestamp

    def clear(self) -> None:
        if self.state_path.exists():
            self.state_path.unlink()

        parent = self.state_path.parent

        if parent.exists() and not any(parent.iterdir()):
            parent.rmdir()

    def _read(self) -> dict[str, Any]:
        if not self.state_path.exists():
            return {}

        try:
            content = self.state_path.read_text(encoding="utf-8")
            data = json.loads(content)
        except json.JSONDecodeError as error:
            raise RuntimeError(
                f"Invalid JSON in synchronization state: {self.state_path}"
            ) from error
        except OSError as error:
            raise RuntimeError(
                f"Could not read synchronization state: {self.state_path}"
            ) from error

        if not isinstance(data, dict):
            raise RuntimeError(
                f"Synchronization state must be a JSON object: {self.state_path}"
            )

        return data

    def _write(self, data: dict[str, Any]) -> None:
        self.state_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        temporary_path = self.state_path.with_suffix(".tmp")

        try:
            temporary_path.write_text(
                json.dumps(
                    data,
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            temporary_path.replace(self.state_path)
        except OSError as error:
            if temporary_path.exists():
                temporary_path.unlink()

            raise RuntimeError(
                f"Could not write synchronization state: {self.state_path}"
            ) from error
