import pytest
from unittest.mock import AsyncMock, patch

from api_chat.api_handler import send_input


def make_fake_message():
    return {
        "messages": [{"role": "user", "content": "Hello"}],
        "temperature": 0.7,
    }


@pytest.mark.asyncio
async def test_send_input_calls_openai_with_correct_params():
    """send_input should call OpenAI with the correct model, messages, temperature, and stream."""
    fake_message = make_fake_message()

    with patch("api_chat.api_handler.AsyncOpenAI") as mock_openai_class:
        mock_client = AsyncMock()
        mock_openai_class.return_value = mock_client

        await send_input(fake_message)

        mock_client.chat.completions.create.assert_awaited_once_with(
            model="gpt-4o",
            messages=fake_message["messages"],
            temperature=fake_message["temperature"],
            stream=True,
        )


@pytest.mark.asyncio
async def test_send_input_returns_api_response():
    """send_input should return whatever the API call returns."""
    fake_message = make_fake_message()
    fake_response = object()

    with patch("api_chat.api_handler.AsyncOpenAI") as mock_openai_class:
        mock_client = AsyncMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create = AsyncMock(return_value=fake_response)

        result = await send_input(fake_message)

        assert result is fake_response


@pytest.mark.asyncio
async def test_send_input_creates_new_client_each_call():
    """send_input should instantiate a new OpenAI client on every call."""
    fake_message = make_fake_message()

    with patch("api_chat.api_handler.AsyncOpenAI") as mock_openai_class:
        mock_openai_class.return_value = AsyncMock()

        await send_input(fake_message)
        await send_input(fake_message)

        assert mock_openai_class.call_count == 2


@pytest.mark.asyncio
async def test_send_input_passes_full_message_history():
    """send_input should forward the entire messages list, not just the latest message."""
    fake_message = {
        "messages": [
            {"role": "system", "content": "Be concise"},
            {"role": "user", "content": "First question"},
            {"role": "assistant", "content": "First answer"},
            {"role": "user", "content": "Follow-up"},
        ],
        "temperature": 1.0,
    }

    with patch("api_chat.api_handler.AsyncOpenAI") as mock_openai_class:
        mock_client = AsyncMock()
        mock_openai_class.return_value = mock_client

        await send_input(fake_message)

        call_kwargs = mock_client.chat.completions.create.await_args.kwargs
        assert call_kwargs["messages"] == fake_message["messages"]
        assert len(call_kwargs["messages"]) == 4
