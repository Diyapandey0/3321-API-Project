from unittest.mock import patch
import pytest
from api_chat.input_handler import FormatInput

def test_new_conversation_basic():
    """No history: should build messages from scratch with user + system."""
    with patch("builtins.input", side_effect=[
        "Hello AI",       # user_text
        "Be concise",     # system_input
        "0.7"             # temperature
    ]):
        result = FormatInput()

    assert result["messages"][0] == {"role": "system", "content": "Be concise"}
    assert result["messages"][1] == {"role": "user", "content": "Hello AI"}
    assert result["temperature"] == 0.7

def test_new_conversation_no_system_input():
    """If user skips system instructions, no system message should be added."""
    with patch("builtins.input", side_effect=[
        "Hello AI",   # user_text
        "",           # system_input skipped
        "1.0"         # temperature
    ]):
        result = FormatInput()

    roles = [m["role"] for m in result["messages"]]
    assert "system" not in roles
    assert result["messages"][0] == {"role": "user", "content": "Hello AI"}
def test_new_conversation_invalid_temperature_defaults_to_1():
    """Non-numeric temperature input should fall back to 1.0."""
    with patch("builtins.input", side_effect=[
        "Hello AI",
        "",
        "hot"          # invalid temperature
    ]):
        result = FormatInput()

    assert result["temperature"] == 1.0
    
def test_new_conversation_empty_temperature_defaults_to_1():
    """Pressing Enter on temperature should default to 1.0."""
    with patch("builtins.input", side_effect=[
        "Hello AI",
        "",
        ""             # empty temperature
    ]):
        result = FormatInput()

    assert result["temperature"] == 1.0


# ── Existing conversation history (follow-up message) ─────────────────────────

def test_existing_history_appends_user_message():
    """With history: should copy existing messages and append new user message."""
    history = {
        "messages": [
            {"role": "system", "content": "Be concise"},
            {"role": "user", "content": "First message"},
            {"role": "assistant", "content": "First reply"}
        ],
        "temperature": 0.5
    }
    with patch("builtins.input", return_value="Follow up question"):
        result = FormatInput(history)

    assert len(result["messages"]) == 4
    assert result["messages"][-1] == {"role": "user", "content": "Follow up question"}

def test_existing_history_preserves_temperature():
    """With history: temperature should be carried over, not re-asked."""
    history = {
        "messages": [{"role": "user", "content": "Hi"}],
        "temperature": 1.5
    }

    with patch("builtins.input", return_value="Next message"):
        result = FormatInput(history)

    assert result["temperature"] == 1.5

def test_existing_history_does_not_mutate_original():
    """FormatInput should not modify the original conversation history dict."""
    history = {
        "messages": [{"role": "user", "content": "Hi"}],
        "temperature": 1.0
    }
    original_length = len(history["messages"])

    with patch("builtins.input", return_value="Follow up"):
        FormatInput(history)

    # Original history should be unchanged
    assert len(history["messages"]) == original_length
