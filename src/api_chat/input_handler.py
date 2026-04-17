
#ask for an input then formats it into a json file to be sent to the api handler.
#-- Jeremiah Stohel
def FormatInput(conversation_history=None):
    if conversation_history is None:
        conversation_history = []
        user_text = input("Please enter your prompt: ")
        system_input = input("Please enter any system instructions (or press Enter for default): ")
        temperature = input("Please enter the desired temperature (0 - 2): ")
        try:
            temperature = float(temperature) if temperature else 1.0
        except ValueError:
            temperature = 1.0

        messages = []
        if system_input:
            messages.append({"role": "system", "content": system_input})
        messages.append({"role": "user", "content": user_text})

    else:
        messages = conversation_history["messages"].copy()
        temperature = conversation_history["temperature"]
        user_text = input("Please enter your prompt: ")
        messages.append({"role": "user", "content": user_text})

    return {
        "messages": messages,
        "temperature": temperature
    }