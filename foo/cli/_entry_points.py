"""
Entry points.
"""
import os
import sys


### Utility functions

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
            spec = "%s = foo.cli._entry_points:%s" % (scriptname, attr)
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


def patch_subcommands(name, behavior=None):
    from rez.cli._util import subcommands
    if name not in subcommands:
        subcommands[name] = behavior or {}


### Entry points

@scriptname("rez")
def run_rez():
    check_production_install()
    patch_subcommands("foo")
    from rez.cli._main import run
    return run()


@scriptname("rez-foo")
def run_rez_foo():
    check_production_install()
    patch_subcommands("foo")
    from rez.cli._main import run
    return run("foo")
