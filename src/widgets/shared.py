# Imports
from gi.repository import Gtk
from enum import Enum


# Should always be in the same order as the StringList of gender_input_row.
class Gender(Enum):
  AVERAGE = 0
  FEMALE = 1
  MALE = 2


def get_nth_child(widget: Gtk.Widget, pos: int) -> Gtk.Widget or None:
  """Gets the nth child of a given widget.

  If not found raises AttributeError.
  """
  last_widget = widget
  for i in range(pos):
    if hasattr(widget, 'get_child'):
      widget = widget.get_child()
    elif hasattr(widget, 'get_first_child'):
      widget = widget.get_first_child()
    else:
      widget = None
    if widget is None:
      raise AttributeError('child', last_widget)
    last_widget = widget
  return widget


def get_children(widget: Gtk.Widget) -> list:
  """Returns a list of all children of a given widgets."""
  child = get_nth_child(widget, 1)
  if child is None:
    return []
  children = [child]
  while True:
    child = child.get_next_sibling()
    if child is None:
      return children
    children.append(child)


def kg_to_lb(value: float) -> float:
  return value * 2.2046226218


_lb_to_kg = 1 / kg_to_lb(1)


def lb_to_kg(value: float) -> float:
  return value * _lb_to_kg


def in_to_cm(value):
  return value * 2.54


_cm_to_in = 1 / in_to_cm(1)


def cm_to_in(value):
  return value * _cm_to_in
