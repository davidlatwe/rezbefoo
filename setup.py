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

from ship._entry_points import get_specifications


class InstallLibWithRezBinsPatch(install_lib.install_lib):
    """Just a wrapper to get the install data into the egg-info"""

    def initialize_options(self):
        super(InstallLibWithRezBinsPatch, self).initialize_options()
        self.outfiles = []

    def get_outputs(self):
        outfiles = super(InstallLibWithRezBinsPatch, self).get_outputs()
        return outfiles + self.outfiles

    def run(self):
        super(InstallLibWithRezBinsPatch, self).run()

        rez_bin_scripts = self._patch_rez_binaries() or []
        rez_cli_files = self._copy_cli_files()
        if self.dry_run:
            return

        self.announce("Patching rez bin tools", level=3)

        dest_bin_path = os.path.join(os.path.dirname(sys.executable), "rez")
        for script in rez_bin_scripts:
            dst = os.path.join(dest_bin_path, os.path.basename(script))
            self.outfiles.append(dst)
            self.copy_file(script, dst)

        self.announce("Copying rez cli files", level=3)

        for build_path, install_path in rez_cli_files:
            self.outfiles.append(install_path)
            self.copy_file(build_path, install_path)

    def _patch_rez_binaries(self):
        # referenced from rez's install.py
        from rez.vendor.distlib.scripts import ScriptMaker

        self.announce("Creating rez bin tools", level=3)

        temp_bin_path = os.path.join(self.build_dir, "rez_bins")
        self.mkpath(temp_bin_path)

        maker = ScriptMaker(
            # note: no filenames are referenced in any specifications, so
            # source_dir is unused
            source_dir=None,
            target_dir=temp_bin_path
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

    def _copy_cli_files(self):
        from rez import cli

        self.announce("Creating rez cli files transfer list", level=3)

        dest_cli_path = cli.__path__[0]

        transfer = list()
        cli_dir = os.path.join(self.build_dir, "ship", "cli")
        for file in [
            # TODO: should be a better way to not hardcoding file names
            "ship.json",
            "ship.py",
        ]:
            build_path = os.path.join(cli_dir, file)
            install_path = os.path.join(dest_cli_path, file)
            transfer.append((build_path, install_path))

        return transfer


setup(
    name="ship",
    version="0.1.0",
    description="Custom Rez cli tools",
    long_description=None,
    author="davidlatwe",
    author_email="davidlatwe@gmail.com",
    license="LGPL",
    cmdclass={
        "install_lib": InstallLibWithRezBinsPatch,
    },
    entry_points={
        "console_scripts": get_specifications().values()
    },
    packages=find_packages("src"),
    package_dir={"": "src"},
    package_data={"ship": ["cli/*.json", "cli/*.py"]},
    include_package_data=True,
    zip_safe=False,
)
