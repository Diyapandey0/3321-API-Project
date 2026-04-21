import pytest
from api_chat.input_handler import format_new_chat, format_continued_chat
from api_chat.models import NewChatRequest, ContinueChatRequest, ConversationHistory, Message


# ── format_new_chat ────────────────────────────────────────────────────────────

def test_new_chat_includes_system_and_user():
    """System input present: system message should come first, then user."""
    request = NewChatRequest(
        user_text="Hello AI",
        system_input="Be concise",
        temperature=0.7,
    )
    result = format_new_chat(request)

    assert result["messages"][0] == {"role": "system", "content": "Be concise"}
    assert result["messages"][1] == {"role": "user", "content": "Hello AI"}
    assert result["temperature"] == 0.7


def test_new_chat_no_system_input():
    """Omitting system_input should produce only a user message."""
    request = NewChatRequest(user_text="Hello AI")
    result = format_new_chat(request)

    roles = [m["role"] for m in result["messages"]]
    assert "system" not in roles
    assert result["messages"][0] == {"role": "user", "content": "Hello AI"}


def test_new_chat_default_temperature():
    """Temperature should default to 1.0 when not supplied."""
    request = NewChatRequest(user_text="Hello AI")
    result = format_new_chat(request)

    assert result["temperature"] == 1.0


def test_new_chat_custom_temperature():
    """Explicitly supplied temperature should be preserved in the payload."""
    request = NewChatRequest(user_text="Hello AI", temperature=0.3)
    result = format_new_chat(request)

    assert result["temperature"] == 0.3


# ── format_continued_chat ──────────────────────────────────────────────────────

def test_continued_chat_appends_user_message():
    """Existing history: new user message should be appended at the end."""
    history = ConversationHistory(
        messages=[
            Message(role="system", content="Be concise"),
            Message(role="user", content="First message"),
            Message(role="assistant", content="First reply"),
        ],
        temperature=0.5,
    )
    request = ContinueChatRequest(conversation_history=history, user_text="Follow up")
    result = format_continued_chat(request)

    assert len(result["messages"]) == 4
    assert result["messages"][-1] == {"role": "user", "content": "Follow up"}


def test_continued_chat_preserves_temperature():
    """Temperature should be taken from conversation history, not re-asked."""
    history = ConversationHistory(
        messages=[Message(role="user", content="Hi")],
        temperature=1.5,
    )
    request = ContinueChatRequest(conversation_history=history, user_text="Next message")
    result = format_continued_chat(request)

    assert result["temperature"] == 1.5


def test_continued_chat_does_not_mutate_history():
    """format_continued_chat should not modify the original ConversationHistory object."""
    history = ConversationHistory(
        messages=[Message(role="user", content="Hi")],
        temperature=1.0,
    )
    original_length = len(history.messages)
    request = ContinueChatRequest(conversation_history=history, user_text="Follow up")
    format_continued_chat(request)

    assert len(history.messages) == original_length