import chainlit as cl

from agent import InputMessage, StreamEvent, chat


@cl.on_chat_start
async def on_chat_start() -> None:
    """Initialize conversation history when a new chat starts."""
    cl.user_session.set("messages", [])


@cl.on_message
async def on_message(message: cl.Message) -> None:
    """Handle incoming user messages."""
    messages: list[InputMessage] = cl.user_session.get("messages") or []

    messages.append({"role": "user", "content": message.content})

    text_events: list[StreamEvent] = []
    thinking_step: cl.Step | None = None
    final_messages: list[InputMessage] = messages

    async for event in chat(messages):
        if event.type == "reasoning":
            # Start thinking step if not already started
            if thinking_step is None:
                thinking_step = cl.Step(
                    name="💭 Thinking...", type="llm", show_input=False
                )
                await thinking_step.__aenter__()
            await thinking_step.stream_token(event.content)

        elif event.type == "reasoning_end":
            # Close thinking step when reasoning ends
            if thinking_step is not None:
                await thinking_step.__aexit__(None, None, None)
                thinking_step = None

        elif event.type == "tool_call":
            # Tool calls appear at the same level as thinking
            async with cl.Step(name=event.tool_name, type="tool") as tool_step:
                tool_step.input = event.content
                tool_step.output = event.tool_result or ""

        elif event.type == "text":
            text_events.append(event)

        elif event.type == "done":
            # Capture the final messages including tool calls
            if event.messages:
                final_messages = event.messages

    # Ensure thinking step is closed if it was still open
    if thinking_step is not None:
        await thinking_step.__aexit__(None, None, None)

    # Stream the text response
    msg = cl.Message(content="")
    await msg.send()

    full_response = ""
    for event in text_events:
        full_response += event.content
        await msg.stream_token(event.content)

    await msg.update()

    # Add the assistant's text response to messages
    final_messages.append({"role": "assistant", "content": full_response})

    cl.user_session.set("messages", final_messages)
