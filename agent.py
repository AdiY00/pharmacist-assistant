import os
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any, Literal, cast

from openai import AsyncOpenAI
from openai.types.responses import (
    EasyInputMessageParam,
    ResponseInputItemParam,
    ToolParam,
)

from tools import (
    BaseTool,
    GetMedicationsByIngredient,
    GetMedicationStock,
    LoadPrescriptions,
    ReserveMedications,
)

MODEL = os.getenv("OPENAI_MODEL", "gpt-5")
REASONING_EFFORT: Any = os.getenv("REASONING_EFFORT", "low")

client = AsyncOpenAI()

SYSTEM_PROMPT = "You are a helpful pharmacist assistant."

# Register all tools here
TOOLS: list[type[BaseTool]] = [
    GetMedicationStock,
    GetMedicationsByIngredient,
    LoadPrescriptions,
    ReserveMedications,
]


def _get_tools_schema() -> list[ToolParam]:
    """Get OpenAI schema for all registered tools."""
    return cast(list[ToolParam], [tool.to_openai_schema() for tool in TOOLS])


def _execute_tool(name: str, arguments: str) -> str:
    """Execute a tool by name."""
    for tool in TOOLS:
        if tool.name() == name:
            return tool.run(arguments)
    return '{"error": "Unknown tool: ' + name + '"}'


@dataclass
class StreamEvent:
    """Event emitted during streaming."""

    type: Literal["reasoning", "reasoning_end", "text", "tool_call"]
    content: str
    tool_name: str | None = None
    tool_result: str | None = None


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
    input_messages: list[Any] = _convert_messages(messages)

    while True:
        stream = await client.responses.create(
            model=MODEL,
            instructions=SYSTEM_PROMPT,
            input=input_messages,
            tools=_get_tools_schema(),
            reasoning={
                "effort": REASONING_EFFORT,
                "summary": "auto",
            },
            stream=True,
        )

        function_calls: dict[str, dict[str, str]] = {}
        has_reasoning = False

        async for event in stream:
            if event.type == "response.reasoning_summary_text.delta":
                has_reasoning = True
                yield StreamEvent(type="reasoning", content=event.delta)
            elif event.type == "response.output_text.delta":
                yield StreamEvent(type="text", content=event.delta)
            elif event.type == "response.function_call_arguments.delta":
                call_id = event.item_id
                if call_id and call_id not in function_calls:
                    function_calls[call_id] = {"name": "", "arguments": ""}
                if call_id:
                    function_calls[call_id]["arguments"] += event.delta
            elif event.type == "response.output_item.added":
                if event.item.type == "function_call":
                    # Signal end of reasoning before tool calls
                    if has_reasoning:
                        yield StreamEvent(type="reasoning_end", content="")
                        has_reasoning = False
                    call_id = event.item.id
                    if call_id:
                        function_calls[call_id] = {
                            "name": event.item.name,
                            "arguments": "",
                        }

        # Signal end of reasoning if we had reasoning but no tool calls
        if has_reasoning:
            yield StreamEvent(type="reasoning_end", content="")

        # If no function calls, we're done
        if not function_calls:
            break

        # Execute function calls and add to conversation for next iteration
        for call_id, call_info in function_calls.items():
            result = _execute_tool(call_info["name"], call_info["arguments"])

            # Emit tool call event
            yield StreamEvent(
                type="tool_call",
                content=call_info["arguments"],
                tool_name=call_info["name"],
                tool_result=result,
            )

            # Add the function call itself
            input_messages.append(
                {
                    "type": "function_call",
                    "call_id": call_id,
                    "name": call_info["name"],
                    "arguments": call_info["arguments"],
                }
            )
            # Add the function call output
            input_messages.append(
                {
                    "type": "function_call_output",
                    "call_id": call_id,
                    "output": result,
                }
            )
