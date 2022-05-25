#!/usr/bin/python3
from gi.repository import Gio, GLib
import requests, json

class ExtensionManager():

    def __init__(self):
        bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
        self.__proxy = Gio.DBusProxy.new_sync(bus, Gio.DBusProxyFlags.NONE, None, "org.gnome.Shell.Extensions","/org/gnome/Shell/Extensions","org.gnome.Shell.Extensions", None)

        # Properties
        self.search_results = []
        self.installed_extensions = []
    
    # Internal Methods for DBus
    def __getproperty(self, prop):
        return self.__proxy.get_cached_property(prop)

    def __callmethod(self, method, args):
        if args != None:
            args = GLib.Variant("(s)", (args,))
        value = self.__proxy.call_sync(method, args, 0, -1, None).unpack()
        if value:
            return value[0]
        return

    # Public Methods
    def shell_version(self):
        return self.__getproperty("ShellVersion").get_string()
    
    def list_extensions(self):
        return self.__callmethod("ListExtensions", None)
    
    def get_extension_info(self, uuid):
        return self.__callmethod("GetExtensionInfo", uuid)
    
    def enable_extension(self, uuid):
        return self.__callmethod("EnableExtension", uuid)
    
    def disable_extension(self, uuid):
        return self.__callmethod("DisableExtension", uuid)
    
    def launch_extension_prefs(self, uuid):
        return self.__callmethod("LaunchExtensionPrefs", uuid)
    
    def install_remote_extension(self, uuid):
        return self.__callmethod("InstallRemoteExtension", uuid)

    def uninstall_extension(self, uuid):
        return self.__callmethod("UninstallExtension", uuid)

    def check_for_updates(self):
        return self.__callmethod("CheckForUpdates", None)
    
    def is_extension_enabled(self, uuid):
        state = self.get_extension_info(uuid)["state"]
        if state == 1:
            return True
        elif state == 2:
            return False
    
    def is_extension_local(self, uuid):
        state = self.get_extension_info(uuid)["type"]
        if state == 1:
            return False
        elif state == 2:
            return True

    def version_to_float(self, version):
        version = version.replace(".beta", "")
        arr = version.split(".")
        if len(arr) > 2:
            arr = arr[:-1]
            version = ".".join(arr)
        return float(version)

    # Web related stuff
    def search_web(self, query):
        self.search_results = []
        response = requests.get("https://extensions.gnome.org/extension-query/?page=1&search=" + query)
        response = json.loads(response.text)["extensions"]


        compatible_extensions = []
        shell_version = self.version_to_float(self.shell_version())
        for extension in response:
            for key in extension["shell_version_map"].keys():
                extension_version = self.version_to_float(key)
                if extension_version >= shell_version:
                    compatible_extensions.append(extension)
                    break

        # Populate array with null objects to match the size of the ordered one
        self.search_results = [None] * len(compatible_extensions)
        sorted_names = []

        # Sort all the names in the response object
        for item in compatible_extensions:
            sorted_names.append(item["name"])
        
        sorted_names = sorted(sorted_names, key=str.casefold)

        # Place all the items inside a ordered array
        for item in compatible_extensions:
            for i in range(0, len(sorted_names)):
                if item["name"] == sorted_names[i]:
                    self.search_results[i] = item
        
    def populate_extensions(self):
        extensions = self.list_extensions()
        self.installed_extensions = []
        self.installed_extensions = [None] * len(extensions)
        sorted_names = []

        for key, item in extensions.items():
            sorted_names.append(item["name"])
        
        sorted_names = sorted(sorted_names, key=str.casefold)

        for key, item in extensions.items():
            for i in range(0, len(sorted_names)):
                if item["name"] == sorted_names[i]:
                    self.installed_extensions[i] = item


    def get_remote_image(self, uuid):
        for item in self.search_results:
            if item["uuid"] == uuid:
                url = "https://extensions.gnome.org" + item["icon"]
                if url == "https://extensions.gnome.org/static/images/plugin.png":
                    return None
                response = requests.get(url, stream=True)
                return response.content
