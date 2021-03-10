"""
Demoing Rez application plugin subcommand
"""
from __future__ import print_function
from rez.application import Application


command_behavior = {
    "hidden": False,   # optional: bool
    "arg_mode": None,  # optional: None, "passthrough", "grouped"
}


def setup_parser(parser, completions=False):
    parser.add_argument("--version", action="store_true",
                        help="Print out version of 'foo'")
    parser.add_argument("-m", "--message", action="store_true",
                        help="Print out message from config")


def command(opts, parser=None, extra_arg_groups=None):
    from foo._version import version
    import foo

    if opts.version:
        print(version)
        return

    if opts.message:
        foo.say()


class ApplicationFoo(Application):
    schema_dict = {}

    @classmethod
    def name(cls):
        return "foo"


def register_plugin():
    return ApplicationFoo
