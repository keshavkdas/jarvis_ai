import os

def get_known_folder_path(name):
    home = os.path.expanduser("~")
    known_folders = {
        "downloads": os.path.join(home, "Downloads"),
        "documents": os.path.join(home, "Documents"),
        "desktop": os.path.join(home, "Desktop"),
        "pictures": os.path.join(home, "Pictures"),
    }

    for key in known_folders:
        if key in name:
            return known_folders[key]
    
    return None
