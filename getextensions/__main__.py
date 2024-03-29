#!/usr/bin/python3
import os, gi, threading, extensionmanager
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gio, Gdk
from gi.repository.GdkPixbuf import Pixbuf, InterpType

# Create main window (I'm too lazy to use glade)
class MainWindow(Gtk.ApplicationWindow):

    def __init__(self):

        # Set app name
        appname = "Get Extensions"
        Gtk.Window.__init__(self, title=appname)
        self.set_wmclass(appname,appname) # Deprecated but its the only workaround I found for GNOME on X11
        GLib.set_prgname(appname)
        self.connect("destroy", Gtk.main_quit)

        # Create Headerbar
        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.props.title = appname
        self.set_titlebar(hb)

        # Disable resizing
        self.set_resizable(False)

        # Create Entry field to grid
        self.entry = Gtk.Entry()
        self.entry.connect("key-press-event",self.on_key_press_event)

        # Create search button
        self.searchbutton = Gtk.Button(label="Search!")
        self.searchbutton.connect("clicked", self.on_searchbutton_clicked)

        # Create ListBox1 and install button
        self.listbox1 = Gtk.ListBox()
        self.listbox1.connect("row-selected", self.on_listbox1_row_selected)
        self.installbutton = Gtk.Button(label="Install")
        self.installbutton.connect("clicked", self.on_installbutton_clicked)
        self.installbutton.set_sensitive(False)

        self.scroll1 = Gtk.ScrolledWindow()
        self.scroll1.set_size_request(-1, 400)
        self.scroll1.add(self.listbox1)

        # Create and attach ListBox2 and delete button to page2
        self.listbox2 = Gtk.ListBox()
        self.listbox2.connect("row-selected", self.on_listbox2_row_selected)
        self.removebutton = Gtk.Button(label="Remove")
        self.removebutton.connect("clicked", self.on_removebutton_clicked)
        self.removebutton.set_sensitive(False)

        self.scroll2 = Gtk.ScrolledWindow()
        self.scroll2.set_size_request(-1, 445)
        self.scroll2.add(self.listbox2)

        # Create tabs
        notebook = Gtk.Notebook()
        notebook.set_halign(Gtk.Align.CENTER)
        self.add(notebook)

        # Define grid1 and set layout
        grid1 = Gtk.Grid()
        notebook.append_page(grid1, Gtk.Label(label="Download Extensions"))

        # Set grid1 padding
        grid1.set_column_homogeneous(True)
        grid1.set_margin_top(10)
        grid1.set_margin_bottom(10)
        grid1.set_margin_start(10)
        grid1.set_margin_end(10)
        grid1.set_column_spacing(10)
        grid1.set_row_spacing(10)

        # Populate grid1
        grid1.add(self.entry)
        grid1.attach(self.searchbutton, 1, 0, 1 ,1)
        grid1.attach(self.scroll1,  0, 1, 2 ,1)
        grid1.attach(self.installbutton,  0, 2, 2 ,1)

        # Define grid2 and set layout
        grid2 = Gtk.Grid()
        notebook.append_page(grid2, Gtk.Label(label="Installed Extensions"))

        # Set grid2 padding
        grid2.set_column_homogeneous(True)
        grid2.set_margin_top(10)
        grid2.set_margin_bottom(10)
        grid2.set_margin_start(10)
        grid2.set_margin_end(10)
        grid2.set_column_spacing(10)
        grid2.set_row_spacing(10)

        # Populate grid2
        grid2.add(self.scroll2)
        grid2.attach(self.removebutton, 0, 1, 1 ,1)

        # Create the ExtensionsManagerobject
        self.extmgr = extensionmanager.ExtensionManager()

        # Populate page2
        self.show_installed_extensions()

        # Set focus on entry
        self.entry.set_can_focus(True)
        self.entry.grab_focus()

        # Add no results to listbox
        name_label = Gtk.Label()
        name_label.set_halign(Gtk.Align.CENTER)
        name_label.set_text(str="Search to show results!")
        listboxrow = Gtk.ListBoxRow()
        listboxrow.add(name_label)
        self.listbox1.insert(listboxrow, 5)
        self.listbox1.set_sensitive(False)
        self.listbox1.show_all()

        # Create the default extension icon pixbuf
        self.default_icon_pixbuf = Pixbuf.new_from_file(os.path.join(os.path.dirname(__file__), "plugin.png"))
    
    def show_installed_extensions(self):
        # Clear old entries
        for entry in self.listbox2.get_children():
            self.listbox2.remove(entry)
        
        self.extmgr.populate_extensions()
        extensions_list = self.extmgr.installed_extensions

        for item in extensions_list:
            # Create a box for each item
            itembox = Gtk.Box()

            # Create label
            name_label = Gtk.Label()
            name_label.set_halign(Gtk.Align.START)

            # Check if the extension name is longer than 30 chars and trim it for label
            num = 30
            if len(item["name"]) >= num:
                name_label.set_text(str=item["name"][:num] + "...")
            else:
                name_label.set_text(str=item["name"])

            # Create switch
            switch = Gtk.Switch()
            fixed_switch = Gtk.Fixed()
            fixed_switch.put(switch, 0, 0)
            fixed_switch.set_valign(Gtk.Align.CENTER)
            switch.connect("notify::active", self.on_switch_activated, item["uuid"])

            if item["state"] == 1:
                switch.set_active(True)
            else:
                switch.set_active(False)

            # Pack everything to itembox
            itembox.pack_start(fixed_switch, False, True, 0)
            itembox.set_center_widget(name_label)

            # Check if item has prefs before adding the button

            if item["hasPrefs"] == True:
                config_button = Gtk.Button()
                config_button.set_halign(Gtk.Align.START)
                config_icon = Gtk.Image()
                config_icon.set_from_icon_name("emblem-system-symbolic", Gtk.IconSize.SMALL_TOOLBAR)
                config_button.add(config_icon)
                config_button.connect("clicked", self.on_config_button_clicked, item["uuid"])
                itembox.pack_end(config_button, False, False, 0)

            # Create the listbox row
            listboxrow = Gtk.ListBoxRow()
            listboxrow.add(itembox)
            # Add tooltip
            listboxrow.set_tooltip_text(item["description"])
            self.listbox2.add(listboxrow)

        # Display after refresh
        self.listbox2.show_all()
        self.show_all()

    def show_error(self, error_message):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.CANCEL,
            text="Error!",
        )
        dialog.format_secondary_text(str(error_message))
        dialog.run()
        dialog.destroy()
    
    def search_worker(self, query):
        try:
            self.extmgr.search_web(query)
        except Exception as error:
            GLib.idle_add(self.show_error, error)
            GLib.idle_add(self.restore_search_button)

        for item in self.extmgr.search_results:
            # Download the image into a buffer and render it with pixbuf
            try:
                img_buffer = self.extmgr.get_remote_image(item["uuid"])
            except Exception as error:
                img_buffer = None
                GLib.idle_add(self.show_error, error)
                GLib.idle_add(self.restore_search_button)

            # Check if the extension icon is local (faster searching)
            if img_buffer == None:
                pixbuf = self.default_icon_pixbuf
            else:
                img_buffer = Gio.MemoryInputStream.new_from_data(img_buffer, None)
                try:
                    pixbuf = Pixbuf.new_from_stream(img_buffer, None)
                    pixbuf = pixbuf.scale_simple(32, 32, InterpType.BILINEAR)
                except Exception as error:
                    pixbuf = self.default_icon_pixbuf
            item["pixbuf"] = pixbuf
        GLib.idle_add(self.display_search_results)

    def restore_search_button(self):
        self.searchbutton.set_sensitive(True)
        self.searchbutton.set_label("Search!")

    def display_search_results(self):
        self.search_thread.join()
        self.listbox1.set_sensitive(False)
        for item in self.extmgr.search_results:

            # Create a box for each item
            resultbox = Gtk.Box()
            name_label = Gtk.Label(label=item["name"])
            name_label.set_halign(Gtk.Align.START)

            # Create the label image
            img = Gtk.Image()
            img.set_from_pixbuf(item["pixbuf"])
            img.set_halign(Gtk.Align.START)

            resultbox.pack_start(img, True, True, 0)
            resultbox.pack_end(name_label, True, True, 0)

            listboxrow = Gtk.ListBoxRow()
            listboxrow.add(resultbox)
            
            listboxrow.set_tooltip_text(item["description"])

            self.listbox1.add(listboxrow)

        self.listbox1.show_all()
        self.show_all()

        # Reenable search button
        self.listbox1.set_sensitive(True)
        self.restore_search_button()

    def show_results(self):
        # Disable search button
        self.searchbutton.set_sensitive(False)
        self.searchbutton.set_label("Searching...")

        # Clear old entries
        for entry in self.listbox1.get_children():
            self.listbox1.remove(entry)

        # Disable install button until you have something selected
        self.installbutton.set_sensitive(False)

        # Start thread to add results
        query = self.entry.get_text()
        self.search_thread = threading.Thread(target=self.search_worker, args=(query,))
        self.search_thread.start()
    
    def on_switch_activated(self, switch, gparam, uuid):
        if switch.get_active():
            self.extmgr.enable_extension(uuid)
        else:
            self.extmgr.disable_extension(uuid)

    def on_key_press_event(self, widget, event):
        if event.keyval == Gdk.KEY_Return:
            self.show_results()

    def on_searchbutton_clicked(self, widget):
        self.show_results()
        
    def on_installbutton_clicked(self, widget):
        self.installbutton.set_sensitive(False)
        id = self.listbox1.get_selected_row().get_index()

        uuid = self.extmgr.search_results[id]["uuid"]
        try:
            self.extmgr.install_remote_extension(uuid)
        except Exception as error:
            self.show_error(error)
            return

        self.installbutton.set_sensitive(True)
        self.show_installed_extensions()
    
    def on_removebutton_clicked(self, widget):
        self.removebutton.set_sensitive(False)
        id = self.listbox2.get_selected_row().get_index()
        uuid = self.extmgr.installed_extensions[id]["uuid"]
        try:
            self.extmgr.uninstall_extension(uuid)
        except Exception as error:
            self.show_error(error)
            return

        self.removebutton.set_sensitive(True)
        self.show_installed_extensions()
    
    def on_listbox1_row_selected(self, widget, row):
        self.installbutton.set_sensitive(True)
    
    def on_listbox2_row_selected(self, widget, row):
        selected_row = self.listbox2.get_selected_row()
        if selected_row == None:
            return
        else:
            id = selected_row.get_index()
            item = self.extmgr.installed_extensions[id]

            if item["type"] == 2:
                self.removebutton.set_sensitive(True)
            else:
                self.removebutton.set_sensitive(False)
    
    def on_config_button_clicked(self, widget, uuid):
        self.extmgr.launch_extension_prefs(uuid)

if __name__ == "__main__":
    win = MainWindow()
    Gtk.main()
