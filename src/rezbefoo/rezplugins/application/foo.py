"""
Demoing Rez application plugin subcommand
"""
from rez.application import Application
from ._helper import ensure_top_module


command_behavior = {
    "hidden": False,   # optional: bool
    "arg_mode": None,  # optional: None, "passthrough", "grouped"
}


def setup_parser(parser, completions=False):
    parser.add_argument("--version", action="store_true",
                        help="Print out version of this plugin command.")
    parser.add_argument("-m", "--message", action="store_true",
                        help="Print out message from config.")


@ensure_top_module
def command(opts, parser=None, extra_arg_groups=None):
    from rezbefoo._version import version
    from rezbefoo import lib

    if opts.version:
        print(version)
        return

    if opts.message:
        msg = lib.get_message()
        print(msg)


class ApplicationFoo(Application):
    schema_dict = {}

    @classmethod
    def name(cls):
        return "foo"


def register_plugin():
    return ApplicationFoo
