# This is a simple format for what i think the project would want to do if
#  you disagree feel free to change it just please leave comments on what you 
# changed , why, and your name so we can keep track of who did what and why.
#-- Jeremiah Stohel


from openai import OpenAI
from input_handler import FormatInput
from api_handler import sendInput
from output_handler import receiveInput

def main():
# on run it will ask for input and create a json.
    inputjson = FormatInput() 
# send message to openai using the json file made earlier.
    response = sendInput(inputjson)
# accept the response and print it out to the user.
    receiveInput(response)

if __name__ == "__main__":
    main()

