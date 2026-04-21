# FastAPI entry point — replaces the CLI while-loop in the original main.py.
# Two routes mirror the two branches of the original FormatInput():
#   POST /chat        → new conversation
#   POST /chat/continue → continue an existing conversation
# -- Jeremiah Stohel (original) | adapted for FastAPI

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

try:
    from .models import NewChatRequest, ContinueChatRequest
    from .input_handler import format_new_chat, format_continued_chat
    from .api_handler import send_input
    from .output_handler import stream_response
except ImportError:
    from api_chat.models import NewChatRequest, ContinueChatRequest
    from api_chat.input_handler import format_new_chat, format_continued_chat
    from api_chat.api_handler import send_input
    from api_chat.output_handler import stream_response

app = FastAPI(
    title="API Chat",
    description="Streaming OpenAI chat via FastAPI",
    version="0.1.0",
)


@app.post("/chat", summary="Start a new conversation")
async def new_chat(request: NewChatRequest) -> StreamingResponse:
    """
    Accepts a user prompt (plus optional system instructions and temperature)
    and streams the assistant's reply token-by-token.

    After the stream completes, reconstruct ConversationHistory on the client
    by appending {"role": "user", "content": request.user_text} and the
    accumulated assistant text, then pass it to POST /chat/continue.
    """
    try:
        payload = format_new_chat(request)
        openai_stream = await send_input(payload)
        return StreamingResponse(stream_response(openai_stream), media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/continue", summary="Continue an existing conversation")
async def continue_chat(request: ContinueChatRequest) -> StreamingResponse:
    """
    Accepts the full conversation history plus a new user message and
    streams the next assistant reply.

    The client is responsible for maintaining history between turns:
    append {"role": "assistant", "content": <accumulated stream>} to
    conversation_history.messages before the next request.
    """
    try:
        payload = format_continued_chat(request)
        openai_stream = await send_input(payload)
        return StreamingResponse(stream_response(openai_stream), media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health", summary="Health check")
async def health() -> dict:
    return {"status": "ok"}


def start():
    """Entry point wired to the `serve` script in pyproject.toml."""
    uvicorn.run("api_chat.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    start()
