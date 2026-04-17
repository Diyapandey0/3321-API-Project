# This is a simple format for what i think the project would want to do if
#  you disagree feel free to change it just please leave comments on what you 
# changed , why, and your name so we can keep track of who did what and why.
#-- Jeremiah Stohel


from openai import OpenAI
from api_chat.input_handler import FormatInput
from api_chat.api_handler import sendInput
from api_chat.output_handler import receiveInput

def main():
    conversation_history = None
    while True:    
    # on run it will ask for input and create a json.
        inputjson = FormatInput(conversation_history) 
    # send message to openai using the json file made earlier.
        response = sendInput(inputjson)
    # accept the response and print it out to the user.
        assistant_response = receiveInput(response)

        if assistant_response is None:
            continue

        inputjson["messages"].append({"role": "assistant", "content": assistant_response})
        conversation_history = inputjson

        continue_chat = input("Continue? (y/n): ").lower()
        if continue_chat != 'y':
            print("Exiting chat. Goodbye!")
            break

if __name__ == "__main__":
    main()

