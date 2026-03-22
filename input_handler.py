
#ask for an input then formats it into a json file to be sent to the api handler.
#-- Jeremiah Stohel
def FormatInput():
    user_text = input("Please enter your prompt: ")
    return {
        "role": "user",
        "content": user_text
    }
