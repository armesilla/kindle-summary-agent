from dataclasses import dataclass, field


@dataclass
class AppConfig:
    readwise_token: str
    openai_api_key: str
    enabled_publishers: list[str] = field(default_factory=list)
    craft_api_url: str | None = None
    craft_folder_name: str | None = None