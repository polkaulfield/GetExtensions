#!/usr/bin/python3

import extensionmanager

em = extensionmanager.ExtensionManager()
print(em.list_user_extensions())
print(em.extension_is_local("dash-to-dock@micxgx.gmail.com"))