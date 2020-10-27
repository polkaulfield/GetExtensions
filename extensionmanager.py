import requests
import json
import lxml.html
import subprocess
import zipfile
import os
import shutil

# Get GNOME version
version = subprocess.Popen("gnome-shell --version", shell=True, stdout=subprocess.PIPE).stdout.read().decode().split()[2]

class ExtensionManager():
    def __init__(self):
        self.extensions_path = os.getenv("HOME") + "/.local/share/gnome-shell/extensions/"
        self.results = []
        self.installed = os.listdir(self.extensions_path)

    def search(self, query):
        response = requests.get("https://extensions.gnome.org/extension-query/?page=1&shell_version=" + version + "&search=" + query)
        self.results = json.loads(response.text)["extensions"]

    def getExtension(self, id):
        url = "https://extensions.gnome.org" + self.results[id]["link"]
        response = requests.get(url)
        root = lxml.html.fromstring(response.text)
        content = root.xpath("/html/body/div[2]/div/div[2]/@data-svm")[0]
        releases = json.loads(content)

        # Get matching version
        extension_id = ""
        for key, value in releases.items():
            if version.startswith(key):
                extension_id = str(value["pk"])
        
        # Get the uuid of the extension
        uuid = self.results[id]["uuid"]

        # Download and install
        self.download("https://extensions.gnome.org/download-extension/" + uuid + ".shell-extension.zip?version_tag=" + extension_id, uuid)
        self.install(uuid)

    def download(self, url, uuid):
        response = requests.get(url)
        with open(uuid + ".zip", "wb") as file:
            file.write(response.content)
        print("Downloaded!")
    
    def install(self, uuid):
        install_path = self.extensions_path + uuid
        
        # Remove old extension
        if os.path.isdir(install_path):
            print("Deleting old one")
            shutil.rmtree(install_path)

        # Create new folder with matching uuid and extract to it
        os.mkdir(install_path)
        with zipfile.ZipFile(uuid + ".zip","r") as zip_ref:
            zip_ref.extractall(install_path)
        print("Installed!")



