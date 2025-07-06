from input.text_input import get_command
from output.speak import respond
from ai.nlp import ask_gpt

def main():
    respond("Hello, I am your JARVIS. How can I assist you?")
    while True:
        command = get_command().lower()
        if command in ["exit", "quit", "bye"]:
            respond("Goodbye!")
            break
        else:
            reply = ask_gpt(command)
            respond(reply)

if __name__ == "__main__":
    main()
