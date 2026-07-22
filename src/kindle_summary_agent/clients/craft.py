from typing import Any

import requests

from kindle_summary_agent.config import CRAFT_API_URL


class CraftClient:
    def __init__(self, api_url: str = CRAFT_API_URL) -> None:
        self.api_url = api_url.rstrip("/")

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

    def delete_document(self, document_id: str) -> None:
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
