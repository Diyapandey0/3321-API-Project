import pytest
from unittest.mock import MagicMock

from api_chat.output_handler import stream_response


def make_fake_chunk(content):
    chunk = MagicMock()
    chunk.choices[0].delta.content = content
    return chunk


async def collect_output(response):
    collected = []
    async for part in stream_response(response):
        collected.append(part)
    return collected


@pytest.mark.asyncio
async def test_stream_response_yields_streamed_content():
    """stream_response should yield each non-None delta in order."""

    async def fake_response():
        for chunk in [make_fake_chunk("Hello"), make_fake_chunk(" world")]:
            yield chunk

    assert await collect_output(fake_response()) == ["Hello", " world"]


@pytest.mark.asyncio
async def test_stream_response_skips_none_deltas():
    """stream_response should skip chunks where delta content is None."""

    async def fake_response():
        for chunk in [make_fake_chunk("Hello"), make_fake_chunk(None), make_fake_chunk("!")]:
            yield chunk

    assert await collect_output(fake_response()) == ["Hello", "!"]


@pytest.mark.asyncio
async def test_stream_response_returns_no_chunks_for_empty_stream():
    """stream_response should yield nothing for an empty stream."""

    async def fake_response():
        if False:
            yield None

    assert await collect_output(fake_response()) == []


@pytest.mark.asyncio
async def test_stream_response_handles_attribute_error():
    """stream_response should yield an error marker on AttributeError."""
    chunk = MagicMock(spec=[])

    async def fake_response():
        yield chunk

    result = await collect_output(fake_response())
    assert len(result) == 1
    assert result[0].startswith("\n[Stream error:")


@pytest.mark.asyncio
async def test_stream_response_handles_index_error():
    """stream_response should yield an error marker when choices list is empty."""
    chunk = MagicMock()
    chunk.choices = []

    async def fake_response():
        yield chunk

    result = await collect_output(fake_response())
    assert len(result) == 1
    assert result[0].startswith("\n[Stream error:")


@pytest.mark.asyncio
async def test_stream_response_propagates_non_async_iterable_error():
    """stream_response should fail when given a non-async iterable response."""
    with pytest.raises(TypeError):
        await collect_output(None)
