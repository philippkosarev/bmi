from gi.repository import GObject, Gtk

from .base_row import BaseRow


class SwitchRow(BaseRow):
  __gtype_name__ = 'SwitchRow'

  value = GObject.Property(type=bool, default=False)

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.switch = Gtk.Switch(valign=Gtk.Align.CENTER, can_focus=False)
    self.add_suffix(self.switch)
    self.set_activatable_widget(self.switch)
    self.wire_property('value', self.switch, 'active')

  def get_value(self) -> bool:
    return self.value

  def set_value(self, value: bool):
    self.value = value
