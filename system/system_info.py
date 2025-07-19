import platform
import psutil # type: ignore
import shutil
import socket

def get_system_info():
    try:
        info = {
            "OS": platform.system() + " " + platform.release(),
            "CPU": platform.processor(),
            "RAM": f"{round(psutil.virtual_memory().total / (1024**3), 2)} GB",
            "Storage": f"{round(shutil.disk_usage('/').total / (1024**3), 2)} GB",
            "Hostname": socket.gethostname(),
            "IP Address": socket.gethostbyname(socket.gethostname())
        }
        return "\n".join([f"{k}: {v}" for k, v in info.items()])
    except Exception as e:
        return f"Error fetching system info: {e}"
