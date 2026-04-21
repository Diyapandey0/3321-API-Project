# Formats incoming request data into the message dict expected by api_handler.
# input() calls are gone — data now arrives via FastAPI request bodies instead.
# -- Jeremiah Stohel (original) | adapted for FastAPI

from .models import NewChatRequest, ContinueChatRequest


def format_new_chat(request: NewChatRequest) -> dict:
    """
    Builds the message payload for a brand-new conversation.
    Mirrors the `if conversation_history is None` branch of the original FormatInput().
    """
    messages = []

    if request.system_input:
        messages.append({"role": "system", "content": request.system_input})

    messages.append({"role": "user", "content": request.user_text})

    return {
        "messages": messages,
        "temperature": request.temperature,
    }


def format_continued_chat(request: ContinueChatRequest) -> dict:
    """
    Appends the new user message to an existing conversation history.
    Mirrors the `else` branch of the original FormatInput().
    """
    messages = [m.model_dump() for m in request.conversation_history.messages]
    messages.append({"role": "user", "content": request.user_text})

    return {
        "messages": messages,
        "temperature": request.conversation_history.temperature,
    }
