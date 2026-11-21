# Imports
from gi.repository import GLib, GObject, Adw


class BaseRow(Adw.ActionRow):
  __gtype_name__ = 'BaseRow'

  key = GObject.Property(type=str)

  def __init__(self, **kwargs):
    super().__init__(**kwargs)

  def get_key(self) -> str:
    return self.key

  def set_key(self, key: str):
    self.key = key

  def wire_property(
    self,
    prop_name: str,
    source: GObject.Object,
    source_prop_name: str|None = None,
  ):
    """Binds the target's property to this row's property."""
    if not source_prop_name:
      source_prop_name = prop_name
    GLib.idle_add(self._wire_property, prop_name, source, source_prop_name)

  def _wire_property(
    self,
    prop_name: str,
    source: GObject.Object,
    source_prop_name: str,
  ):
    value = self.get_property(prop_name)
    source.set_property(source_prop_name, value)
    flags = (
      GObject.BindingFlags.BIDIRECTIONAL
      | GObject.BindingFlags.SYNC_CREATE
    )
    self.bind_property(prop_name, source, source_prop_name, flags)
