import os


def get_required_env(name: str) -> str:
    value = os.getenv(name)

    if not value:
        raise ValueError(f"Missing environment variable: {name}")

    return value


CRAFT_API_URL = get_required_env("CRAFT_API_URL")
CRAFT_FOLDER_NAME = os.getenv(
    "CRAFT_FOLDER_NAME",
    "Base de conocimiento",
)
