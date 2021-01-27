
import os
import sys
import shutil
from rez import cli
from rez.vendor.distlib.scripts import ScriptMaker


def install_cli():
    # copy foo.cli into rez.cli (except '_' prefixed .py)
    script_dir = os.path.dirname(__file__)
    for script in os.listdir(script_dir):
        if script.startswith("_"):
            continue
        shutil.copy2(os.path.join(script_dir, script), cli.__path__[0])


def patch_binaries():
    # make bin scripts
    py_executable = sys.executable
    dest_bin_path = os.path.join(os.path.dirname(py_executable), "rez")

    specs = get_specifications()
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


def get_specifications():
    """Get entry point specifications

    See:
    * https://pythonhosted.org/distlib/reference.html#distlib.scripts.ScriptMaker.make_multiple
    * https://setuptools.readthedocs.io/en/latest/setuptools.html#automatic-script-creation

    Example return value:

        {
            "rez-env": "rez-env = rez.cli._entry_points.run_rez_env",
            ...
        }

    Returns:
        dict (str, str): The specification string for each script name.
    """
    specs = {}

    for attr, obj in sys.modules[__name__].__dict__.items():
        scriptname = getattr(obj, "__scriptname__", None)
        if scriptname:
            spec = "%s = ship.cli_patch._install:%s" % (scriptname, attr)
            specs[scriptname] = spec

    return specs


def scriptname(name):
    def decorator(fn):
        setattr(fn, "__scriptname__", name)
        return fn
    return decorator


def check_production_install():
    path = os.path.dirname(sys.argv[0])
    filepath = os.path.join(path, ".rez_production_install")

    if not os.path.exists(filepath):
        sys.stderr.write(
            "Pip-based rez installation detected. Please be aware that rez command "
            "line tools are not guaranteed to function correctly in this case. See "
            "https://github.com/nerdvegas/rez/wiki/Installation#why-not-pip-for-production "
            " for futher details.\n"
        )


def patch_subcommands():
    from rez.cli._util import subcommands
    subcommands.update({
        "ship": {},
    })


# Entry points

# @scriptname("rez")
# def run_rez():
#     check_production_install()
#     patch_subcommands()
#     from rez.cli._main import run
#     return run()


@scriptname("rez-ship")
def run_rez_ship():
    check_production_install()
    patch_subcommands()
    from rez.cli._main import run
    return run("ship")


if __name__ == "__main__":
    install_cli()
    patch_binaries()
