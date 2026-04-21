from unittest.mock import MagicMock
from api_chat.output_handler import receiveInput


def make_fake_chunk(content):
    chunk = MagicMock()
    chunk.choices[0].delta.content = content
    return chunk


def test_receive_input_prints_streamed_content(capsys):
    """receiveInput should print each non-None delta in order."""
    chunks = [make_fake_chunk("Hello"), make_fake_chunk(" world")]

    receiveInput(iter(chunks))

    captured = capsys.readouterr()
    assert "Hello world" in captured.out


def test_receive_input_skips_none_deltas(capsys):
    """receiveInput should skip chunks where delta content is None."""
    chunks = [make_fake_chunk("Hello"), make_fake_chunk(None), make_fake_chunk("!")]

    receiveInput(iter(chunks))

    captured = capsys.readouterr()
    assert "Hello!" in captured.out
    assert "None" not in captured.out


def test_receive_input_returns_none():
    """receiveInput has no return statement, so it always returns None."""
    result = receiveInput(iter([]))

    assert result is None


def test_receive_input_handles_attribute_error(capsys):
    """receiveInput should catch AttributeError and print an error message."""
    chunk = MagicMock(spec=[])  # spec=[] means no attributes — accessing .choices raises AttributeError

    receiveInput(iter([chunk]))

    captured = capsys.readouterr()
    assert "Error" in captured.out


def test_receive_input_handles_index_error(capsys):
    """receiveInput should catch IndexError when choices list is empty."""
    chunk = MagicMock()
    chunk.choices = []  # choices[0] will raise IndexError

    receiveInput(iter([chunk]))

    captured = capsys.readouterr()
    assert "Error" in captured.out


def test_receive_input_handles_type_error(capsys):
    """receiveInput should catch TypeError when response is not iterable."""
    receiveInput(None)  # iterating None raises TypeError

    captured = capsys.readouterr()
    assert "Error" in captured.out
