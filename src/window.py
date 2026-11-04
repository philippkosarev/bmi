import math
import re

from gi.repository import GObject, Gtk, Adw, Gio, Gdk

from . import widgets, calculate
from .widgets import cm_to_in, in_to_cm, kg_to_lb, lb_to_kg


@Gtk.Template(resource_path='/io/github/philippkosarev/bmi/window.ui')
class BmiWindow(Adw.ApplicationWindow):
  __gtype_name__ = 'BmiWindow'

  # Properties
  settings = GObject.Property(type=Gio.Settings)

  # Important Widgets
  toast_overlay = Gtk.Template.Child()
  clamp = Gtk.Template.Child()
  orientable_box = Gtk.Template.Child()
  simple_breakpoint = Gtk.Template.Child()
  advanced_breakpoint = Gtk.Template.Child()
  advanced_inputs_clamp = Gtk.Template.Child()

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
    self.set_default_size(*self.settings['window-size'])
    self._on_measurement_system_changed()
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
    # Setting result row thresholds
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
    self.update_whr_thresholds()
    self.update_whtr_thresholds()
    # Connecting result rows
    for row in [
      self.bmi_result_row,
      self.whtr_result_row,
      self.whr_result_row,
      self.bri_result_row,
    ]:
      row.connect('activated', self.copy_result)
    # Calculating initial_results
    self.update_bmi()
    self.update_bri()
    self.update_whr()
    self.update_whtr()
    # Connecting stuff
    self.settings.connect('changed', self._on_settings_value_changed)
    self.simple_breakpoint.connect('apply', self._on_simple_breakpoint_apply)
    self.simple_breakpoint.connect('unapply', self._on_simple_breakpoint_unapply)
    self.advanced_breakpoint.connect('apply', self._on_advanced_breakpoint_apply)
    self.advanced_breakpoint.connect('unapply', self._on_advanced_breakpoint_unapply)
    self.connect('close-request', self._on_close_request)

  def _on_input_row_value_changed(self, row, *args):
    if self.settings['remember-inputs']:
      self.settings[row.key] = row.value
    self.inputs.set_property(row.key, row.value)

  def get_settings(self) -> Gio.Settings:
    return self.settings

  def set_settings(self, settings: Gio.Settings):
    self.settings = settings

  def _remember_input(self, key: str, value: any):
    if self.settings['remember-inputs']:
      self.settings[key] = value

  def _on_height_input_changed(self, *args):
    self._remember_input('height', self.height_input_row.get_value())
    self.update_bmi()
    self.update_bri()

  def _on_weight_input_changed(self, *args):
    self._remember_input('mass', self.weight_input_row.get_value())
    self.update_bmi()

  def _on_waist_input_changed(self, *args):
    self._remember_input('waist', self.waist_input_row.get_value())
    self.update_bri()
    self.update_whr()
    self.update_whtr()

  def _on_hip_input_changed(self, *args):
    self._remember_input('hip', self.hip_input_row.get_value())
    self.update_whr()

  def _on_gender_input_changed(self, *args):
    self._remember_input('gender', self.gender_input_row.get_value())
    self.update_whr_thresholds()

  def _on_age_input_changed(self, *args):
    self._remember_input('age', self.age_input_row.get_value())
    self.update_whtr_thresholds()

  def update_bmi(self):
    height = self.height_input_row.get_centimetres()
    weight = self.weight_input_row.get_kilograms()
    result = calculate.bmi(height, weight)
    self.bmi_result_row.set_result(result)
    context_thresholds = widgets.Thresholds()
    for threshold in self.bmi_result_row.thresholds:
      value = calculate.mass_from_bmi_and_height(threshold.value, height)
      if self.height_input_row.imperial:
        value = widgets.kg_to_lb(value)
      value = round(value, 1)
      context_thresholds.append(
        widgets.Threshold(threshold.name, value, threshold.style)
      )
    self.bmi_result_row.set_context_thresholds(context_thresholds)

  def update_bri(self):
    height = self.height_input_row.get_centimetres()
    waist = self.waist_input_row.get_centimetres()
    result = calculate.bri(height, waist)
    self.bri_result_row.set_result(result)

  def update_whr(self):
    waist = self.waist_input_row.get_centimetres()
    hip = self.hip_input_row.get_centimetres()
    result = calculate.whr(waist, hip)
    self.whr_result_row.set_result(result)

  def update_whtr(self):
    height = self.height_input_row.get_centimetres()
    waist = self.waist_input_row.get_centimetres()
    result = calculate.whtr(waist, height)
    self.whtr_result_row.set_result(result)

  def update_whr_thresholds(self):
    gender = self.gender_input_row.get_value()
    self.whr_result_row.set_thresholds(widgets.Thresholds(
      (_("Healthy"),    0,                                'success'),
      (_("Overweight"), calculate.whr_overweight(gender), 'warning'),
      (_("Obese"),      calculate.whr_obese(gender),      'error'),
    ))

  def update_whtr_thresholds(self):
    age = self.age_input_row.get_value()
    self.whtr_result_row.set_thresholds(widgets.Thresholds(
      (_("Healthy"),   0,                             'success'),
      (_("Unhealthy"), calculate.whtr_unhealthy(age), 'warning'),
    ))

  def copy_result(self, row: widgets.ResultRow):
    clipboard = Gdk.Display.get_default().get_clipboard()
    clipboard.set(row.result_label)
    self.show_toast(_("Result copied"))

  def show_toast(self, text: str):
    self.toast_overlay.dismiss_all()
    toast = Adw.Toast(title=text, timeout=1)
    self.toast_overlay.add_toast(toast)

  def _on_settings_value_changed(self, settings: Gio.Settings, key: str):
    handlers = {
      'advanced-mode': self._on_advanced_mode_changed,
      'measurement-system': self._on_measurement_system_changed,
      'remember-inputs': self._on_remember_inputs_changed,
    }
    handler = handlers.get(key)
    if handler:
      handler()

  def _on_advanced_mode_changed(self):
    mode = self.settings['advanced-mode']
    self.advanced_inputs_clamp.set_visible(mode)
    self.whtr_result_row.set_visible(mode)
    self.whr_result_row.set_visible(mode)
    self.bri_result_row.set_visible(mode)
    self.update_breakpoints()

  def _on_measurement_system_changed(self):
    imperial = bool(self.settings['measurement-system'])
    for row in [
      self.height_input_row,
      self.weight_input_row,
      self.waist_input_row,
      self.hip_input_row,
    ]:
      row.set_imperial(imperial)
    self._on_remember_inputs_changed()

  def _on_remember_inputs_changed(self):
    if self.settings['remember-inputs']:
      return
    self.reset_remembered_inputs()
    if not self.settings['measurement-system']:
      return
    for key in ['height', 'waist', 'hip']:
      self.settings[key] = round(cm_to_in(self.settings[key]))
    self.settings['mass'] = round(kg_to_lb(self.settings['mass']))

  def reset_remembered_inputs(self):
    for key in ['height', 'mass', 'gender', 'age', 'waist', 'hip']:
      self.settings.reset(key)

  def _eval_breakpoint(self, adw_breakpoint):
    width = self.get_size(Gtk.Orientation.HORIZONTAL)
    height = self.get_size(Gtk.Orientation.VERTICAL)
    condition = adw_breakpoint.get_condition().to_string()
    condition = condition.replace('min-width:', 'width >')
    condition = condition.replace('max-width:', 'width <')
    condition = condition.replace('min-height:', 'height >')
    condition = condition.replace('max-height:', 'height <')
    condition = condition.split('and')
    for statement in condition:
      combined = re.search('([0-9]).*', statement).group().strip()
      units = combined[-2] + combined[-1] # Last 2 chars (i.e. px, sp or pt)
      value = float(combined.removesuffix(units))
      adw_lenght_units = {u.name.lower(): u for u in Adw.LengthUnit}
      units = adw_lenght_units[units]
      pixels = math.ceil( Adw.LengthUnit.to_px(units, value) )
      statement = statement.replace(combined, str(pixels))
      if not eval(statement):
        return False
    return True

  def _on_simple_breakpoint_apply(self, adw_breakpoint = None):
    if self.settings['advanced-mode']:
      return
    self.set_ui_orientation(Gtk.Orientation.HORIZONTAL)

  def _on_simple_breakpoint_unapply(self, adw_breakpoint = None):
    if self.settings['advanced-mode']:
      return
    self.set_ui_orientation(Gtk.Orientation.VERTICAL)

  def _on_advanced_breakpoint_apply(self, adw_breakpoint = None):
    self.set_ui_orientation(Gtk.Orientation.HORIZONTAL)

  def _on_advanced_breakpoint_unapply(self, adw_breakpoint = None):
    self.set_ui_orientation(Gtk.Orientation.VERTICAL)

  def set_ui_orientation(self, orientation: Gtk.Orientation):
    self.orientable_box.set_orientation(orientation)
    if orientation is Gtk.Orientation.HORIZONTAL:
      self.orientable_box.set_spacing(24);
    else:
      self.orientable_box.set_spacing(16);

  def update_breakpoints(self):
    if self._eval_breakpoint(self.advanced_breakpoint):
      self._on_advanced_breakpoint_apply()
    else:
      self._on_advanced_breakpoint_unapply()
    if self._eval_breakpoint(self.simple_breakpoint):
      self._on_simple_breakpoint_apply()
    else:
      self._on_simple_breakpoint_unapply()

  def _on_close_request(self, *args):
    """Action after closing the app window."""
    width = self.get_size(Gtk.Orientation.HORIZONTAL)
    height = self.get_size(Gtk.Orientation.VERTICAL)
    self.settings['window-size'] = (width, height)
