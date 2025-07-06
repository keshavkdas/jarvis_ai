from input.text_input import get_command
from output.speak import respond
from ai.nlp import ask_gpt
from system.commands import execute_command

def main():
    respond("Hello, I am your JARVIS. How can I assist you?")
    while True:
        command = get_command().lower()

        if command in ["exit", "quit", "bye"]:
            respond("Goodbye!")
            break

        elif command.startswith("run "):
            shell_cmd = command[4:]  # Strip "run "
            output = execute_command(shell_cmd)
            respond(output)

        else:
            reply = ask_gpt(command)
            respond(reply)

if __name__ == "__main__":
    main()
