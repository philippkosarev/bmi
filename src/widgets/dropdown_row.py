# Imports
from gi.repository import GLib, GObject, Adw


class DropDownRow(Adw.ComboRow):
  __gtype_name__ = 'DropDownRow'

  key = GObject.Property(type=str)
  value = GObject.Property(type=int, default=0)

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    GLib.idle_add(lambda: DropDownRow._post_init(self))

  def _post_init(self):
    flags = (
      GObject.BindingFlags.BIDIRECTIONAL
      | GObject.BindingFlags.SYNC_CREATE
    )
    self.set_property('selected', self.value)
    self.bind_property('selected', self, 'value', flags)

  def get_key(self) -> str:
    return self.key

  def set_key(self, key: str):
    self.key = key

  def get_value(self) -> int:
    return self.value

  def set_value(self, value: int):
    self.value = value
