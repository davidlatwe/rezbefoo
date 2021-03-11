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


setup_args = dict(
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

    def patch_rez_binaries(self):
        from rez.vendor.distlib.scripts import ScriptMaker

        self.announce("Generating rez bin tools...", level=3)

        build_path = os.path.join("build", "rez_b")
        self.mkpath(build_path)
        # referenced from rez's install.py
        maker = ScriptMaker(
            source_dir=None,
            target_dir=build_path
        )
        maker.executable = sys.executable
        rez_bin_scripts = maker.make_multiple(
            specifications=get_specifications().values(),
            options=dict(interpreter_args=["-E"])
        )
        src_scripts = []
        for script in rez_bin_scripts:
            src_scripts.append(os.path.join(build_path, os.path.basename(script)))

        rez_bin_dir = os.path.join(os.path.dirname(sys.executable), "rez")
        relative_rez_bin_dir = os.path.relpath(rez_bin_dir, sys.prefix)

        data_files = [(relative_rez_bin_dir, src_scripts)]
        if self.distribution.data_files is None:
            self.distribution.data_files = data_files
        else:
            self.distribution.data_files += data_files

    def run(self):
        super(BuildPyWithRezBinsPatch, self).run()
        self.patch_rez_binaries()


setup(
    cmdclass={
        "build_py": BuildPyWithRezBinsPatch,
    },
    **setup_args
)
