
import os
import sys
import venv
import stat
import shutil
import functools
import subprocess


REZ_URL = "https://github.com/MoonShineVFX/rez.git"
REZ_SRC = "build/rezsrc"

venv_pip_packages = [
    # pip package name here...
    ".",  # foo
]


def install_rez(dst):
    git_clone(REZ_URL, REZ_SRC)
    src_path = REZ_SRC + "/src"

    rez_version = subprocess.check_output([
        sys.executable, "-c",
        "from rez.utils._version import _rez_version;print(_rez_version)"
    ], universal_newlines=True, cwd=src_path).strip()

    dst = functools.reduce(
        lambda path, f: f(path),
        [dst,
         os.path.expanduser,
         os.path.expandvars,
         os.path.normpath]
    ).format(version=rez_version)

    # if os.path.isdir(dst):
    #     clean(dst)
    # os.makedirs(dst)
    #
    # subprocess.check_call([sys.executable, "install.py", "-v", dst],
    #                       cwd=REZ_SRC)

    install_pip_packages(dst)

    sys.path.insert(0, src_path)  # rez api required
    install_kitz(dst)


def install_pip_packages(dst):
    if not venv_pip_packages:
        return

    py_executable = os.path.join(get_virtualenv_bin_dir(dst),
                                 os.path.basename(sys.executable))
    subprocess.check_call([
        py_executable, "-m", "pip", "install"] + venv_pip_packages)


def install_kitz(dst):
    from rez.vendor.distlib.scripts import ScriptMaker
    from foo.cli._entry_points import get_specifications

    venv_bin_dir = get_virtualenv_bin_dir(dst)
    dest_bin_path = os.path.join(venv_bin_dir, "rez")
    py_executable = os.path.join(venv_bin_dir, os.path.basename(sys.executable))

    specs = get_specifications()

    # copy foo.cli into rez.cli (except '_' prefixed .py)
    subprocess.check_call([py_executable, "-m", "foo.cli._install"])

    # make bin scripts

    maker = ScriptMaker(
        # note: no filenames are referenced in any specifications, so
        # source_dir is unused
        source_dir=None,
        target_dir=dest_bin_path
    )

    maker.executable = py_executable

    maker.make_multiple(
        specifications=specs.values(),
        # the -E arg is crucial - it means rez cli tools still work within a
        # rez-resolved env, even if PYTHONPATH or related env-vars would have
        # otherwise changed rez's behaviour
        options=dict(interpreter_args=["-E"])
    )


def get_virtualenv_bin_dir(dest_dir):
    builder = venv.EnvBuilder()
    context = builder.ensure_directories(dest_dir)
    return context.bin_path


def git_clone(url, dst, branch=None, single_branch=True):
    # https://stackoverflow.com/a/4568323/14054728

    if os.path.isdir(dst + "/.git"):
        print("git dir exists, skip clone.")
        return

    args = ["git", "clone"]

    if branch:
        args.extend(["-b", branch])

    if single_branch:
        args.append("--single-branch")

    args.extend([url, dst])

    subprocess.check_output(args)


def clean(path):
    def del_rw(action, name, exc):
        # handling read-only files, e.g. in .git
        os.chmod(name, stat.S_IWRITE)
        os.remove(name)

    shutil.rmtree(path, onerror=del_rw)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("location", nargs="?", const=True, default=None,
                        help="Rez install path if you want to install it in "
                             "custom path. If no path given, Rez will be "
                             "installed in '~/rez/core'. Directory will be "
                             "removed if exists.")
    parser.add_argument("--yes", action="store_true",
                        help="Yes to all.")

    opt = parser.parse_args()

    location = opt.location or "~/rez/core/{version}"

    print("Rez will be installed to %s" % location)
    print("Directory will be removed if exists.")
    # if opt.yes or lib.confirm("Do you want to continue ? [Y/n]\n"):
    #     install_rez(location)
    # else:
    #     print("Cancelled")

    install_rez(location)
