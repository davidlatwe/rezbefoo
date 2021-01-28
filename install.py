
import os
import sys
import venv
import stat
import shutil
import functools
import subprocess


REZ_URL = "https://github.com/davidlatwe/rez.git"
REZ_SRC = "build/rezsrc"

venv_pip_packages = [
    # pip package name here...
    # "pymongo",
]


def load_src():
    git_clone(REZ_URL, REZ_SRC, branch="plug-subcommand")

    # custom cli
    sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)) + "/src")
    # rez api, for querying version
    sys.path.insert(0, REZ_SRC + "/src")


def install(dst):
    load_src()
    rez_version = get_rez_version()

    dst = functools.reduce(
        lambda path, f: f(path),
        [dst,
         os.path.expanduser,
         os.path.expandvars,
         os.path.normpath]
    ).format(version=rez_version)

    install_rez(dst)

    venv_dir = get_virtualenv_bin_dir(dst)
    py_exec = os.path.join(venv_dir, os.path.basename(sys.executable))

    pip_install_packages(py_exec, venv_pip_packages)
    patch_custom_cli_tools(py_exec)


def get_rez_version():
    from rez.utils._version import _rez_version
    return _rez_version


def install_rez(dst):
    if os.path.isdir(dst):
        clean(dst)
    os.makedirs(dst)

    subprocess.check_call([sys.executable, "install.py", "-v", dst],
                          cwd=REZ_SRC)


def pip_install_packages(py_exec, names):
    if not names:
        return
    args = [
        py_exec, "-m", "pip", "install"
    ]
    subprocess.check_call(args + names, cwd=os.path.dirname(os.path.realpath(__file__)))


def patch_custom_cli_tools(py_exec):
    pip_install_packages(py_exec, [".", "-vvv"])


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

    install(location)
