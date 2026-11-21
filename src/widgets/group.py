# Imports
from gi.repository import Adw

# Internal imports
from .shared import get_children


class Group(Adw.PreferencesGroup):
  """An AdwPreferencesGroup, but with a way to get its children."""

  __gtype_name__ = 'Group'

  def __init__(self, **kwargs):
    super().__init__(**kwargs)

  def get_rows(self) -> list:
    rows = []
    listbox = self.get_first_child().get_last_child().get_first_child()
    rows += get_children(listbox)
    return rows
