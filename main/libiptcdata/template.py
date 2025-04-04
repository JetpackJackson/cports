pkgname = "libiptcdata"
pkgver = "1.0.4"
pkgrel = 0
build_style = "gnu_configure"
# fails to regen
configure_gen = []
hostmakedepends = ["pkgconf"]
pkgdesc = "Library for manipulating the IPTC metadata"
license = "LGPL-2.1-or-later"
url = "http://libiptcdata.sourceforge.net"
source = f"$(SOURCEFORGE_SITE)/libiptcdata/libiptcdata-{pkgver}.tar.gz"
sha256 = "79f63b8ce71ee45cefd34efbb66e39a22101443f4060809b8fc29c5eebdcee0e"


@subpackage("libiptcdata-devel")
def _(self):
    return self.default_devel(extra=["usr/share/gtk-doc"])
