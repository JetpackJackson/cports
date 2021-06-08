from cbuild.core import logger, template, paths, xbps
from cbuild.step import build as do_build
from cbuild import cpu
from os import makedirs

_tcache = {}

def _srcpkg_ver(pkgn):
    global _tcache

    # avoid a failure
    if not (paths.templates() / pkgn / "template.py").is_file():
        return None

    if pkgn in _tcache:
        return _tcache[pkgn]

    rv = template.read_pkg(pkgn, False, False, False, None)
    _tcache[pkgn] = rv

    return rv.version + "_" + str(rv.revision)

def _setup_depends(pkg):
    hdeps = []
    tdeps = []
    rdeps = []

    crdeps = list(pkg.depends)

    # also account for subpackages
    for sp in pkg.subpkg_list:
        crdeps += sp.depends

    for dep in crdeps:
        pd = xbps.get_pkg_dep_name(dep)
        if not pd:
            pd = xpbs.get_pkg_name(dep)
        if not pd:
            rdeps.append(dep + ">=0")
        else:
            rdeps.append(dep)

    for dep in pkg.hostmakedepends:
        sver = _srcpkg_ver(dep)
        if not sver:
            hdeps.append(dep)
            continue
        hdeps.append(dep + "-" + sver)

    for dep in pkg.makedepends:
        sver = _srcpkg_ver(dep)
        if not sver:
            hdeps.append(dep)
            continue
        tdeps.append(dep + "-" + sver)

    return hdeps, tdeps, rdeps

def _install_from_repo(pkg, pkglist):
    success, sout, serr = xbps.install(pkglist, capture_out = True)
    if not success:
        outl = sout.strip().decode("ascii")
        if len(outl) > 0:
            pkg.logger.out_plain(">> stdout:")
            pkg.logger.out_plain(outl)
        outl = serr.decode("ascii")
        if len(outl) > 0:
            pkg.logger.out_plain(">> stderr:")
            pkg.logger.out_plain(outl)
        pkg.error(f"failed to install dependencies")

def _is_installed(pkgn):
    pn = xbps.get_pkg_dep_name(pkgn)
    if not pn:
        pn = xbps.get_pkg_name(pkgn)

    if not pn:
        return None

    return xbps.get_installed_version(pn) != None

def install(pkg, origpkg, step, depmap):
    style = ""
    if pkg.build_style:
        style = f" [{pkg.build_style}]"

    if pkg.pkgname != origpkg:
        pkg.log(f"building{style} (dependency of {origpkg}) for {cpu.target()}...")
    else:
        pkg.log(f"building{style} for {cpu.target()}...")

    host_binpkg_deps = []
    binpkg_deps = []
    host_missing_deps = []
    missing_deps = []
    missing_rdeps = []

    log = logger.get()

    ihdeps, itdeps, irdeps = _setup_depends(pkg)

    if len(ihdeps) == 0 and len(itdeps) == 0 and len(irdeps) == 0:
        return

    for dep in ihdeps:
        pkgn = xbps.get_pkg_name(dep)
        # maybe no template
        if not pkgn:
            rurl = xbps.repository_url(dep)
            if rurl:
                log.out_plain(f"   [host] {dep}: found ({rurl})")
                host_binpkg_deps.append(dep)
                continue
            log.out_plain(f"   [host] {dep}: unresolved build dependency")
            pkg.error(f"host dependency '{dep}' does not exist")
        # got a template
        inst = _is_installed(dep)
        if inst:
            log.out_plain(f"   [host] {dep}: installed")
            continue
        # unresolved
        if inst == None:
            log.out_plain(f"   [host] {dep}: unresolved build dependency")
            pkg.error(f"host dependency '{dep}' does not exist")
        # not installed
        rurl = xbps.repository_url(dep)
        if rurl:
            log.out_plain(f"   [host] {dep}: found ({rurl})")
            host_binpkg_deps.append(dep)
            continue
        # not found
        log.out_plain(f"   [host] {dep}: not found")
        # check for loops
        if pkgn == origpkg or pkgn == pkg.pkgname:
            pkg.error(f"[host] build loop detected: {pkgn} <-> {origpkg}")
        # consider missing
        host_missing_deps.append(dep)

    for dep in itdeps:
        pkgn = xbps.get_pkg_name(dep)
        # maybe no template
        if not pkgn:
            rurl = xbps.repository_url(dep)
            if rurl:
                log.out_plain(f"   [target] {dep}: found ({rurl})")
                binpkg_deps.append(dep)
                continue
            log.out_plain(f"   [target] {dep}: unresolved build dependency")
            pkg.error(f"target dependency '{dep}' does not exist")
        # got a template, first ensure it's not a subpackage
        is_subpkg = False
        for sp in pkg.subpkg_list:
            if sp.pkgname == pkgn:
                is_subpkg = True
                break
        if is_subpkg:
            continue
        # not a subpackage, so match normally like above
        inst = _is_installed(dep)
        if inst:
            log.out_plain(f"   [target] {dep}: installed")
            continue
        # unresolved
        if inst == None:
            log.out_plain(f"   [target] {dep}: unresolved build dependency")
            pkg.error(f"target dependency '{dep}' does not exist")
        # not installed
        rurl = xbps.repository_url(dep)
        if rurl:
            log.out_plain(f"   [target] {dep}: found ({rurl})")
            binpkg_deps.append(dep)
            continue
        # not found
        log.out_plain(f"   [target] {dep}: not found")
        # check for loops
        if pkgn == origpkg or pkgn == pkg.pkgname:
            pkg.error(f"[target] build loop detected: {pkgn} <-> {pkgn}")
        # consider missing
        missing_deps.append(dep)

    for dep in irdeps:
        pkgn = xbps.get_pkg_dep_name(dep)
        # sanitize
        if not pkgn:
            pkgn = xbps.get_pkg_name(dep)
            if not pkgn:
                pkg.error(f"invalid runtime dependency: {dep}")
        # first ensure it's not a subpackage
        is_subpkg = False
        for sp in pkg.subpkg_list:
            if sp.pkgname == pkgn:
                is_subpkg = True
                break
        if is_subpkg:
            continue
        # not a subpackage
        props = xbps.repository_properties(pkgn, ["pkgver", "repository"])
        if props and xbps.pkg_match(props[0], dep):
            log.out_plain(f"   [target] {dep}: found ({props[1]})")
            continue
        # not found
        log.out_plain(f"   [runtime] {dep}: not found")
        # check for loops
        if pkgn == origpkg or pkgn == pkg.pkgname:
            pkg.error(f"[runtime] build loop detected: {pkgn} <-> {pkgn}")
        # consider missing
        missing_rdeps.append(dep)

    for hd in host_missing_deps:
        pn = xbps.get_pkg_name(hd)
        try:
            build.build(step, template.read_pkg(
                pn, pkg.force_mode, pkg.bootstrapping, True, pkg
            ), depmap)
        except template.SkipPackage:
            pass
        host_binpkg_deps.append(hd)

    for td in missing_deps:
        pn = xbps.get_pkg_name(td)
        try:
            build.build(step, template.read_pkg(
                pn, pkg.force_mode, pkg.bootstrapping, True, pkg
            ), depmap)
        except template.SkipPackage:
            pass
        host_binpkg_deps.append(td)

    for rd in missing_rdeps:
        pn = xbps.get_pkg_name(rd)
        try:
            build.build(step, template.read_pkg(
                pn, pkg.force_mode, pkg.bootstrapping, True, pkg
            ), depmap)
        except template.SkipPackage:
            pass
        host_binpkg_deps.append(rd)

    if len(host_binpkg_deps) > 0:
        pkg.log(f"installing host dependencies: {', '.join(host_binpkg_deps)}")
        _install_from_repo(pkg, host_binpkg_deps)

    if len(binpkg_deps) > 0:
        pkg.log(f"installing target dependencies: {', '.join(binpkg_deps)}")
        _install_from_repo(pkg, binpkg_deps)
