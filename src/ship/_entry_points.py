
import sys


def get_specifications():
    specs = {}
    for attr, obj in sys.modules[__name__].__dict__.items():
        script = getattr(obj, "__scriptname__", None)
        if script:
            spec = "%s = %s:%s" % (script, __name__, attr)
            specs[script] = spec
    return specs


def scriptname(name):
    def decorator(fn):
        setattr(fn, "__scriptname__", name)
        return fn
    return decorator


# Entry points

@scriptname("rez-ship")
def run_rez_ship():
    from rez.cli._main import run
    return run("ship")
