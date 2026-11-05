pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / 'bmi'
gnome = import('gnome')

blueprints = custom_target(
  'blueprints',
  input: files(
    # Main
    'window.blp',
    'preferences.blp',
    # Widgets
    'widgets/result_dialog.blp',
  ),
  output: '.',
  command: [find_program('blueprint-compiler'), 'batch-compile', '@OUTPUT@', '@CURRENT_SOURCE_DIR@', '@INPUT@'],
)

gnome.compile_resources('bmi',
  'bmi.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
  dependencies: blueprints,
)

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').full_path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', get_option('prefix') / get_option('localedir'))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'bmi.in',
  output: 'bmi',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'r-xr-xr-x'
)

configure_file(
  input: 'data.py.in',
  output: 'data.py',
  configuration: conf,
  install: true,
  install_dir: moduledir,
)

bmi_sources = [
  '__init__.py',
  'main.py',
  'window.py',
  'preferences.py',
  'calc.py',
]

install_data(bmi_sources, install_dir: moduledir)

subdir('widgets')
