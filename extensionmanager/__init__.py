#!/usr/bin/python3
import os, requests, json, lxml.html, subprocess, zipfile, shutil, re

class ExtensionManager():

    def __init__(self):
        self.extensions_local_path = os.getenv("HOME") + "/.local/share/gnome-shell/extensions/"
        self.extensions_sys_path = "/usr/share/gnome-shell/extensions/"
        self.results = []
        self.installed = self.list_all_extensions()
        self.version = self.run_command("gnome-shell --version").split()[2]
    
    def run_command(self, command):
        return subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).stdout.read().decode()    

    def list_all_extensions(self):
        installed_extensions = []
        uuids = self.list_user_extensions() + self.list_system_extensions()
        enabled_extensions = re.findall(r'\'(.+?)\'', self.run_command("gsettings get org.gnome.shell enabled-extensions"))
        for uuid in uuids:
            extension_local_path = self.extensions_local_path + uuid
            extension_sys_path = self.extensions_sys_path + uuid

            extension_data = {"uuid": uuid, "local": self.extension_is_local(uuid)}
            if uuid in enabled_extensions:
                extension_data["enabled"] = True
            else:
                extension_data["enabled"] = False
            if extension_data["local"] == True:
                metadata = open(extension_local_path + "/metadata.json", "r").read()
            else:
                metadata = open(extension_sys_path + "/metadata.json").read()
            metadata = json.loads(metadata)

            # Check for preferences
            if os.path.exists(extension_sys_path + "/prefs.js") or os.path.exists(extension_local_path + "/prefs.js"):
                extension_data["prefs"] = True
            else:
                extension_data["prefs"] = False

            extension_data["name"] = metadata["name"]
            installed_extensions.append(extension_data)
        return installed_extensions
    
    def extension_is_local(self, uuid):
        if uuid in self.list_user_extensions():
            return True
        else:
            return False

    def list_system_extensions(self):
        return os.listdir(self.extensions_sys_path)

    def list_user_extensions(self):
        try:
            return os.listdir(self.extensions_local_path)
        except FileNotFoundError:
            os.mkdir(self.extensions_local_path)
            return os.listdir(self.extensions_local_path)

    def search(self, query):
        try:
            response = self.get_request("https://extensions.gnome.org/extension-query/?page=1&search=" + query)
        except:
            raise
            return        
        self.results = json.loads(response.text)["extensions"]

    def get_extensions(self, uuid):
        # Parse the extension webpage and get the json from the data-svm element
        url = "https://extensions.gnome.org" + self.results[self.get_index(uuid)]["link"]
        try:
            response = self.get_request(url)
        except:
            raise

        root = lxml.html.fromstring(response.text)
        content = root.xpath("/html/body/div[2]/div/div[2]/@data-svm")[0]
        releases = json.loads(content)

        # Get matching version
        extension_id = ""

        # Iterate through the different releases and get the matching one for your gnome version and failsafe to the lastest release
        subversions = []
        for key, value in releases.items():
            subversions.append(float(key[2:]))

            if self.version.startswith(str(key)):
                extension_id = str(value["pk"])
        
        # If the ID doesn't start with your current version, get the highest one
        if extension_id == "":

            # Use re to remove .0 from the float conversion above
            max_subversion = re.sub('\.0$', '', str(max(subversions)))
            highest_version = "3." + max_subversion
            extension_id = str(releases[highest_version]["pk"])

        # Download and install
        try:
            self.download("https://extensions.gnome.org/download-extension/" + uuid + ".shell-extension.zip?version_tag=" + extension_id, uuid)
            self.install(uuid)
        except:
            raise

    def get_index(self, uuid):
        for index, entry in enumerate(self.results):
            if entry["uuid"] == uuid:
                return index
    
    def get_uuid(self, index):
        return self.results[index]["uuid"]

    def download(self, url, uuid):
        try:
            response = self.get_request(url)
            with open(self.get_zip_path(uuid), "wb") as file:
                file.write(response.content)
                print("Downloaded " + uuid)
        except:
            raise

    def remove(self, uuid):
        install_path = self.extensions_local_path + uuid
        if os.path.isdir(install_path):
            print("Deleting " + uuid)
            try:
                shutil.rmtree(install_path)
            except:
                raise
        self.installed = self.list_all_extensions()
    
    def get_image(self, uuid):
        url = "https://extensions.gnome.org" + self.results[self.get_index(uuid)]["icon"]
        if url == "https://extensions.gnome.org/static/images/plugin.png":
            return None
        try:
            response = self.get_request(url)
            return response.content
        except:
            raise
    
    def get_request(self, url):
        response = requests.get(url)
        if response == None:
            raise
            return
        return response
    
    def set_extension_status(self, uuid, status):
        self.run_command("gnome-extensions " + status + " " + uuid)
    
    def get_zip_path(self, uuid):
        return "/tmp/" + uuid + ".zip"

    def install(self, uuid):
        # Remove old extension       
        self.remove(uuid)
        zip_path = self.get_zip_path(uuid)

        # Create new folder with matching uuid and extract to it
        install_path = self.extensions_local_path + uuid

        try:
            os.mkdir(install_path)
            with zipfile.ZipFile(zip_path,"r") as zip_ref:
                zip_ref.extractall(install_path)
            os.remove(zip_path)
            self.installed = self.list_all_extensions()
            print("Installed " + uuid)
            
        except:
            raise



