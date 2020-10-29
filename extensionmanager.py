#!/usr/bin/python3
import os, requests, json, lxml.html, subprocess, zipfile, shutil

class ExtensionManager():

    def __init__(self):
        self.extensions_path = os.getenv("HOME") + "/.local/share/gnome-shell/extensions/"
        self.results = []
        self.installed = self.list_extensions()
        self.version = subprocess.Popen("gnome-shell --version", shell=True, stdout=subprocess.PIPE).stdout.read().decode().split()[2]
    
    def list_extensions(self):
        try:
            return os.listdir(self.extensions_path)
        except FileNotFoundError:
            os.mkdir(self.extensions_path)
            return os.listdir(self.extensions_path)

    def search(self, query):
        response = self.get_request("https://extensions.gnome.org/extension-query/?page=1&search=" + query)
        self.results = json.loads(response.text)["extensions"]

    def get_extensions(self, uuid):
        # Parse the extension webpage and get the json from the data-svm element
        url = "https://extensions.gnome.org" + self.results[self.get_index(uuid)]["link"]
        response = self.get_request(url)
        root = lxml.html.fromstring(response.text)
        content = root.xpath("/html/body/div[2]/div/div[2]/@data-svm")[0]
        releases = json.loads(content)

        # Get matching version
        extension_id = ""

        # Iterate through the different releases and get the matching one for your gnome version and failsafe to the lastest release
        subversions = []
        for key, value in releases.items():
            subversions.append(int(key[2:]))
            if self.version.startswith(key):
                extension_id = str(value["pk"])
        
        # If the ID doesn't start with your current version, get the highest one
        if extension_id == "":
            print(subversions)
            print(str(max(subversions)))
            highest_version = "3." + str(max(subversions))
            extension_id = str(releases[highest_version]["pk"])

        # Download and install
        self.download("https://extensions.gnome.org/download-extension/" + uuid + ".shell-extension.zip?version_tag=" + extension_id, uuid)
        self.install(uuid)

    def get_index(self, uuid):
        for index, entry in enumerate(self.results):
            if entry["uuid"] == uuid:
                return index
    
    def get_uuid(self, index):
        return self.results[index]["uuid"]

    def download(self, url, uuid):
        response = get_request(url)
        with open(uuid + ".zip", "wb") as file:
            file.write(response.content)
        print("Downloaded " + uuid)
    
    def remove(self, uuid):
        install_path = self.extensions_path + uuid
        if os.path.isdir(install_path):
            print("Deleting " + uuid)
            shutil.rmtree(install_path)
        self.installed = self.list_extensions()
    
    def get_image(self, uuid):
        response = self.get_request("https://extensions.gnome.org" + self.results[self.get_index(uuid)]["icon"])
        return response.content
    
    def get_request(self, url):
        try:
            return requests.get(url)
        except requests.ConnectionError:
            print("[!] Cannot request " + url)
            return None
    
    def install(self, uuid):
        # Remove old extension       
        self.remove(uuid)

        # Create new folder with matching uuid and extract to it
        install_path = self.extensions_path + uuid
        os.mkdir(install_path)
        with zipfile.ZipFile(uuid + ".zip","r") as zip_ref:
            zip_ref.extractall(install_path)
        self.installed = self.list_extensions()
        print("Installed " + uuid)



