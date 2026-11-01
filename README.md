# BMI
Calculator for body health metrics. Built with GTK4 and LibAdwaita.

<img width='640' src='screenshots/advanced-dark.png'/>

## Installation
Available as a [Flatpak](https://flatpak.org)
on [Flathub](https://flathub.org/apps/details/io.github.philippkosarev.bmi)
and via [Github Releases](https://github.com/philippkosarev/bmi/releases).

<a href='https://flathub.org/apps/details/io.github.philippkosarev.bmi'>
  <img
    width='176'
    alt='Download on Flathub'
    src='https://flathub.org/api/badge?locale=en'
  />
</a>

## Development
### Dependencies
You will need these dependencies to build and run the app:
- [Python 3](https://www.python.org)
- [PyGObject](https://pypi.org/project/PyGObject)
- [Meson](https://mesonbuild.com)
- [blueprint-compiler](https://gnome.pages.gitlab.gnome.org/blueprint-compiler)
- [flatpak-builder](https://docs.flatpak.org/en/latest/flatpak-builder.html)

### Running
Use the project's runner script:
```sh
./run native # Native build
./run flatpak # Flatpak build
```
