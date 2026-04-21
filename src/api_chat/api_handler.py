# Receives the formatted message payload and sends it to the OpenAI API.
# Logic is unchanged from the CLI version — only type hints added.
# -- Zerric Stewart (original) | adapted for FastAPI

from openai import AsyncOpenAI

async def send_input(message: dict):
    client = AsyncOpenAI()
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=message["messages"],
        temperature=message["temperature"],
        stream=True,
    )
    return response