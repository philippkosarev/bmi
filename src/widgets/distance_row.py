# Imports
from gi.repository import GLib, GObject

# Internal imports
from .spin_row import SpinRow
from .shared import cm_to_in, in_to_cm


class DistanceRow(SpinRow):
  __gtype_name__ = 'DistanceRow'

  imperial = GObject.Property(type=bool, default=False)

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    GLib.idle_add(self._post_init)

  def _post_init(self):
    self._last_imperial = self.imperial
    self._on_imperial_changed()
    self.connect('notify::imperial', self._on_imperial_changed)

  def get_imperial(self) -> bool:
    return self.imperial

  def set_imperial(self, imperial: bool):
    self.imperial = imperial

  def _on_imperial_changed(self, *args):
    if self.imperial:
      subtitle = _("Inches")
      convert_func = cm_to_in
    else:
      convert_func = in_to_cm
      subtitle = _("Centimetres")
    self.set_subtitle(subtitle)
    if self.imperial != self._last_imperial:
      self.value = convert_func(self.value)
    self._last_imperial = self.imperial

  def get_centimetres(self):
    """Returns the current value in centimetres."""
    value = self.get_value()
    if self.imperial:
      value = in_to_cm(value)
    return value

  def get_inches(self):
    """Returns the current value in inches."""
    value = self.get_value()
    if not self.imperial:
      value = cm_to_in(value)
    return value
