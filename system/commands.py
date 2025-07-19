import subprocess

def execute_command(command: str) -> str:
    try:
        # Run the command, capture stdout and stderr
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return result.stdout.strip() or "(No output)"
        else:
            return f"Error: {result.stderr.strip()}"
    except Exception as e:
        return f"Failed to execute command: {str(e)}"
    
def open_application(app_name: str) -> str:
    try:
        subprocess.Popen(app_name, shell=True)
        return f"Opening {app_name}"
    except Exception as e:
        return f"Failed to open {app_name}: {e}"    
