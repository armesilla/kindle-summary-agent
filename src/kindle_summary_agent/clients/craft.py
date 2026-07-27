from typing import Any

import requests

from kindle_summary_agent.config import CRAFT_API_URL


class CraftClient:
    def __init__(self, api_url: str = CRAFT_API_URL) -> None:
        self.api_url = api_url.rstrip("/")

    # -------------------------------------------------------------------------
    # Folders
    # -------------------------------------------------------------------------

    def get_folders(self) -> list[dict[str, Any]]:
        response = requests.get(
            f"{self.api_url}/folders",
            timeout=30,
        )
        response.raise_for_status()

        data = response.json()
        return data.get("items", [])

    def find_folder_by_name(self, name: str) -> dict[str, Any] | None:
        folders = self.get_folders()
        return self._find_folder(folders, name)

    # -------------------------------------------------------------------------
    # Documents
    # -------------------------------------------------------------------------

    def get_documents(
        self,
        folder_id: str,
    ) -> list[dict[str, Any]]:
        response = requests.get(
            f"{self.api_url}/documents",
            params={
                "folderId": folder_id,
            },
            timeout=30,
        )
        response.raise_for_status()

        data = response.json()
        return data.get("items", [])

    def find_document_by_title(
        self,
        title: str,
        folder_id: str,
    ) -> dict[str, Any] | None:
        expected_title = title.casefold()

        for document in self.get_documents(folder_id):
            document_title = str(document.get("title", ""))

            if document_title.casefold() == expected_title:
                return document

        return None

    def create_document(
        self,
        title: str,
        folder_id: str,
    ) -> dict[str, Any]:
        response = requests.post(
            f"{self.api_url}/documents",
            json={
                "documents": [
                    {
                        "title": title,
                    }
                ],
                "destination": {
                    "folderId": folder_id,
                },
            },
            timeout=30,
        )
        response.raise_for_status()

        data = response.json()
        items = data.get("items", [])

        if not items:
            raise RuntimeError("Craft did not return the created document")

        return items[0]

    def delete_document(
        self,
        document_id: str,
    ) -> None:
        response = requests.delete(
            f"{self.api_url}/documents",
            json={
                "documentIds": [
                    document_id,
                ]
            },
            timeout=30,
        )
        response.raise_for_status()

    # -------------------------------------------------------------------------
    # Blocks
    # -------------------------------------------------------------------------

    def get_document_blocks(
        self,
        document_id: str,
    ) -> dict[str, Any]:
        response = requests.get(
            f"{self.api_url}/blocks",
            params={
                "id": document_id,
                "maxDepth": -1,
            },
            headers={
                "Accept": "application/json",
            },
            timeout=30,
        )
        response.raise_for_status()

        return response.json()

    def insert_markdown(
        self,
        document_id: str,
        markdown: str,
    ) -> list[dict[str, Any]]:
        response = requests.post(
            f"{self.api_url}/blocks",
            json={
                "markdown": markdown,
                "position": {
                    "position": "end",
                    "pageId": document_id,
                },
            },
            timeout=30,
        )
        response.raise_for_status()

        data = response.json()
        return data.get("items", [])

    def delete_blocks(
        self,
        block_ids: list[str],
    ) -> None:
        if not block_ids:
            return

        response = requests.delete(
            f"{self.api_url}/blocks",
            json={
                "blockIds": block_ids,
            },
            timeout=30,
        )
        response.raise_for_status()

    def replace_document_content(
        self,
        document_id: str,
        markdown: str,
    ) -> list[dict[str, Any]]:
        document = self.get_document_blocks(document_id)
        content = document.get("content", [])

        block_ids = [str(block["id"]) for block in content if block.get("id")]

        self.delete_blocks(block_ids)

        return self.insert_markdown(
            document_id=document_id,
            markdown=markdown,
        )

    # -------------------------------------------------------------------------
    # Private helpers
    # -------------------------------------------------------------------------

    def _find_folder(
        self,
        folders: list[dict[str, Any]],
        name: str,
    ) -> dict[str, Any] | None:
        expected_name = name.casefold()

        for folder in folders:
            folder_name = str(folder.get("name", ""))

            if folder_name.casefold() == expected_name:
                return folder

            nested_folders = folder.get("folders", [])

            if nested_folders:
                match = self._find_folder(
                    nested_folders,
                    name,
                )

                if match:
                    return match

        return None
