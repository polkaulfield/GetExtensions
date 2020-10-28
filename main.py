#!/usr/bin/python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

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

        # Create notebook for tabs
        self.notebook = Gtk.Notebook()
        self.add(self.notebook)

        # Layout for page1
        self.page1 = Gtk.VBox()
        self.page1.set_spacing(10)
        self.searchbox = Gtk.HBox()
        self.page1.pack_start(self.searchbox, True, True, 0)
        self.page1.set_border_width(10)
        self.notebook.append_page(self.page1, Gtk.Label(label="Download Extensions"))

        # Layout for page2
        self.page2 = Gtk.VBox()
        self.page2.set_border_width(10)
        self.notebook.append_page(self.page2, Gtk.Label(label="Installed Extensions"))

        # Create and attach Entry field to grid
        self.entry = Gtk.Entry()
        self.entry.connect("key-press-event",self.on_key_press_event)
        self.searchbox.pack_start(self.entry, True, True, 0)

        # Create and attach search button
        self.searchbutton = Gtk.Button(label="Search")
        self.searchbutton.connect("clicked", self.on_searchbutton_clicked)
        self.searchbox.pack_start(self.searchbutton, True, True, 0)
        
        # Create and attach ListBox1 and install button to page1
        self.listbox1 = Gtk.ListBox()
        self.page1.pack_start(self.listbox1, True, True, 0)
        self.listbox1.connect("row-selected", self.on_listbox1_row_selected)
        self.installbutton = Gtk.Button(label="Install")
        self.installbutton.connect("clicked", self.on_installbutton_clicked)
        self.installbutton.set_sensitive(False)
        self.page1.pack_end(self.installbutton, True, True, 0)

        # Create and attach ListBox2 and delete button to page2
        self.listbox2 = Gtk.ListBox()
        self.page2.pack_start(self.listbox2, True, True, 0)
        self.listbox2.connect("row-selected", self.on_listbox2_row_selected)
        self.removebutton = Gtk.Button(label="Remove")
        self.removebutton.connect("clicked", self.on_removebutton_clicked)
        self.removebutton.set_sensitive(False)
        self.page2.pack_end(self.removebutton, True, True, 0)

        # Create the ExtensionsManagerobject
        self.extmgr = extensionmanager.ExtensionManager()

        # Populate page2
        self.show_installed_extensions()

    def show_installed_extensions(self):
        # Clear old entries
        for entry in self.listbox2.get_children():
            self.listbox2.remove(entry)

        for name in self.extmgr.installed:
            listboxrow = ListBoxRowWithData(name)
            self.listbox2.add(listboxrow)

        # Display after refresh
        self.listbox2.show_all()
        self.show_all()

    def show_results(self):
        # Clear old entries
        for entry in self.listbox1.get_children():
            self.listbox1.remove(entry)
        
        # Disable install button until you have something selected
        self.installbutton.set_sensitive(False)

        # Refresh results and populate list
        self.extmgr.search(self.entry.get_text())
        for result in self.extmgr.results:
            listboxrow = ListBoxRowWithData(result["name"])
            self.listbox1.add(listboxrow)

        # Display after refresh
        self.listbox1.show_all()
        self.show_all()
    
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
        self.extmgr.remove(self.extmgr.installed[id])
        self.removebutton.set_sensitive(True)
        self.show_installed_extensions()
    
    def on_listbox1_row_selected(self, widget, row):
        self.installbutton.set_sensitive(True)
    
    def on_listbox2_row_selected(self, widget, row):
        self.removebutton.set_sensitive(True)

win = MainWindow()
win.show_all()
Gtk.main()
