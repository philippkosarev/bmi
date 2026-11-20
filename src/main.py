import sys

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import GObject, Gio, Adw

from .data import APP_ID, VERSION
from .window import BmiWindow
from .preferences import BmiPreferences


class BmiApplication(Adw.Application):

  settings = GObject.Property(type=Gio.Settings)

  def __init__(self):
    super().__init__(
      application_id=APP_ID,
      flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
      version=VERSION,
    )
    self.settings = Gio.Settings.new(self.get_application_id())
    self.create_action('preferences', self.show_preferences, ['<primary>comma'])
    self.create_action('about', self.show_about, ['F1'])
    self.create_action('quit', self.on_quit, ['<primary>q', '<primary>w'])

  def get_settings(self) -> Gio.Settings:
    return self.settings

  def set_settings(self, settings: Gio.Settings):
    self.settings = settings

  def show_preferences(self, action, param):
    """Shows the preferences dialog."""
    preferences = BmiPreferences()
    preferences.set_settings(self.get_settings())
    preferences.present(self.get_active_window())

  def show_about(self, action, param):
    """Shows the about dialog."""
    # Creating about dialog
    about_dialog = Adw.AboutDialog(
      application_name = 'BMI',
      application_icon = self.get_application_id(),
      version          = self.get_version(),
      developer_name   = 'Philipp Kosarev',
      website          = 'https://github.com/philippkosarev/bmi',
      issue_url        = 'https://github.com/philippkosarev/bmi/issues',
      developers = [
        'Philipp Kosarev https://github.com/PhilippKosarev',
        'vikdevelop https://github.com/vikdevelop',
      ],
      artists = [
        'Philipp Kosarev https://github.com/PhilippKosarev',
      ],
      translator_credits = '\n'.join([
        'David Sultaniiazov <x1z53@alt-gnome.ru>',
        'Maksym Dilanian <maksym@dilanian.xyz>',
        'Albano Battistella <albanobattistella@gmail.com>',
        'Renato Tavares <dr.renatotavares@gmail.com>',
        'Marcos Sánchez https://github.com/haggen88',
        'pcharlanes https://github.com/pcharlanes',
        'Huỳnh Thiện Lộc https://github.com/hthienloc',
        'Vincon https://github.com/Vincenderman',
      ]),
      copyright    = '© 2024 Philipp Kosarev',
      license_type = 'GTK_LICENSE_GPL_2_0',
    )
    about_dialog.present(self.get_active_window())

  def on_quit(self, action, param):
    window = self.get_active_window()
    window.close()
    self.quit()

  def do_activate(self):
    window = self.get_active_window()
    if not window:
      window = BmiWindow(self)
    window.present()

  def create_action(self, name, callback, shortcuts=None):
    action = Gio.SimpleAction.new(name, None)
    action.connect('activate', callback)
    self.add_action(action)
    if shortcuts:
      self.set_accels_for_action(f'app.{name}', shortcuts)


def main():
  app = BmiApplication()
  return app.run(sys.argv)
