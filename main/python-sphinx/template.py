pkgname = "python-sphinx"
pkgver = "4.2.0"
pkgrel = 0
build_style = "python_module"
hostmakedepends = ["python-setuptools"]
checkdepends = ["python-pytest", "python-markupsafe"]
depends = [
    "python-jinja2", "python-docutils<0.18", "python-pygments",
    "python-snowballstemmer", "python-babel", "python-alabaster",
    "python-imagesize", "python-requests", "python-packaging",
    "python-sphinxcontrib-applehelp", "python-sphinxcontrib-devhelp",
    "python-sphinxcontrib-htmlhelp", "python-sphinxcontrib-jsmath",
    "python-sphinxcontrib-qthelp", "python-sphinxcontrib-serializinghtml"
]
pkgdesc = "Python documentation generator"
maintainer = "q66 <q66@chimera-linux.org>"
license = "BSD-3-Clause"
url = "http://sphinx-doc.org"
source = f"$(PYPI_SITE)/S/Sphinx/Sphinx-{pkgver}.tar.gz"
sha256 = "94078db9184491e15bce0a56d9186e0aec95f16ac20b12d00e06d4e36f1058a6"
# dependency of pytest, missing other checkdepends
options = ["!check"]

def post_install(self):
    self.install_license("LICENSE")
