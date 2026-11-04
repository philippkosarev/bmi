# Imports
from gi.repository import GLib, GObject, Gio, Gtk, Adw


class Threshold(GObject.Object):
  name = GObject.Property(type=str)
  value = GObject.Property(type=float)
  style = GObject.Property(type=str)

  def __init__(self, name: str, value: float, style: str):
    super().__init__()
    self.name = name
    self.value = value
    self.style = style

  def __getitem__(self, index: int):
    if index == 0:
      return self.name
    elif index == 1:
      return self.value
    elif index == 2:
      return self.style
    else:
      raise IndexError

  def get_name(self) -> str:
    return self.name

  def set_name(self, name: str):
    self.name = name

  def get_value(self) -> float:
    return self.value

  def set_value(self, value: float):
    self.value = value

  def get_style(self) -> str:
    return self.style

  def set_style(self, style: str):
    self.style = style


class Thresholds(GObject.Object):
  items = GObject.Property(type=Gio.ListStore)

  def __init__(self, *thresholds: Threshold|tuple):
    super().__init__()
    thresholds = list(thresholds)
    thresholds.sort(key=lambda i: i[1])
    self.items = Gio.ListStore.new(Threshold)
    for i, item in enumerate(thresholds):
      if isinstance(item, tuple):
        item = Threshold(*item)
      self.items.append(item)

  def __len__(self) -> int:
    return len(self.items)

  def __getitem__(self, index: int) -> Threshold:
    return self.items[index]

  def __iter__(self) -> Threshold:
    for item in self.items:
      yield item

  def append(self, threshold: Threshold):
    self.items.append(threshold)


@Gtk.Template(resource_path='/io/github/philippkosarev/bmi/widgets/result_dialog.ui')
class ResultDialog(Adw.Dialog):
  __gtype_name__ = 'ResultDialog'

  # Properties
  result_label = GObject.Property(type=str)
  feedback_label = GObject.Property(type=str)
  thresholds = GObject.Property(type=Thresholds)
  context_description = GObject.Property(type=str)
  context_thresholds = GObject.Property(type=Thresholds)

  # Widgets
  _result_label = Gtk.Template.Child('result_label')
  _feedback_label = Gtk.Template.Child('feedback_label')
  _thresholds_group = Gtk.Template.Child('thresholds_group')
  _context_group = Gtk.Template.Child('context_group')

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    flags = (
      GObject.BindingFlags.BIDIRECTIONAL
      | GObject.BindingFlags.SYNC_CREATE
    )
    self.bind_property(
      'result-label', self._result_label, 'label', flags,
    )
    self.bind_property(
      'feedback-label', self._feedback_label, 'label', flags,
    )
    self.bind_property(
      'context-description', self._context_group, 'description', flags,
    )
    self.connect('notify::thresholds', self._on_thresholds_changed)
    self.connect(
      'notify::context-thresholds', self._on_context_thresholds_changed,
    )

  def get_result_label(self) -> str:
    return self.result_label

  def set_result_label(self, label: str):
    self.result_label = label

  def get_feedback_label(self) -> str:
    return self.feedback_label

  def set_feedback_label(self, label: str) -> str:
    self.feedback_label = label

  def get_thresholds(self) -> Thresholds|None:
    return self.thresholds

  def set_thresholds(self, thresholds: None|Thresholds|list|tuple):
    if isinstance(thresholds, (list, tuple)):
      thresholds = Thresholds(*thresholds)
    self.thresholds = thresholds

  def get_context_description(self) -> str:
    return self.context_description

  def set_context_description(self, description: str):
    self.context_description = description

  def get_context_thresholds(self) -> Thresholds|None:
    return self.context_thresholds

  def set_context_thresholds(self, thresholds: Thresholds|None):
    self.context_thresholds = thresholds

  def _on_thresholds_changed(self, *args):
    self._set_group_thresholds(self._thresholds_group, self.thresholds)

  def _on_context_thresholds_changed(self, *args):
    self._set_group_thresholds(self._context_group, self.context_thresholds)

  def _set_group_thresholds(
    self,
    group: Adw.PreferencesGroup,
    thresholds: Thresholds|None,
  ):
    while row := group.get_row(0):
      group.remove(row)
    if not thresholds:
      group.set_visible(False)
      return
    group.set_visible(True)
    n_thresholds = len(thresholds)
    for i in range(n_thresholds):
      this_value = thresholds[i].value
      if this_value.is_integer():
        this_value = int(this_value)
      if i + 1 < n_thresholds:
        next_value = thresholds[i + 1].value
        if next_value.is_integer():
          next_value = int(next_value)
      else:
        next_value = None
      if not this_value and next_value:
        qualifier = _("Under {}")
        qualifier = qualifier.format(next_value)
      elif this_value and not next_value:
        qualifier = _("{} and over")
        qualifier = qualifier.format(this_value)
      elif this_value and next_value:
        qualifier = _("{} to {}")
        qualifier = qualifier.format(this_value, next_value)
      else:
        values = [t.value for t in thresholds]
        raise ValueError(f'Invalid threshold values {values!r}')
      row = Adw.ActionRow(
        title=qualifier,
        css_classes=['heading', thresholds[i].style],
        title_selectable=True,
      )
      feedback_label = Gtk.Label(
        label=thresholds[i].name,
        selectable=True,
      )
      row.add_suffix(feedback_label)
      group.add(row)


class ResultRow(Adw.ActionRow):
  __gtype_name__ = 'ResultRow'

  # Properties
  result = GObject.Property(type=float, default=0.0)
  digits = GObject.Property(type=int, default=2)
  result_label = GObject.Property(type=str, default='0.0')
  thresholds = GObject.Property(type=Thresholds)
  context_description = GObject.Property(type=str, default='')
  context_thresholds = GObject.Property(type=Thresholds)

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    # Setting up self
    self.set_size_request(300, 60)
    self.set_activatable(True)
    self.set_css_classes(['heading'])
    # Creating the result label
    self._result_label = Gtk.Label(
      label=self.result_label,
      valign=Gtk.Align.CENTER,
      css_classes=['title-3'],
    )
    self.add_suffix(self._result_label)
    # Creating the info button
    self._info_button = Gtk.Button(
      valign=Gtk.Align.CENTER,
      css_classes=['circular', 'flag'],
      icon_name='help-about-symbolic',
      visible=False,
    )
    self.connect('notify::thresholds', self._on_thresholds_changed)
    self._info_button.connect('clicked', self._on_info_button_clicked)
    self.add_suffix(self._info_button)
    GLib.idle_add(self._post_init)

  def _post_init(self):
    flags = GObject.BindingFlags.BIDIRECTIONAL
    self.connect('notify::result', self._on_result_changed)
    self.bind_property(
      'result-label', self._result_label, 'label', flags,
    )
    self._on_result_changed()

  def set_css_classes(self, css_classess: list):
    styles = ['heading', *css_classess]
    if self.get_activatable():
      styles.append('activatable')
    super().set_css_classes(styles)

  def set_digits(self, digits: int):
    self.digits = digits

  def get_digits(self) -> int:
    return self.digits

  def get_result(self) -> float:
    return self.result

  def set_result(self, result: float):
    self.result = result

  def get_result_label(self) -> str:
    return self.result_label

  def set_result_label(self, label: str):
    self.result_label = label

  def get_thresholds(self) -> Thresholds:
    return self.thresholds

  def set_thresholds(self, thresholds: None|Thresholds|list|tuple):
    if isinstance(thresholds, (list, tuple)):
      thresholds = Thresholds(*thresholds)
    self.thresholds = thresholds

  def get_context_description(self) -> str:
    return self.context_descriptionl

  def set_context_description(self, description: str):
    self.context_description = description

  def get_context_thresholds(self) -> Thresholds:
    return self.context_thresholds

  def set_context_thresholds(self, thresholds: Thresholds):
    self.context_thresholds = thresholds

  def _on_info_button_clicked(self, *args):
    self.show_dialog()

  def show_dialog(self):
    dialog = ResultDialog()
    dialog.set_title(self.get_title())
    dialog.set_result_label(self.result_label)
    dialog.set_feedback_label(self.get_subtitle())
    dialog.set_thresholds(self.thresholds)
    dialog.set_context_description(self.context_description)
    dialog.set_context_thresholds(self.context_thresholds)
    dialog.present(self.get_root())

  def _update_feedback(self):
    if not self.thresholds:
      return
    for threshold in reversed(self.thresholds):
      if self.result > threshold.value:
        self.set_subtitle(threshold.name)
        self.set_css_classes([threshold.style])
        break

  def _on_result_changed(self, *args):
    self._update_feedback()
    self.result_label = str(round(self.result, self.digits))

  def _on_thresholds_changed(self, *args):
    self._update_feedback()
    self._info_button.set_visible(self.thresholds is not None)
