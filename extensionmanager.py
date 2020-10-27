#!/usr/bin/python3
import os, requests, json, lxml.html, subprocess, zipfile, shutil

class ExtensionManager():

    def __init__(self):
        self.extensions_path = os.getenv("HOME") + "/.local/share/gnome-shell/extensions/"
        self.results = []
        self.installed = self.listExtensions()
        self.version = subprocess.Popen("gnome-shell --version", shell=True, stdout=subprocess.PIPE).stdout.read().decode().split()[2]
    
    def listExtensions(self):
        return os.listdir(self.extensions_path)

    def search(self, query):
        response = requests.get("https://extensions.gnome.org/extension-query/?page=1&search=" + query)
        self.results = json.loads(response.text)["extensions"]

    def getExtension(self, uuid):
        # Parse the extension webpage and get the json from the data-svm element
        url = "https://extensions.gnome.org" + self.results[self.getindex(uuid)]["link"]
        response = requests.get(url)
        root = lxml.html.fromstring(response.text)
        content = root.xpath("/html/body/div[2]/div/div[2]/@data-svm")[0]
        releases = json.loads(content)

        # Get matching version
        extension_id = ""

        # Iterate through the different releases and get the matching one for your gnome version and failsafe to the lastest release
        for key, value in releases.items():
            if version.startswith(key):
                extension_id = str(value["pk"])
        if extension_id == "":
            extension_id = str(releases[max(releases)]["pk"])

        # Download and install
        print(uuid)
        self.download("https://extensions.gnome.org/download-extension/" + uuid + ".shell-extension.zip?version_tag=" + extension_id, uuid)
        self.install(uuid)

    def getindex(self, uuid):
        for index, entry in enumerate(self.results):
            if entry["uuid"] == uuid:
                return index

    def download(self, url, uuid):
        response = requests.get(url)
        with open(uuid + ".zip", "wb") as file:
            file.write(response.content)
        print("Downloaded " + uuid)
    
    def remove(self, uuid):
        install_path = self.extensions_path + uuid
        if os.path.isdir(install_path):
            print("Deleting " + uuid)
            shutil.rmtree(install_path)
        self.installed = self.listExtensions()
    
    def install(self, uuid):
        # Remove old extension       
        self.remove(uuid)

        # Create new folder with matching uuid and extract to it
        install_path = self.extensions_path + uuid
        os.mkdir(install_path)
        with zipfile.ZipFile(uuid + ".zip","r") as zip_ref:
            zip_ref.extractall(install_path)
        self.installed = self.listExtensions()
        print("Installed " + uuid)



