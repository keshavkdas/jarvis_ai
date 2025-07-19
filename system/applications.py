import winreg

def list_installed_apps():
    apps = []
    paths = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
    ]
    for root in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
        for path in paths:
            try:
                reg_key = winreg.OpenKey(root, path)
                for i in range(0, winreg.QueryInfoKey(reg_key)[0]):
                    sub_key = winreg.EnumKey(reg_key, i)
                    app_key = winreg.OpenKey(reg_key, sub_key)
                    try:
                        app_name = winreg.QueryValueEx(app_key, "DisplayName")[0]
                        apps.append(app_name)
                    except FileNotFoundError:
                        pass
            except Exception:
                continue
    return sorted(set(apps))
