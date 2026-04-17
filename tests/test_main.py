from unittest.mock import patch, MagicMock
import pytest
from api_chat.main import main

def make_fake_inputjson():
    return {
        "messages": [
            {"role": "user", "content": "Hello"}
        ]
    }

def test_main_single_loop_then_exit():
    """User sends one message, then types 'n' to quit."""
    fake_inputjson = make_fake_inputjson()
    fake_response = MagicMock()         # pretend OpenAI response object
    fake_assistant_reply = "Hi there!"

    with patch("api_chat.main.FormatInput", return_value=fake_inputjson) as mock_format, \
         patch("api_chat.main.sendInput", return_value=fake_response) as mock_send, \
         patch("api_chat.main.receiveInput", return_value=fake_assistant_reply) as mock_receive, \
         patch("builtins.input", return_value="n"):  # user picks 'n' to exit

        main()

        # Each handler should have been called exactly once
        mock_format.assert_called_once()
        mock_send.assert_called_once_with(fake_inputjson)
        mock_receive.assert_called_once_with(fake_response)

def test_main_continues_on_y_then_exits():
    """User sends two messages — types 'y' to continue, then 'n' to quit."""
    fake_inputjson = make_fake_inputjson()

    with patch("api_chat.main.FormatInput", return_value=fake_inputjson), \
         patch("api_chat.main.sendInput", return_value=MagicMock()), \
         patch("api_chat.main.receiveInput", return_value="A reply"), \
         patch("builtins.input", side_effect=["y", "n"]):  # two turns

        main()  # should complete without error

def test_main_skips_when_receive_returns_none():
    """If receiveInput returns None, the loop should continue without appending to history."""
    fake_inputjson = make_fake_inputjson()

    with patch("api_chat.main.FormatInput", return_value=fake_inputjson), \
         patch("api_chat.main.sendInput", return_value=MagicMock()), \
         patch("api_chat.main.receiveInput", side_effect=[None, "A reply"]), \
         patch("builtins.input", side_effect=["y", "n"]):

        main()

        # After the None response the loop continued, so messages list
        # should only have one assistant entry appended (from the second turn)
        assert fake_inputjson["messages"].count(
            {"role": "assistant", "content": "A reply"}
        ) == 1


def test_main_appends_assistant_response_to_history():
    """After a valid reply, the assistant message should be added to conversation history."""
    fake_inputjson = make_fake_inputjson()

    with patch("api_chat.main.FormatInput", return_value=fake_inputjson), \
         patch("api_chat.main.sendInput", return_value=MagicMock()), \
         patch("api_chat.main.receiveInput", return_value="Hello back!"), \
         patch("builtins.input", return_value="n"):

        main()

        assert {"role": "assistant", "content": "Hello back!"} in fake_inputjson["messages"]