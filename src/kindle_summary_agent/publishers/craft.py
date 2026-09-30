import os
from typing import Any

from kindle_summary_agent.clients.craft import CraftClient
from kindle_summary_agent.domain.models import BookDocument, Highlight


class CraftPublisher:
    def __init__(
        self,
        client: CraftClient | None = None,
        folder_name: str | None = None,
    ) -> None:
        resolved_folder_name = folder_name or os.getenv(
            "CRAFT_FOLDER_NAME",
            "Base de conocimiento",
        )

        self.client = client or CraftClient()
        self.folder_name = resolved_folder_name

    def publish(self, document: BookDocument) -> dict[str, Any]:
        folder = self.client.find_folder_by_name(self.folder_name)

        if folder is None:
            raise RuntimeError(f"Craft folder not found: {self.folder_name}")

        folder_id = str(folder["id"])
        title = document.book.title
        markdown = self._render(document)

        matches = self._find_documents_by_title(
            title=title,
            folder_id=folder_id,
        )

        if len(matches) > 1:
            raise RuntimeError(
                f"Multiple Craft documents found with title: {title}"
            )

        if matches:
            craft_document = matches[0]

            self.client.replace_document_content(
                document_id=str(craft_document["id"]),
                markdown=markdown,
            )

            return craft_document

        craft_document = self.client.create_document(
            title=title,
            folder_id=folder_id,
        )

        self.client.insert_markdown(
            document_id=str(craft_document["id"]),
            markdown=markdown,
        )

        return craft_document

    def _find_documents_by_title(
        self,
        title: str,
        folder_id: str,
    ) -> list[dict[str, Any]]:
        expected_title = title.casefold()

        return [
            document
            for document in self.client.get_documents(folder_id)
            if str(document.get("title", "")).casefold() == expected_title
        ]

    def _render(self, document: BookDocument) -> str:
        book = document.book

        key_ideas = "\n".join(f"- {idea}" for idea in document.key_ideas)

        key_concepts = "\n".join(
            f"- {concept}" for concept in document.key_concepts
        )

        highlights = "\n".join(
            self._render_highlight(highlight)
            for highlight in book.highlights
            if highlight.text
        )

        return f"""## Información

- Autor: {book.author or "Desconocido"}
- Highlights: {book.highlight_count}

## Resumen

{document.summary}

## Ideas principales

{key_ideas}

## Conceptos clave

{key_concepts}

## Highlights

{highlights}
"""

    def _render_highlight(self, highlight: Highlight) -> str:
        content = f"- {highlight.text}"

        if highlight.note:
            content += f"\n  - Nota: {highlight.note}"

        return content