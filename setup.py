from __future__ import print_function, with_statement

import os.path
import sys


try:
    from setuptools import setup, find_packages
    from setuptools.command import build_py
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

from rezbefoo._entry_points import get_specifications
from rezbefoo._version import version

with open(os.path.join(source_path, "README.md")) as f:
    long_description = f.read()


setup_kwargs = dict(
    name="rezbefoo",
    version=version,
    packages=find_packages("src"),
    package_dir={"": "src"},
    entry_points={"console_scripts": get_specifications().values()},
    include_package_data=True,
    zip_safe=False,
    license="LGPL",
    author="davidlatwe",
    author_email="davidlatwe@gmail.com",
    description="Demoing Rez's application plugin",
    long_description=long_description,
)


class BuildPyWithRezBinsPatch(build_py.build_py):

    def run(self):
        super(BuildPyWithRezBinsPatch, self).run()
        self.patch_rez_binaries()

    def patch_rez_binaries(self):
        from rez.vendor.distlib.scripts import ScriptMaker

        self.announce("Generating rez bin tools...", level=3)

        # Create additional build dir for binaries, so they won't be handled
        # as regular builds under "build/lib".
        build_path = os.path.join("build", "rez_bins")
        self.mkpath(build_path)

        # Make binaries, referenced from rez's install.py
        maker = ScriptMaker(
            source_dir=None,
            target_dir=build_path
        )
        maker.executable = sys.executable
        rel_rez_bin_paths = maker.make_multiple(
            specifications=get_specifications().values(),
            options=dict(interpreter_args=["-E"])
        )

        # Compute relative install path, to work with wheel.
        # Install path, e.g. "bin/rez" or "scripts/rez" on Windows.
        abs_rez_dir = os.path.join(os.path.dirname(sys.executable), "rez")
        rel_rez_dir = os.path.relpath(abs_rez_dir, sys.prefix)

        # Append information into `data_files`, they will be picked up by
        # the `distutils.command.install_data` and ship into right place.
        data_files = [
            (rel_rez_dir, rel_rez_bin_paths)
        ]
        if self.distribution.data_files is None:
            self.distribution.data_files = data_files
        else:
            self.distribution.data_files += data_files


setup(
    cmdclass={
        "build_py": BuildPyWithRezBinsPatch,
    },
    **setup_kwargs
)
