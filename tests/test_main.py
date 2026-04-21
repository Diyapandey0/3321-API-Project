import sys
from pathlib import Path
from unittest.mock import patch, AsyncMock, MagicMock

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from api_chat.main import app

client = TestClient(app)


def make_streaming_mock(chunks: list[str]):
    """Returns an async generator that yields fake OpenAI stream chunks."""
    async def _gen():
        for chunk in chunks:
            yield chunk
    return _gen()


# ── /health ────────────────────────────────────────────────────────────────────

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ── POST /chat ─────────────────────────────────────────────────────────────────

def test_new_chat_streams_response():
    """Valid new-chat request should stream the assistant reply."""
    with patch("api_chat.main.send_input", new_callable=AsyncMock) as mock_send, \
         patch("api_chat.main.stream_response", return_value=make_streaming_mock(["Hello", " there"])):

        mock_send.return_value = MagicMock()  # fake OpenAI stream object

        response = client.post("/chat", json={
            "user_text": "Hello",
            "system_input": "Be concise",
            "temperature": 0.7,
        })

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/plain; charset=utf-8"


def test_new_chat_calls_format_and_send():
    """Route should call format_new_chat then send_input with the resulting payload."""
    with patch("api_chat.main.format_new_chat") as mock_format, \
         patch("api_chat.main.send_input", new_callable=AsyncMock) as mock_send, \
         patch("api_chat.main.stream_response", return_value=make_streaming_mock(["hi"])):

        fake_payload = {"messages": [{"role": "user", "content": "Hello"}], "temperature": 1.0}
        mock_format.return_value = fake_payload
        mock_send.return_value = MagicMock()

        client.post("/chat", json={"user_text": "Hello"})

        mock_format.assert_called_once()
        mock_send.assert_called_once_with(fake_payload)


def test_new_chat_returns_500_on_exception():
    """If send_input raises, the route should return HTTP 500."""
    with patch("api_chat.main.send_input", new_callable=AsyncMock, side_effect=Exception("API down")):
        response = client.post("/chat", json={"user_text": "Hello"})

    assert response.status_code == 500
    assert "API down" in response.json()["detail"]


# ── POST /chat/continue ────────────────────────────────────────────────────────

def test_continue_chat_streams_response():
    """Valid continue-chat request should stream the assistant reply."""
    with patch("api_chat.main.send_input", new_callable=AsyncMock) as mock_send, \
         patch("api_chat.main.stream_response", return_value=make_streaming_mock(["Continued"])):

        mock_send.return_value = MagicMock()

        response = client.post("/chat/continue", json={
            "conversation_history": {
                "messages": [
                    {"role": "user", "content": "Hi"},
                    {"role": "assistant", "content": "Hello!"},
                ],
                "temperature": 0.9,
            },
            "user_text": "Tell me more",
        })

        assert response.status_code == 200


def test_continue_chat_calls_format_and_send():
    """Route should call format_continued_chat then send_input."""
    with patch("api_chat.main.format_continued_chat") as mock_format, \
         patch("api_chat.main.send_input", new_callable=AsyncMock) as mock_send, \
         patch("api_chat.main.stream_response", return_value=make_streaming_mock(["ok"])):

        fake_payload = {"messages": [], "temperature": 0.9}
        mock_format.return_value = fake_payload
        mock_send.return_value = MagicMock()

        client.post("/chat/continue", json={
            "conversation_history": {
                "messages": [{"role": "user", "content": "Hi"}],
                "temperature": 0.9,
            },
            "user_text": "More",
        })

        mock_format.assert_called_once()
        mock_send.assert_called_once_with(fake_payload)


def test_continue_chat_returns_500_on_exception():
    """If send_input raises, the route should return HTTP 500."""
    with patch("api_chat.main.send_input", new_callable=AsyncMock, side_effect=RuntimeError("timeout")):
        response = client.post("/chat/continue", json={
            "conversation_history": {
                "messages": [{"role": "user", "content": "Hi"}],
                "temperature": 1.0,
            },
            "user_text": "More",
        })

    assert response.status_code == 500
