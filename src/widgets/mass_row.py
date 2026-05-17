# Imports
from gi.repository import GObject, Gtk, Adw

# Internal imports
from .spin_row import SpinRow
from .shared import *

# Class
class MassRow(SpinRow):
  __gtype_name__ = 'MassRow'

  imperial = GObject.Property(
    type=bool, default=False,
  )

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.set_subtitle(_('Kilograms'))

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

  def set_imperial(self, imperial: bool):
    if self.imperial is imperial:
      return
    value = self.get_value()
    if imperial is True:
      value = kg_to_lb(value)
      self.set_subtitle(_('Pounds'))
    else:
      value = lb_to_kg(value)
      self.set_subtitle(_('Kilograms'))
    value = round(value, 1)
    self.imperial = imperial
    self.set_value(value)
