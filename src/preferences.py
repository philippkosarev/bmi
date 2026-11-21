# Imports
from gi.repository import Gtk, Adw, Gio, GObject

# Internal imports
from .widgets.shared import get_nth_child, get_children


@Gtk.Template(resource_path='/io/github/philippkosarev/bmi/preferences.ui')
class BmiPreferences(Adw.PreferencesDialog):
  __gtype_name__ = 'BmiPreferences'

  settings = GObject.Property(type=Gio.Settings)

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.connect('notify::settings', self._on_settings_changed)
    for row in self.get_rows():
      row.connect('notify::value', self._on_row_value_changed)

  def get_settings(self) -> Gio.Settings:
    return self.settings

  def set_settings(self, settings: Gio.Settings):
    self.settings = settings

  def _on_settings_changed(self, *args):
    if not self.settings:
      return
    # Setting initial values
    for row in self.get_rows():
      row.set_value(self.settings[row.key])

  def _on_row_value_changed(self, row, *args):
    if not self.settings:
      return
    self.settings[row.key] = row.value

  def get_pages(self) -> list:
    navigation_view = self.get_child().get_child()
    navigation_stack = navigation_view.get_navigation_stack()
    page = list(navigation_stack)[0]
    child = page.get_child()
    toolbar_view = child.get_child()
    stack = toolbar_view.get_content()
    toolbar_view = list(stack)[0]
    view_stack = toolbar_view.get_content()
    return [page.get_child() for page in view_stack.get_pages()]

  def get_groups(self) -> list:
    groups = []
    for page in self.get_pages():
      box = get_nth_child(page, 4)
      children = get_children(box)
      groups += [
        widget for widget in children
        if isinstance(widget, Adw.PreferencesGroup)
      ]
    return groups

  def get_rows(self) -> list:
    rows = []
    for group in self.get_groups():
      rows += group.get_rows()
    return rows
