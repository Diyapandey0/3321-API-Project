# Accepts the API response and prints the LLM's reply to the user.
# -- Diya Pandey

def receiveInput(response):
    try:
        reply = response.choices[0].message.content
        print("Response:", reply)
    except (AttributeError, IndexError, TypeError) as e:
        print(f"Error: Could not read the response. Details: {e}")
