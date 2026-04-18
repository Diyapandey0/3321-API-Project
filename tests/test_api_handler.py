from unittest.mock import patch, MagicMock
from api_chat.api_handler import sendInput


def make_fake_message():
    return {
        "messages": [{"role": "user", "content": "Hello"}],
        "temperature": 0.7
    }


def test_send_input_calls_openai_with_correct_params():
    """sendInput should call OpenAI with the correct model, messages, temperature, and stream."""
    fake_message = make_fake_message()

    with patch("api_chat.api_handler.OpenAI") as mock_openai_class:
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        sendInput(fake_message)

        mock_client.chat.completions.create.assert_called_once_with(
            model="gpt-4o",
            messages=fake_message["messages"],
            temperature=fake_message["temperature"],
            stream=True
        )


def test_send_input_returns_api_response():
    """sendInput should return whatever the API call returns."""
    fake_message = make_fake_message()
    fake_response = MagicMock()

    with patch("api_chat.api_handler.OpenAI") as mock_openai_class:
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.return_value = fake_response

        result = sendInput(fake_message)

        assert result is fake_response


def test_send_input_creates_new_client_each_call():
    """sendInput should instantiate a new OpenAI client on every call."""
    fake_message = make_fake_message()

    with patch("api_chat.api_handler.OpenAI") as mock_openai_class:
        mock_openai_class.return_value = MagicMock()

        sendInput(fake_message)
        sendInput(fake_message)

        assert mock_openai_class.call_count == 2


def test_send_input_passes_full_message_history():
    """sendInput should forward the entire messages list, not just the latest message."""
    fake_message = {
        "messages": [
            {"role": "system", "content": "Be concise"},
            {"role": "user", "content": "First question"},
            {"role": "assistant", "content": "First answer"},
            {"role": "user", "content": "Follow-up"}
        ],
        "temperature": 1.0
    }

    with patch("api_chat.api_handler.OpenAI") as mock_openai_class:
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        sendInput(fake_message)

        call_kwargs = mock_client.chat.completions.create.call_args.kwargs
        assert call_kwargs["messages"] == fake_message["messages"]
        assert len(call_kwargs["messages"]) == 4
