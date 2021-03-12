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
        build_py.build_py.run(self)
        self.patch_rez_binaries()

    def _append(self, data_files):
        """Append `data_files` into `distribution.data_files`

        Just like how additional files be assigned with setup(data_files=[..]),
        but for those extra files that can only be created in build time, here
        is the second chance.

        The `data_files` specifies a sequence of (directory, files) pairs in
        the following way:

            setup(...,
                data_files=[('config', ['foo/cfg/data.cfg'])],
            )

        Each (directory, files) pair in the sequence specifies the installation
        directory and the files to install there.

        So in the example above, the file `data.cfg` will be installed to
        `config/data.cfg`.

        IMPORTANT:
        The directory MUST be a relative path. It is interpreted relative to
        the installation prefix (Python’s sys.prefix for system installations;
        site.USER_BASE for user installations).

        @param data_files: a sequence of (directory, files) pairs
        @return:
        """
        # will be picked up by `distutils.command.install_data`
        if self.distribution.data_files is None:
            self.distribution.data_files = data_files
        else:
            self.distribution.data_files += data_files

    def patch_rez_binaries(self):
        from rez.vendor.distlib.scripts import ScriptMaker

        self.announce("Generating rez bin tools...", level=3)

        # Create additional build dir for binaries, so they won't be handled
        # as regular builds under "build/lib".
        build_path = os.path.join("build", "rez_b")
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

        self._append([(rel_rez_dir, rel_rez_bin_paths)])


setup(
    cmdclass={
        "build_py": BuildPyWithRezBinsPatch,
    },
    **setup_args
)
