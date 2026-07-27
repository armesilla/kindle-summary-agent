from datetime import datetime
from typing import Any

import requests

from kindle_summary_agent.domain.models import Book, Highlight

BASE_URL = "https://readwise.io/api/v2"


class ReadwiseClient:
    def __init__(self, token: str | None = None) -> None:
        import os

        self.token = token or os.getenv("READWISE_TOKEN")

        if not self.token:
            raise ValueError("Missing READWISE_TOKEN")

        self.headers = {
            "Authorization": f"Token {self.token}",
        }

    def validate(self) -> bool:
        response = requests.get(
            f"{BASE_URL}/auth/",
            headers=self.headers,
            timeout=30,
        )

        return response.status_code == 204

    def get_books(
        self,
        updated_after: datetime | None = None,
    ) -> list[Book]:
        if updated_after is None:
            items = self._export()
            return self._parse_books(items)

        changed_items = self._export(
            updated_after=updated_after,
            include_deleted=True,
        )

        changed_book_ids = self._extract_book_ids(changed_items)

        if not changed_book_ids:
            return []

        complete_items = self._export(
            book_ids=changed_book_ids,
        )

        return self._parse_books(complete_items)

    def _export(
        self,
        updated_after: datetime | None = None,
        book_ids: list[int] | None = None,
        include_deleted: bool = False,
    ) -> list[dict[str, Any]]:
        params: dict[str, str] = {}

        if updated_after is not None:
            params["updatedAfter"] = updated_after.isoformat()

        if book_ids:
            params["ids"] = ",".join(str(book_id) for book_id in book_ids)

        if include_deleted:
            params["includeDeleted"] = "true"

        results: list[dict[str, Any]] = []
        page_cursor: str | None = None

        while True:
            page_params = dict(params)

            if page_cursor:
                page_params["pageCursor"] = page_cursor

            response = requests.get(
                f"{BASE_URL}/export/",
                headers=self.headers,
                params=page_params,
                timeout=30,
            )
            response.raise_for_status()

            data = response.json()
            results.extend(data.get("results", []))

            page_cursor = data.get("nextPageCursor")

            if not page_cursor:
                break

        return results

    def _extract_book_ids(
        self,
        items: list[dict[str, Any]],
    ) -> list[int]:
        book_ids: set[int] = set()

        for item in items:
            raw_id = item.get("user_book_id")

            if raw_id is None:
                raw_id = item.get("id")

            if raw_id is None:
                continue

            book_ids.add(int(raw_id))

        return sorted(book_ids)

    def _parse_books(
        self,
        items: list[dict[str, Any]],
    ) -> list[Book]:
        books: list[Book] = []

        for item in items:
            highlights = [
                Highlight(
                    text=str(highlight.get("text", "")),
                    note=highlight.get("note"),
                    location=self._normalize_location(highlight.get("location")),
                )
                for highlight in item.get("highlights", [])
                if not highlight.get("is_deleted", False)
            ]

            books.append(
                Book(
                    title=str(item.get("title") or "Untitled"),
                    author=item.get("author"),
                    highlights=highlights,
                )
            )

        return books

    def _normalize_location(
        self,
        location: Any,
    ) -> str | None:
        if location is None:
            return None

        return str(location)
