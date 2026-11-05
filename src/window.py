from gi.repository import GObject, Gtk, Adw, Gio, Gdk

from . import calc
from .widgets import Threshold, Thresholds, ResultRow


@Gtk.Template(resource_path='/io/github/philippkosarev/bmi/window.ui')
class BmiWindow(Adw.ApplicationWindow):
  __gtype_name__ = 'BmiWindow'

  # Properties
  settings = GObject.Property(type=Gio.Settings)
  units = GObject.Property(type=calc.Units, default=calc.Units.METRIC)

  # Important Widgets
  toast_overlay = Gtk.Template.Child()

  # Input rows
  height_input_row = Gtk.Template.Child()
  weight_input_row = Gtk.Template.Child()
  waist_input_row = Gtk.Template.Child()
  hip_input_row = Gtk.Template.Child()
  gender_input_row = Gtk.Template.Child()
  age_input_row = Gtk.Template.Child()

  # Result rows
  bmi_result_row = Gtk.Template.Child()
  bri_result_row = Gtk.Template.Child()
  whr_result_row = Gtk.Template.Child()
  whtr_result_row = Gtk.Template.Child()

  def __init__(self, app: Gio.Application):
    # Setting up self
    super().__init__(application=app)
    self.settings = app.get_settings()
    flags = GObject.BindingFlags.BIDIRECTIONAL
    self.bind_property('settings', app, 'settings', flags)
    self.settings.connect('changed', self._on_settings_value_changed)
    self.connect('close-request', self._on_close_request)
    self.connect('notify::units', self._on_units_changed)
    self.set_default_size(*self.settings['window-size'])
    # Setting static result row thresholds
    self.bmi_result_row.set_thresholds([
      (_("Underweight [Severe]"),   0,    'error'),
      (_("Underweight [Moderate]"), 16,   'warning'),
      (_("Underweight [Mild]"),     17,   'warning'),
      (_("Healthy"),                18.5, 'success'),
      (_("Overweight"),             25,   'warning'),
      (_("Obese [Class 1]"),        30,   'error'),
      (_("Obese [Class 2]"),        35,   'error'),
      (_("Obese [Class 3]"),        40,   'error'),
    ])
    self.bri_result_row.set_thresholds([
      (_("Very lean"),     0,    'success'),
      (_("Lean"),          3.41, 'success'),
      (_("Average"),       4.45, 'success'),
      (_("Above average"), 5.46, 'success'),
      (_("High"),          6.91, 'warning'),
    ])
    # Setting units
    self._last_units = self.get_units()
    self.set_units(self.settings['units'])
    # Setting initial input row values
    self.height_input_row.set_value(self.settings['height'])
    self.weight_input_row.set_value(self.settings['mass'])
    self.waist_input_row.set_value(self.settings['waist'])
    self.hip_input_row.set_value(self.settings['hip'])
    self.gender_input_row.set_value(self.settings['gender'])
    self.age_input_row.set_value(self.settings['age'])
    # Connecting input rows
    self.height_input_row.connect('notify::value', self._on_height_input_changed)
    self.weight_input_row.connect('notify::value', self._on_weight_input_changed)
    self.waist_input_row.connect('notify::value', self._on_waist_input_changed)
    self.hip_input_row.connect('notify::value', self._on_hip_input_changed)
    self.gender_input_row.connect('notify::value', self._on_gender_input_changed)
    self.age_input_row.connect('notify::value', self._on_age_input_changed)
    # Connecting result rows
    for row in [
      self.bmi_result_row,
      self.whtr_result_row,
      self.whr_result_row,
      self.bri_result_row,
    ]:
      row.connect('activated', self._on_result_copied)
    # Calculating initial results
    self.recalculate_results()
    self._initialised = True

  def get_settings(self) -> Gio.Settings:
    return self.settings

  def set_settings(self, settings: Gio.Settings):
    self.settings = settings

  def get_units(self) -> calc.Units:
    return self.units

  def set_units(self, units: calc.Units):
    self.units = units

  def _remember_input(self, key: str, value: any):
    if self.settings['remember-inputs']:
      self.settings[key] = value

  def _on_height_input_changed(self, *args):
    self._remember_input('height', self.height_input_row.value)
    self.update_bmi()
    self.update_bri()

  def _on_weight_input_changed(self, *args):
    self._remember_input('mass', self.weight_input_row.value)
    self.update_bmi()

  def _on_waist_input_changed(self, *args):
    self._remember_input('waist', self.waist_input_row.value)
    self.update_bri()
    self.update_whr()
    self.update_whtr()

  def _on_hip_input_changed(self, *args):
    self._remember_input('hip', self.hip_input_row.value)
    self.update_whr()

  def _on_gender_input_changed(self, *args):
    self._remember_input('gender', self.gender_input_row.value)
    self.update_whr_thresholds()

  def _on_age_input_changed(self, *args):
    self._remember_input('age', self.age_input_row.value)
    self.update_whtr_thresholds()

  def _get_len_row_value_in_cm(self, input_row) -> float:
    value = input_row.get_value()
    if self.units == calc.Units.IMPERIAL:
      value = calc.in_to_cm(value)
    return value

  def get_height_in_cm(self) -> float:
    return self._get_len_row_value_in_cm(self.height_input_row)

  def get_waist_in_cm(self) -> float:
    return self._get_len_row_value_in_cm(self.waist_input_row)

  def get_hip_in_cm(self) -> float:
    return self._get_len_row_value_in_cm(self.hip_input_row)

  def get_weight_in_kg(self) -> float:
    value = self.weight_input_row.get_value()
    if self.units == calc.Units.IMPERIAL:
      value = calc.lb_to_kg(value)
    return value

  def get_gender(self) -> calc.Gender:
    return calc.Gender(self.gender_input_row.value)

  def get_age(self) -> int:
    return self.age_input_row.get_value()

  def update_bmi(self):
    height = self.get_height_in_cm()
    weight = self.get_weight_in_kg()
    result = calc.bmi(height, weight)
    self.bmi_result_row.set_result(result)
    context_thresholds = Thresholds()
    for threshold in self.bmi_result_row.thresholds:
      value = calc.mass_from_bmi_and_height(threshold.value, height)
      if self.units == calc.Units.IMPERIAL:
        value = calc.kg_to_lb(value)
      value = round(value, 1)
      context_thresholds.append(
        Threshold(threshold.name, value, threshold.style)
      )
    self.bmi_result_row.set_context_thresholds(context_thresholds)

  def update_bri(self):
    height = self.get_height_in_cm()
    waist = self.get_waist_in_cm()
    result = calc.bri(height, waist)
    self.bri_result_row.set_result(result)

  def update_whr(self):
    waist = self.get_waist_in_cm()
    hip = self.get_hip_in_cm()
    result = calc.whr(waist, hip)
    self.whr_result_row.set_result(result)

  def update_whtr(self):
    height = self.get_height_in_cm()
    waist = self.get_waist_in_cm()
    result = calc.whtr(waist, height)
    self.whtr_result_row.set_result(result)

  def update_whr_thresholds(self):
    gender = self.get_gender()
    self.whr_result_row.set_thresholds([
      (_("Healthy"),    0,                           'success'),
      (_("Overweight"), calc.whr_overweight(gender), 'warning'),
      (_("Obese"),      calc.whr_obese(gender),      'error'),
    ])

  def update_whtr_thresholds(self):
    age = self.get_age()
    self.whtr_result_row.set_thresholds([
      (_("Healthy"),   0,                        'success'),
      (_("Unhealthy"), calc.whtr_unhealthy(age), 'warning'),
    ])

  def recalculate_results(self):
    self.update_bmi()
    self.update_bri()
    self.update_whr()
    self.update_whr_thresholds()
    self.update_whtr()
    self.update_whtr_thresholds()

  def _on_result_copied(self, row: ResultRow):
    self.show_toast(_("Result copied"))

  def show_toast(self, text: str):
    self.toast_overlay.dismiss_all()
    toast = Adw.Toast(title=text, timeout=1)
    self.toast_overlay.add_toast(toast)

  def _on_settings_value_changed(self, settings: Gio.Settings, key: str):
    handlers = {
      'units': self._on_units_setting_changed,
      'remember-inputs': self._on_remember_inputs_changed,
    }
    handler = handlers.get(key)
    if handler:
      handler()

  def _on_units_setting_changed(self):
    self.set_units(self.settings['units'])

  def _on_units_changed(self, *args):
    self._on_remember_inputs_changed()
    convert_len, convert_mass, len_label, mass_label = {
      calc.Units.IMPERIAL: (
        calc.cm_to_in, calc.kg_to_lb,
        _("Inches"), _("Pounds"),
      ),
      calc.Units.METRIC: (
        calc.in_to_cm, calc.lb_to_kg,
        _("Centimetres"), _("Kilograms"),
      ),
    }[self.units]
    len_rows = [
      self.height_input_row, self.waist_input_row, self.hip_input_row,
    ]
    for row in len_rows:
      row.set_subtitle(len_label)
    self.weight_input_row.set_subtitle(mass_label)
    if self._last_units == self.units:
      return
    self._last_units = self.units
    for row in len_rows:
      value = convert_len(row.value)
      row.set_value(value)
    weight = convert_mass(self.weight_input_row.value)
    self.weight_input_row.set_value(weight)
    if getattr(self, '_initialised', False):
      self.recalculate_results()

  def _on_remember_inputs_changed(self):
    if self.settings['remember-inputs']:
      return
    self.reset_remembered_inputs()
    if self.units == calc.Units.METRIC:
      return
    for convert_func, keys in [
      (calc.cm_to_in, ['height', 'waist', 'hip']),
      (calc.kg_to_lb, ['mass']),
    ]:
      for key in keys:
        self.settings[key] = round(convert_func(self.settings[key]))

  def reset_remembered_inputs(self):
    for key in ['height', 'mass', 'gender', 'age', 'waist', 'hip']:
      self.settings.reset(key)

  def _on_close_request(self, *args):
    width = self.get_size(Gtk.Orientation.HORIZONTAL)
    height = self.get_size(Gtk.Orientation.VERTICAL)
    self.settings['window-size'] = (width, height)
