from gi.repository import GObject, Gtk

from .base_row import BaseRow


class SpinRow(BaseRow):
  __gtype_name__ = 'SpinRow'

  digits = GObject.Property(type=int, default=1)
  lower = GObject.Property(type=float, default=0.1)
  upper = GObject.Property(type=float, default=999.9)
  value = GObject.Property(type=float, default=10.0)

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    # Creating the spin button
    self.spin_button = Gtk.SpinButton(
      xalign=1,
      hexpand=True,
      valign=Gtk.Align.CENTER,
      css_classes=['spin'],
      climb_rate=1,
    )
    adjustment = self.spin_button.get_adjustment()
    self._update_step_increment()
    adjustment.set_page_size(0)
    # Wiring spin button properties
    self.wire_property('digits', self.spin_button)
    self.wire_property('lower', adjustment)
    self.wire_property('upper', adjustment)
    self.wire_property('value', adjustment)
    # Setting up self
    self.add_suffix(self.spin_button)
    self.set_size_request(260, 60)
    self.set_activatable(True)
    self.set_css_classes(['spin'])
    self.connect('notify::digits', self._on_digits_changed)

  def _on_digits_changed(self, *args):
    self._update_step_increment()

  def _update_step_increment(self):
    step_increment = 1 / 10 ** self.digits
    page_increment = step_increment * 10
    self.spin_button.set_increments(step_increment, page_increment)

  def get_value(self) -> float:
    return self.value

  def set_value(self, value: float):
    self.value = value

  def get_digits(self) -> int:
    return self.digits

  def set_digits(self, digits: int):
    self.digits = digits

  def get_lower(self) -> float:
    return self.lower

  def set_lower(self, lower: float):
    self.lower = lower

  def get_upper(self) -> float:
    return self.upper

  def set_upper(self, upper: float):
    self.upper = upper
