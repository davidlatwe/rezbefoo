from __future__ import print_function, with_statement

import os.path
import sys


try:
    from setuptools import setup, find_packages, Command
    from setuptools.command import build_py, install_data
except ImportError:
    print("install failed - requires setuptools", file=sys.stderr)
    sys.exit(1)


if sys.version_info < (2, 7):
    print("install failed - requires python v2.7 or greater", file=sys.stderr)
    sys.exit(1)


# carefully import some sourcefiles that are standalone
source_path = os.path.dirname(os.path.realpath(__file__))
src_path = os.path.join(source_path, "src")
sys.path.insert(0, src_path)

from ship._entry_points import get_specifications


class PatchRezBins(Command):
    """Just a wrapper to get the install data into the egg-info"""

    def initialize_options(self):
        self.build_dir = None
        self.outfiles = []

    def finalize_options(self):
        self.set_undefined_options('build',
                                   ('build_scripts', 'build_dir'))

    def run(self):
        rez_bin_scripts = self._patch_rez_binaries() or []
        if self.dry_run:
            return

        dest_bin_path = os.path.join(os.path.dirname(sys.executable), "rez")
        for script in rez_bin_scripts:
            dst = os.path.join(dest_bin_path, os.path.basename(script))
            self.outfiles.append(dst)
            self.copy_file(script, dst)
        # TODO: not recorded in egg

    def get_outputs(self):
        return self.outfiles

    def _patch_rez_binaries(self):
        try:
            from rez.vendor.distlib.scripts import ScriptMaker
        except Exception as e:
            print("Rez binary tool not patched: %s" % str(e))
            return

        dest_bin_path = os.path.join(self.build_dir, "rez_bins")
        self.mkpath(dest_bin_path)

        maker = ScriptMaker(
            # note: no filenames are referenced in any specifications, so
            # source_dir is unused
            source_dir=None,
            target_dir=dest_bin_path
        )
        maker.executable = sys.executable

        scripts = maker.make_multiple(
            specifications=get_specifications().values(),
            # the -E arg is crucial - it means rez cli tools still work within a
            # rez-resolved env, even if PYTHONPATH or related env-vars would have
            # otherwise changed rez's behaviour
            options=dict(interpreter_args=["-E"])
        )
        return scripts


class BuildPyCommand(build_py.build_py):
    """Custom build command."""
    def run(self):
        build_py.build_py.run(self)
        self.run_command("install_data")


setup(
    name="ship",
    version="0.1.0",
    description="Custom Rez cli tools",
    long_description=None,
    author="davidlatwe",
    author_email="davidlatwe@gmail.com",
    license="LGPL",
    cmdclass={
        "install_data": PatchRezBins,
        "build_py": BuildPyCommand,
    },
    entry_points={
        "console_scripts": get_specifications().values()
    },
    namespace_packages=["rez.cli"],
    package_dir={"": "src"},
    packages=find_packages("src"),
    package_data={"rez": ["cli/ship.json"]},
    include_package_data=True,
    zip_safe=False,
)
