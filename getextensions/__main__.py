#!/usr/bin/python3
import os, gi, threading, extensionmanager
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gio, Gdk
from gi.repository.GdkPixbuf import Pixbuf, InterpType

class ListBoxRowWithData(Gtk.ListBoxRow):
    def __init__(self, data):
        super(Gtk.ListBoxRow, self).__init__()
        self.data = data
        self.add(Gtk.Label(label=data))

# Create main window (I'm too lazy to use glade)
class MainWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Get Extensions")
        GLib.set_prgname("Get Extensions")
        self.connect("destroy", Gtk.main_quit)

        # Create Headerbar
        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.props.title = "Get Extensions"
        self.set_titlebar(hb)

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

        # Create and attach ListBox2 and delete button to page2
        self.listbox2 = Gtk.ListBox()
        self.listbox2.connect("row-selected", self.on_listbox2_row_selected)
        self.removebutton = Gtk.Button(label="Remove")
        self.removebutton.connect("clicked", self.on_removebutton_clicked)
        self.removebutton.set_sensitive(False)

        # Create tabs
        self.notebook = Gtk.Notebook()
        self.notebook.set_halign(Gtk.Align.CENTER)
        self.add(self.notebook)

        # Define grid1 and set layout
        self.grid1 = Gtk.Grid()
        self.notebook.append_page(self.grid1, Gtk.Label(label="Download Extensions"))

        # Set grid1 padding
        self.grid1.set_column_homogeneous(True)
        self.grid1.set_margin_top(10)
        self.grid1.set_margin_bottom(10)
        self.grid1.set_margin_start(10)
        self.grid1.set_margin_end(10)
        self.grid1.set_column_spacing(10)
        self.grid1.set_row_spacing(10)

        # Populate grid1
        self.grid1.add(self.entry)
        self.grid1.attach(self.searchbutton, 1, 0, 1 ,1)
        self.grid1.attach(self.listbox1,  0, 1, 2 ,1)
        self.grid1.attach(self.installbutton,  0, 2, 2 ,1)

        # Define grid2 and set layout
        self.grid2 = Gtk.Grid()
        self.notebook.append_page(self.grid2, Gtk.Label(label="Installed Extensions"))

        # Set grid2 padding
        self.grid2.set_column_homogeneous(True)
        self.grid2.set_margin_top(10)
        self.grid2.set_margin_bottom(10)
        self.grid2.set_margin_start(10)
        self.grid2.set_margin_end(10)
        self.grid2.set_column_spacing(10)
        self.grid2.set_row_spacing(10)

        # Populate grid2
        self.grid2.add(self.listbox2)
        self.grid2.attach(self.removebutton, 0, 1, 1 ,1)

        # Create the ExtensionsManagerobject
        self.extmgr = extensionmanager.ExtensionManager()

        # Populate page2
        self.show_installed_extensions()

        # Set focus on entry
        self.entry.set_can_focus(True)
        self.entry.grab_focus()

        # Add no results to listbox
        self.listbox1.add(ListBoxRowWithData("Search to show results!"))
        self.listbox1.set_sensitive(False)
    
    def show_installed_extensions(self):
        # Clear old entries
        for entry in self.listbox2.get_children():
            self.listbox2.remove(entry)
        
        extensions_list = self.extmgr.list_extensions()

        for uuid, value in extensions_list.items():
            # Create a box for each item
            itembox = Gtk.Box()

            # Create label
            name_label = Gtk.Label()
            name_label.set_halign(Gtk.Align.START)

            # Check if the extension name is longer than 30 chars and trim it for label
            num = 30
            if len(value["name"]) >= num:
                name_label.set_text(str=value["name"][:num] + "...")
            else:
                name_label.set_text(str=value["name"])

            # Create switch
            switch = Gtk.Switch()
            fixed_switch = Gtk.Fixed()
            fixed_switch.put(switch, 0, 0)
            fixed_switch.set_valign(Gtk.Align.CENTER)
            switch.connect("notify::active", self.on_switch_activated, uuid)

            if value["state"] == 1:
                switch.set_active(True)
            else:
                switch.set_active(False)

            # Pack everything to itembox
            itembox.pack_start(fixed_switch, False, True, 0)
            itembox.set_center_widget(name_label)

            # Check if item has prefs before adding the button

            if value["hasPrefs"] == True:
                config_button = Gtk.Button()
                config_button.set_halign(Gtk.Align.START)
                config_icon = Gtk.Image()
                config_icon.set_from_icon_name(Gtk.STOCK_PREFERENCES, Gtk.IconSize.SMALL_TOOLBAR)
                config_button.add(config_icon)
                config_button.connect("clicked", self.on_config_button_clicked, uuid)
                itembox.pack_end(config_button, False, False, 0)

            # Create the listbox row
            listboxrow = Gtk.ListBoxRow()
            listboxrow.add(itembox)
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

        for uuid, result in self.extmgr.search_results.items():
            # Download the image into a buffer and render it with pixbuf
            try:
                img_buffer = self.extmgr.get_remote_image(uuid)
            except Exception as error:
                GLib.idle_add(self.show_error, error)
                GLib.idle_add(self.restore_search_button)

            # Check if the extension icon is local (faster searching)
            if img_buffer == None:
                pixbuf = Pixbuf.new_from_file(os.path.join(os.path.dirname(__file__), "plugin.png"))
            else:
                img_buffer = Gio.MemoryInputStream.new_from_data(img_buffer, None)
                pixbuf = Pixbuf.new_from_stream(img_buffer, None)
                pixbuf = pixbuf.scale_simple(32, 32, InterpType.BILINEAR)
            result["pixbuf"] = pixbuf
        GLib.idle_add(self.display_search_results)

    def restore_search_button(self):
        self.searchbutton.set_sensitive(True)
        self.searchbutton.set_label("Search!")

    def display_search_results(self):
        self.search_thread.join()
        self.listbox1.set_sensitive(False)
        for result in self.extmgr.search_results.values():

            # Create a box for each item
            resultbox = Gtk.Box()
            name_label = Gtk.Label(label=result["name"])
            name_label.set_halign(Gtk.Align.START)

            # Create the label image
            img = Gtk.Image()
            img.set_from_pixbuf(result["pixbuf"])
            img.set_halign(Gtk.Align.START)

            resultbox.pack_start(img, True, True, 0)
            resultbox.pack_end(name_label, True, True, 0)

            listboxrow = Gtk.ListBoxRow()
            listboxrow.add(resultbox)
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

        uuid = list(self.extmgr.search_results.keys())[id]
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
        item = list(self.extmgr.list_extensions().values())[id]
        uuid = list(self.extmgr.list_extensions().keys())[id]
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
            item = list(self.extmgr.list_extensions().values())[id]

            if item["type"] == 2:
                self.removebutton.set_sensitive(True)
            else:
                self.removebutton.set_sensitive(False)
    
    def on_config_button_clicked(self, widget, uuid):
        self.extmgr.launch_extension_prefs(uuid)

if __name__ == "__main__":
    win = MainWindow()
    Gtk.main()
