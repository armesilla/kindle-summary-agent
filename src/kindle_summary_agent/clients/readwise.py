import os

import requests

from kindle_summary_agent.domain.models import Book, Highlight

BASE_URL = "https://readwise.io/api/v2"


class ReadwiseClient:
    def __init__(self, token: str | None = None):
        self.token = token or os.getenv("READWISE_TOKEN")

        if not self.token:
            raise ValueError("Missing READWISE_TOKEN")

        self.headers = {"Authorization": f"Token {self.token}"}

    def validate(self) -> bool:
        response = requests.get(
            f"{BASE_URL}/auth/",
            headers=self.headers,
            timeout=30,
        )
        return response.status_code == 204

    def get_books(self) -> list[Book]:
        response = requests.get(
            f"{BASE_URL}/export/",
            headers=self.headers,
            timeout=30,
        )
        response.raise_for_status()

        books = []

        for item in response.json()["results"]:
            highlights = [
                Highlight(
                    text=highlight.get("text", ""),
                    note=highlight.get("note"),
                    location=highlight.get("location"),
                )
                for highlight in item.get("highlights", [])
            ]

            books.append(
                Book(
                    title=item.get("title", "Untitled"),
                    author=item.get("author"),
                    highlights=highlights,
                )
            )

        return books
