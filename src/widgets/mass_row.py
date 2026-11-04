# Imports
from gi.repository import GLib, GObject

# Internal imports
from .spin_row import SpinRow
from .shared import kg_to_lb, lb_to_kg


class MassRow(SpinRow):
  __gtype_name__ = 'MassRow'

  imperial = GObject.Property(type=bool, default=False)

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self._last_imperial = type(self).imperial.default
    GLib.idle_add(self._post_init)

  def _post_init(self):
    self._on_imperial_changed()
    self.connect('notify::imperial', self._on_imperial_changed)

  def _on_imperial_changed(self, *args):
    if self.imperial:
      subtitle = _("Pounds")
      convert_func = kg_to_lb
    else:
      subtitle = _('Kilograms')
      convert_func = lb_to_kg
    if self.imperial != self._last_imperial:
      self.value = convert_func(self.value)
    self.set_subtitle(subtitle)
    self._last_imperial = self.imperial

  def get_imperial(self) -> bool:
    return self.imperial

  def set_imperial(self, imperial: bool):
    self.imperial = imperial

  def get_kilograms(self):
    if self.imperial:
      return lb_to_kg(self.get_value())
    else:
      return self.get_value()

  def get_pounds(self):
    if self.imperial:
      return self.get_value()
    else:
      return kg_to_lb(self.get_value())
