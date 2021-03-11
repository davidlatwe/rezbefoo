from __future__ import print_function, with_statement

import os.path
import sys


try:
    from setuptools import setup, find_packages, find_namespace_packages
    from setuptools.command import install_lib
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

from foo._entry_points import get_specifications
from foo._version import version


setup_args = dict(
    name="foo",
    version=version,
    packages=find_packages("src"),
    package_dir={"": "src"},
    entry_points={"console_scripts": get_specifications().values()},
    package_data={"foo": []},
    include_package_data=True,
    zip_safe=False,
    license="LGPL",
    author="davidlatwe",
    author_email="davidlatwe@gmail.com",
    description="Demoing Rez's application plugin",
    long_description=None,
)


class InstallLibWithRezBinsPatch(install_lib.install_lib):

    def _patch_rez_binaries(self):
        from rez.vendor.distlib.scripts import ScriptMaker
        self.announce("Creating rez bin tools", level=3)
        temp_bin_path = os.path.join(self.build_dir, "rez_bins")
        self.mkpath(temp_bin_path)
        # referenced from rez's install.py
        maker = ScriptMaker(
            source_dir=None,
            target_dir=temp_bin_path
        )
        maker.executable = sys.executable
        return maker.make_multiple(
            specifications=get_specifications().values(),
            options=dict(interpreter_args=["-E"])
        )

    def initialize_options(self):
        super(InstallLibWithRezBinsPatch, self).initialize_options()
        self.outfiles = []

    def get_outputs(self):
        outfiles = super(InstallLibWithRezBinsPatch, self).get_outputs()
        return outfiles + self.outfiles

    def run(self):
        super(InstallLibWithRezBinsPatch, self).run()

        rez_bin_scripts = self._patch_rez_binaries() or []
        if self.dry_run:
            return

        self.announce("Patching rez bin tools", level=3)
        dest_bin_path = os.path.join(os.path.dirname(sys.executable), "rez")
        for script in rez_bin_scripts:
            dst = os.path.join(dest_bin_path, os.path.basename(script))
            self.outfiles.append(dst)
            self.copy_file(script, dst)


setup(
    cmdclass={
        "install_lib": InstallLibWithRezBinsPatch,
    },
    **setup_args
)
