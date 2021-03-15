from __future__ import print_function, with_statement

import os.path
import sys


from distutils.command import install_data
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


def patch_production_scripts(target_dir):
    from rez.vendor.distlib.scripts import ScriptMaker
    maker = ScriptMaker(source_dir=None, target_dir=target_dir)
    maker.executable = sys.executable
    scripts = maker.make_multiple(
        specifications=get_specifications().values(),
        options=dict(interpreter_args=["-E"])
    )
    return scripts


with open(os.path.join(source_path, "README.md")) as f:
    long_description = f.read()


setup_kwargs = dict(
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
    # install_requires=[
    #     "rez>=2.78.0",  # on development
    # ],
)


class RezBuildPy(build_py.build_py):

    def run(self):
        build_py.build_py.run(self)
        self.patch_rez_binaries()

    def _append(self, data_files):
        if self.distribution.data_files is None:
            self.distribution.data_files = []
        self.distribution.data_files += data_files

    def patch_rez_binaries(self):
        # Create additional build dir for binaries, so they won't be handled
        # as regular builds under "build/lib".
        build_path = os.path.join("build", "rez_bins")
        self.mkpath(build_path)
        production_scripts = patch_production_scripts(build_path)
        self._append([
            # We don't know script install dir at this moment, therefore we
            # use a placeholder and pickup later.
            ("_production_script_:rez", production_scripts)
        ])


class InstallData(install_data.install_data):

    def initialize_options(self):
        install_data.install_data.initialize_options(self)
        self.script_dir = None

    def finalize_options(self):
        install_data.install_data.finalize_options(self)
        self.set_undefined_options(
            'install', ('install_scripts', 'script_dir'),
        )

    def run(self):
        self.patch_rez_binaries()
        install_data.install_data.run(self)

    def patch_rez_binaries(self):
        data_files = []
        for dst, src in self.data_files:
            if dst.startswith("_production_script_:"):
                # Compute relative script install path
                sub_dir = dst.split(":")[-1]
                abs_dst_dir = os.path.join(self.script_dir, sub_dir)
                dst = os.path.relpath(abs_dst_dir, self.install_dir)
            data_files.append((dst, src))
        self.data_files[:] = data_files


setup(
    cmdclass={
        "build_py": RezBuildPy,
        "install_data": InstallData,
    },
    **setup_kwargs
)
