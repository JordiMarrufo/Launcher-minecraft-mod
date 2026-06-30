import requests

class Updater:

    def __init__(self):
        self.version_local = "1.0.0"
        self.url_version = "https://raw.githubusercontent.com/JordiMarrufo/Launcher-minecraft-mod/main/version.json"

    def check_update(self):

        try:
            r = requests.get(self.url_version, timeout=10)
            r.raise_for_status()

            data = r.json()
            version_online = data["version"]

            if version_online != self.version_local:
                return True, version_online

            return False, version_online

        except Exception as e:
            print("Error checking update:", e)
            return False, None