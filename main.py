import chainlit as cl

from agent import StreamEvent, chat


@cl.on_chat_start
async def on_chat_start() -> None:
    """Initialize conversation history when a new chat starts."""
    cl.user_session.set("messages", [])


@cl.step(name="Thinking...", type="llm", show_input=False)
async def thinking_step(messages: list[dict[str, str]]) -> list[StreamEvent]:
    """Process reasoning events and return text events for later streaming."""
    current_step = cl.context.current_step
    text_events: list[StreamEvent] = []

    async for event in chat(messages):
        if event.type == "reasoning":
            await current_step.stream_token(event.content)
        elif event.type == "text":
            text_events.append(event)

    return text_events


@cl.on_message
async def on_message(message: cl.Message) -> None:
    """Handle incoming user messages."""
    messages: list[dict[str, str]] = cl.user_session.get("messages", [])

    messages.append({"role": "user", "content": message.content})

    # First: run thinking step (streams reasoning, collects text events)
    text_events = await thinking_step(messages)

    # Second: stream the text response
    msg = cl.Message(content="")
    await msg.send()

    full_response = ""
    for event in text_events:
        full_response += event.content
        await msg.stream_token(event.content)

    await msg.update()

    messages.append({"role": "assistant", "content": full_response})
