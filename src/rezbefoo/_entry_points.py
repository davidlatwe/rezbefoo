
import sys


def get_specifications():
    specs = {}
    for attr, obj in sys.modules[__name__].__dict__.items():
        script = getattr(obj, "__scriptname__", None)
        if script:
            spec = "%s = %s:%s" % (script, __name__, attr)
            specs[script] = spec
    return specs


def get_first_launch_specifications():
    specs = {}
    for attr, obj in sys.modules[__name__].__dict__.items():
        script = getattr(obj, "__scriptname__", None)
        if script:
            spec = "%s = %s:%s" % (script, __name__, "on_first_launch")
            specs[script] = spec
    return specs


def scriptname(name):
    def decorator(fn):
        setattr(fn, "__scriptname__", name)
        return fn
    return decorator


def on_first_launch(path):
    import os
    from pip._vendor.distlib.scripts import ScriptMaker
    # generate script
    # call entry in subprocess
    os.remove(path)
    target_dir, entry = os.path.split(path)
    script_name = os.path.splitext(entry)[0]
    for name, specification in get_specifications().items():
        if name == script_name:
            maker = ScriptMaker(source_dir=None, target_dir=target_dir)
            # maker.script_template = SCRIPT_TEMPLATE
            maker.executable = sys.executable
            maker.make(
                specification=specification,
                options=dict(interpreter_args=["-E"])
            )
            break


# Entry points

@scriptname("rez-foo")
def run_rez_ship():
    from rez.cli._main import run
    return run("foo")
