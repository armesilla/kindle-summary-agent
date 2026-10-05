from collections.abc import Callable

from kindle_summary_agent.app_config import AppConfig
from kindle_summary_agent.clients.craft import CraftClient
from kindle_summary_agent.clients.llm import LLMClient
from kindle_summary_agent.clients.readwise import ReadwiseClient
from kindle_summary_agent.publishers.base import Publisher
from kindle_summary_agent.publishers.craft import CraftPublisher
from kindle_summary_agent.publishers.markdown import MarkdownPublisher
from kindle_summary_agent.services.document_builder import BookDocumentBuilder
from kindle_summary_agent.services.summarizer import Summarizer
from kindle_summary_agent.services.sync import SyncService
from kindle_summary_agent.services.sync_event import SyncEvent


ProgressCallback = Callable[[SyncEvent], None]


def build_publishers(config: AppConfig) -> list[Publisher]:
    publishers: list[Publisher] = []

    for publisher_name in config.enabled_publishers:
        if publisher_name == "markdown":
            publishers.append(
                MarkdownPublisher()
            )
            continue

        if publisher_name == "craft":
            if not config.craft_api_url:
                raise ValueError(
                    "Craft is enabled but craft_api_url is missing"
                )

            craft_client = CraftClient(
                api_url=config.craft_api_url,
            )

            craft_publisher = CraftPublisher(
                client=craft_client,
                folder_name=(
                    config.craft_folder_name
                    or "Base de conocimiento"
                ),
            )

            publishers.append(craft_publisher)
            continue

        raise ValueError(
            f"Unknown publisher: {publisher_name}"
        )

    return publishers


def build_sync_service(
    config: AppConfig,
    progress_callback: ProgressCallback | None = None,
) -> SyncService:
    readwise_client = ReadwiseClient(
        token=config.readwise_token,
    )

    llm_client = LLMClient(
        api_key=config.openai_api_key,
    )

    summarizer = Summarizer(
        llm=llm_client,
    )

    document_builder = BookDocumentBuilder(
        summarizer=summarizer,
    )

    publishers = build_publishers(config)

    return SyncService(
        readwise_client=readwise_client,
        document_builder=document_builder,
        publishers=publishers,
        progress_callback=progress_callback,
    )