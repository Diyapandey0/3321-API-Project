# Accepts the API response and prints the LLM's reply to the user.
# -- Diya Pandey

def receiveInput(response):
    try:
        print("Response: ", end="", flush=True)
        for chunk in response:
            delta = chunk.choices[0].delta.content
            if delta:
                print(delta, end="", flush=True)
        print()
    except (AttributeError, IndexError, TypeError) as e:
        print(f"Error: Could not read the response. Details: {e}")
