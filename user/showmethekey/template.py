pkgname = "showmethekey"
pkgver = "1.18.1"
pkgrel = 0
build_style = "meson"
hostmakedepends = [
    "gettext-devel",
    "gtk+3-update-icon-cache",
    "meson",
    "pkgconf",
]
makedepends = [
    "cairo-devel",
    "glib-devel",
    "gtk4-devel",
    "json-glib-devel",
    "libadwaita-devel",
    "libevdev-devel",
    "libinput-devel",
    "libxkbcommon-devel",
    "pango-devel",
    "udev-devel",
]
pkgdesc = "Show keys you typed on screen"
license = "Apache-2.0"
url = "https://github.com/AlynxZhou/showmethekey"
source = f"{url}/archive/refs/tags/v{pkgver}.tar.gz"
sha256 = "e457d9cd9dc267983681022f95c04b2518d92588ce356ac815c67021f5819237"
