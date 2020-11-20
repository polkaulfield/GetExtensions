#!/usr/bin/python3
from gi.repository import Gio, GLib
import requests, json

class ExtensionManager():

    def __init__(self):
        bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
        self.__proxy = Gio.DBusProxy.new_sync(bus, Gio.DBusProxyFlags.NONE, None, "org.gnome.Shell.Extensions","/org/gnome/Shell/Extensions","org.gnome.Shell.Extensions", None)

        # Properties
        self.search_results = {}
        self.installed_extensions = {}
    
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
        return self.__getproperty("ShellVersion")
    
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
            
    # Web related stuff
    def search_web(self, query):
        response = requests.get("https://extensions.gnome.org/extension-query/?page=1&search=" + query)
        response = json.loads(response.text)

        # Reorganize array into a dict with uuids as keys
        for item in response["extensions"]:

            # Delete the redundant uuid key and populate new dict
            uuid = item["uuid"]
            item.pop("uuid")
            self.search_results[uuid] = item

    def get_remote_image(self, uuid):
        url = "https://extensions.gnome.org" + self.search_results[uuid]["icon"]
        if url == "https://extensions.gnome.org/static/images/plugin.png":
            return None
        response = requests.get(url, stream=True)
        return response.content





