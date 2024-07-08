pkgname = "base-desktop"
pkgver = "0.1"
pkgrel = 2
build_style = "meta"
depends = ["base-full"]
pkgdesc = "Chimera default desktop session (deprecated transitional package)"
maintainer = "q66 <q66@chimera-linux.org>"
license = "custom:meta"
url = "https://chimera-linux.org"


@subpackage("base-desktop-gnome")
def _gnome(self):
    self.pkgdesc = f"{pkgdesc} (GNOME)"
    self.install_if = [f"{pkgname}={pkgver}-r{pkgrel}"]
    self.depends = [
        f"{pkgname}={pkgver}-r{pkgrel}",
        "gnome",
    ]
    return []
