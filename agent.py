import os
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any, Literal

from openai import AsyncOpenAI
from openai.types.responses import EasyInputMessageParam, ResponseInputItemParam

MODEL = os.getenv("OPENAI_MODEL", "gpt-5")
REASONING_EFFORT: Any = os.getenv("REASONING_EFFORT", "low")

client = AsyncOpenAI()

SYSTEM_PROMPT = "You are a helpful pharmacist assistant."


@dataclass
class StreamEvent:
    """Event emitted during streaming."""

    type: Literal["reasoning", "text"]
    content: str


def _convert_messages(
    messages: list[dict[str, str]],
) -> list[ResponseInputItemParam | EasyInputMessageParam]:
    """Convert chat format messages to Responses API format."""
    result: list[ResponseInputItemParam | EasyInputMessageParam] = []
    for msg in messages:
        role = msg["role"]
        content = msg["content"]

        if role == "user":
            result.append({"role": "user", "content": content})
        elif role == "assistant":
            result.append({"role": "assistant", "content": content})

    return result


async def chat(messages: list[dict[str, str]]) -> AsyncIterator[StreamEvent]:
    """
    Stream a chat completion response from OpenAI using the Responses API.

    Args:
        messages: Conversation history (user and assistant messages).

    Yields:
        StreamEvent objects containing either reasoning or text content.
    """
    converted_messages = _convert_messages(messages)

    stream = await client.responses.create(
        model=MODEL,
        instructions=SYSTEM_PROMPT,
        input=converted_messages,
        reasoning={
            "effort": REASONING_EFFORT,
            "summary": "auto",
        },
        stream=True,
    )

    async for event in stream:
        if event.type == "response.reasoning_summary_text.delta":
            yield StreamEvent(type="reasoning", content=event.delta)
        elif event.type == "response.output_text.delta":
            yield StreamEvent(type="text", content=event.delta)
