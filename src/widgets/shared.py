from gi.repository import Gtk


def get_nth_child(widget: Gtk.Widget, pos: int) -> Gtk.Widget|None:
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
