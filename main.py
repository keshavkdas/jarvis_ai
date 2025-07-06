from input.text_input import get_command
from output.speak import respond

def main():
    respond("Hello, I am your JARVIS. Awaiting your command...")
    while True:
        command = get_command().lower()
        if command in ["exit", "quit", "bye"]:
            respond("Goodbye!")
            break
        else:
            respond(f"You said: {command}")

if __name__ == "__main__":
    main()
