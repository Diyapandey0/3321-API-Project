# Converts the OpenAI streaming response into an async generator that
# FastAPI's StreamingResponse can consume directly.
# Print statements are gone — the caller (main.py) owns the HTTP response.
# -- Diya Pandey (original) | adapted for FastAPI

from typing import AsyncGenerator


async def stream_response(response) -> AsyncGenerator[str, None]:
    async for chunk in response:  # non-blocking
        try:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
        except (AttributeError, IndexError, TypeError) as e:
            yield f"\n[Stream error: {e}]"
            return