from typing import Any, Protocol

from kindle_summary_agent.domain.models import BookDocument


class Publisher(Protocol):
    def publish(self, document: BookDocument) -> Any:
        ...