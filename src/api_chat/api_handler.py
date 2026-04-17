# Receives the formatted message from input_handler and sends it to the OpenAI API.
# Returns the API response to be handled by output_handler.
# -- Zerric Stewart

from openai import OpenAI

def sendInput(message):
    client = OpenAI()  # uses OPENAI_API_KEY environment variable by default
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=message["messages"],
        temperature=message["temperature"],  # message is already {"role": "user", "content": "..."}
        stream=True
    )
    return response
