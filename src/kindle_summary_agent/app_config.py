import os
from dataclasses import dataclass, field


@dataclass
class AppConfig:
    readwise_token: str
    openai_api_key: str
    enabled_publishers: list[str] = field(default_factory=list)
    craft_api_url: str | None = None
    craft_folder_name: str | None = None

    @classmethod
    def from_environment(cls) -> "AppConfig":
        readwise_token = os.getenv("READWISE_TOKEN")
        openai_api_key = os.getenv("OPENAI_API_KEY")
        craft_api_url = os.getenv("CRAFT_API_URL")
        craft_folder_name = os.getenv(
            "CRAFT_FOLDER_NAME",
            "Base de conocimiento",
        )

        if not readwise_token:
            raise ValueError("Missing READWISE_TOKEN")

        if not openai_api_key:
            raise ValueError("Missing OPENAI_API_KEY")

        if not craft_api_url:
            raise ValueError("Missing CRAFT_API_URL")

        return cls(
            readwise_token=readwise_token,
            openai_api_key=openai_api_key,
            enabled_publishers=[
                "markdown",
                "craft",
            ],
            craft_api_url=craft_api_url,
            craft_folder_name=craft_folder_name,
        )