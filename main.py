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
        self.searchbox = Gtk.HBox()
        self.page1.pack_start(self.searchbox, True, True, 0)
        self.page1.set_border_width(10)
        self.notebook.append_page(self.page1, Gtk.Label(label="Download Extensions"))

        # Layout for page2
        self.page2 = Gtk.Box()
        self.page2.set_border_width(10)
        self.notebook.append_page(self.page2, Gtk.Label(label="Installed Extensions"))

        # Create and attach SearchBar to grid
        self.searchbar = Gtk.SearchBar()
        self.searchentry = Gtk.SearchEntry()
        self.searchbar.connect_entry(self.searchentry)
        self.searchbar.add(self.searchentry)
        self.searchbar.set_search_mode(True)
        self.searchbox.pack_start(self.searchbar, True, True, 0)

        # Create and attach search button
        self.searchbutton = Gtk.Button(label="Search")
        self.searchbutton.connect("clicked", self.on_searchbutton_clicked)
        self.searchbox.pack_start(self.searchbutton, True, True, 0)

        # Create and attach ListBox1 to page1
        self.listbox1 = Gtk.ListBox()
        self.page1.pack_start(self.listbox1, True, True, 0)
        self.installbutton = Gtk.Button(label="Install")
        self.installbutton.connect("clicked", self.on_installbutton_clicked)
        self.page1.pack_end(self.installbutton, True, True, 0)

        # Create and attach ListBox2 to page2
        self.listbox2 = Gtk.ListBox()
        self.page2.pack_start(self.listbox2, True, True, 0)

        # Create the ExtensionsManagerobject
        self.extmgr = extensionmanager.ExtensionManager()

        # Populate page2
        self.ShowInstalledExtensions()

    def ShowInstalledExtensions(self):
        print("running")
        print(self.extmgr.installed)
        for name in self.extmgr.installed:
            print(name)
            listboxrow = ListBoxRowWithData(name)
            self.listbox2.add(listboxrow)
        
        # Display after refresh
        self.listbox2.show_all()
        self.show_all()
    
    def ShowResults(self):
        # Clear old entries
        for entry in self.listbox1.get_children():
            self.listbox1.remove(entry)

        # Refresh results and populate list
        self.extmgr.search(self.searchentry.get_text())
        for result in self.extmgr.results:
            listboxrow = ListBoxRowWithData(result["name"])
            self.listbox1.add(listboxrow)
        
        # Display after refresh
        self.listbox1.show_all()
        self.show_all()
    
    def on_searchbutton_clicked(self, widget):
        self.ShowResults()
    
    def on_installbutton_clicked(self, widget):
        self.installbutton.set_sensitive(False)
        id = self.listbox1.get_selected_row().get_index()
        self.extmgr.getExtension(id)
        self.installbutton.set_sensitive(True)

win = MainWindow()
win.show_all()
Gtk.main()
