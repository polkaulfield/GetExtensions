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

        # Create Grid
        grid = Gtk.Grid()
        self.add(grid)

        # Create and attach SearchBar to grid
        self.searchbar = Gtk.SearchBar()
        grid.attach(self.searchbar, 0, 1, 1, 1)
        self.searchentry = Gtk.SearchEntry()
        self.searchbar.connect_entry(self.searchentry)
        self.searchbar.add(self.searchentry)
        self.searchbar.set_search_mode(True)

        # Create and attach search button
        self.searchbutton = Gtk.Button(label="Search")
        self.searchbutton.connect("clicked", self.on_searchbutton_clicked)
        grid.attach(self.searchbutton, 1, 1, 1, 1)

        # Create and attach ListBox to grid
        self.listbox = Gtk.ListBox()
        grid.attach(self.listbox,0, 2, 2, 1)

        self.installbutton = Gtk.Button(label="Install")
        self.installbutton.connect("clicked", self.on_installbutton_clicked)
        grid.attach(self.installbutton, 0, 3, 2, 1)

        # Create the ExtensionsManagerobject
        self.extmgr = extensionmanager.ExtensionManager()

    def ShowResults(self):
        # Clear old entries
        for entry in self.listbox.get_children():
            self.listbox.remove(entry)

        # Refresh results and populate list
        self.extmgr.search(self.searchentry.get_text())
        for result in self.extmgr.results:
            listboxrow = ListBoxRowWithData(result["name"])
            self.listbox.add(listboxrow)
        
        # Display after refresh
        self.listbox.show_all()
        self.show_all()
    
    def on_searchbutton_clicked(self, widget):
        self.ShowResults()
    
    def on_installbutton_clicked(self, widget):
        id = self.listbox.get_selected_row().get_index()
        self.extmgr.getMatchingVersion(id)

win = MainWindow()
win.show_all()
Gtk.main()
