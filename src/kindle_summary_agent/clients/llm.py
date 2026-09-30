import os

from openai import OpenAI
from pydantic import BaseModel, Field


class SummaryOutput(BaseModel):
    summary: str = Field(
        description="Resumen objetivo y fiel basado exclusivamente en los highlights."
    )
    key_ideas: list[str] = Field(
        description="Entre 5 y 10 ideas principales sintetizadas."
    )
    key_concepts: list[str] = Field(
        description="Conceptos, personas, instituciones o términos clave."
    )


class LLMClient:
    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gpt-4.1-mini",
    ) -> None:
        resolved_api_key = api_key or os.getenv("OPENAI_API_KEY")

        if not resolved_api_key:
            raise ValueError("Missing OPENAI_API_KEY")

        self.client = OpenAI(api_key=resolved_api_key)
        self.model = model

    def generate_summary(self, prompt: str) -> SummaryOutput:
        response = self.client.responses.parse(
            model=self.model,
            input=prompt,
            text_format=SummaryOutput,
        )

        if response.output_parsed is None:
            raise RuntimeError("The model did not return a structured summary")

        return response.output_parsed