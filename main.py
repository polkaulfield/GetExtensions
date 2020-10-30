#!/usr/bin/python3
import gi, threading
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository.GdkPixbuf import Pixbuf, InterpType
from gi.repository import Gio

# Local modules
import extensionmanager

class ListBoxRowWithData(Gtk.ListBoxRow):
    def __init__(self, data):
        super(Gtk.ListBoxRow, self).__init__()
        self.data = data
        self.add(Gtk.Label(label=data))

class MainWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Get Extensions")
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

        # Refresh installed extensions (todo with get property, kinda spaghetti now)
        self.extmgr.list_all_extensions()

        for item in self.extmgr.installed:            
            # Create a box for each item
            itembox = Gtk.HBox()
            name_label = Gtk.Label()

            # Check if the extension name is longer than 20 chars and trim it
            num = 30
            if len(item["name"]) >= num:
                name_label.set_text(str=item["name"][:num] + "...")
            else:
                name_label.set_text(str=item["name"])

            name_label.set_halign(1)

            switch = Gtk.Switch()
            switch.connect("notify::active", self.on_switch_activated, item["uuid"])
            switch.set_halign(1)
            if item["enabled"] == True:
                switch.set_active(True)
            else:
                switch.set_active(False)

            itembox.pack_start(switch, True, True, 0)
            itembox.pack_end(name_label, True, True, 0)

            listboxrow = Gtk.ListBoxRow()
            listboxrow.add(itembox)
            self.listbox2.add(listboxrow)

        # Display after refresh
        self.listbox2.show_all()
        self.show_all()
    
    def show_error(self, message):
        # TODO error box
        print(message)

    def search_from_entry(self):
        self.listbox1.set_sensitive(False)
        if self.extmgr.search(self.entry.get_text()) == 1:
            self.show_error("Couldn't fetch the extensions list.")
        
        for index, result in enumerate(self.extmgr.results):

            # Create a box for each item
            resultbox = Gtk.HBox()
            name_label = Gtk.Label(label=result["name"])
            name_label.set_halign(1)

            # Download the image into a buffer and render it with pixbuf
            img_buffer = self.extmgr.get_image(self.extmgr.get_uuid(index))
            
            # Check if the extension icon is local (faster searching)
            if img_buffer == None:
                pixbuf = Pixbuf.new_from_file("plugin.png")
            else:
                img_buffer = Gio.MemoryInputStream.new_from_data(img_buffer, None)
                pixbuf = Pixbuf.new_from_stream(img_buffer, None)
                pixbuf = pixbuf.scale_simple(32, 32, InterpType.BILINEAR)

            # Create the label image
            img = Gtk.Image()
            img.set_from_pixbuf(pixbuf)
            img.set_halign(1)

            resultbox.pack_start(img, True, True, 0)
            resultbox.pack_end(name_label, True, True, 0)

            listboxrow = Gtk.ListBoxRow()
            listboxrow.add(resultbox)
            self.listbox1.add(listboxrow)

        self.listbox1.show_all()
        self.show_all()
        
        # Reenable search button
        self.listbox1.set_sensitive(True)
        self.searchbutton.set_sensitive(True)
        self.searchbutton.set_label("Search!")
        return

    def show_results(self):
        # Disable search button while searching
        self.searchbutton.set_sensitive(False)
        self.searchbutton.set_label("Searching...")

        # Clear old entries
        for entry in self.listbox1.get_children():
            self.listbox1.remove(entry)
        
        # Disable install button until you have something selected
        self.installbutton.set_sensitive(False)

        # Start thread to add results
        self.search_thread = threading.Thread(target=self.search_from_entry)
        self.search_thread.start()

    def on_switch_activated(self, switch, gparam, name):
        if switch.get_active():
            self.extmgr.set_extension_status(name, "enable")
            print(name + " enabled")
        else:
            self.extmgr.set_extension_status(name, "disable")
            print(name + " disabled")
    
    def on_key_press_event(self, widget, event):
        # Enter key value
        if event.keyval == 65293:
            self.show_results()

    def on_searchbutton_clicked(self, widget):
        self.show_results()

    def on_installbutton_clicked(self, widget):
        self.installbutton.set_sensitive(False)
        id = self.listbox1.get_selected_row().get_index()
        self.extmgr.get_extensions(self.extmgr.results[id]["uuid"])
        self.installbutton.set_sensitive(True)
        self.show_installed_extensions()
    
    def on_removebutton_clicked(self, widget):
        self.removebutton.set_sensitive(False)
        id = self.listbox2.get_selected_row().get_index()
        self.extmgr.remove(self.extmgr.installed[id]["uuid"])
        self.removebutton.set_sensitive(True)
        self.show_installed_extensions()
    
    def on_listbox1_row_selected(self, widget, row):
        self.installbutton.set_sensitive(True)
    
    def on_listbox2_row_selected(self, widget, row):
        id = self.listbox2.get_selected_row().get_index()
        if self.extmgr.installed[id]["local"]:
            self.removebutton.set_sensitive(True)
        else:
            self.removebutton.set_sensitive(False)

win = MainWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
