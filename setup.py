from __future__ import print_function, with_statement

import os.path
import sys


try:
    from setuptools import setup, find_packages, Distribution
    from setuptools.command import install_scripts
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
    from pip._vendor.distlib.util import get_export_entry

    python_script_template = r'''# -*- coding: utf-8 -*-
import re
import os
import sys
if "REZ_PRODUCTION_PATH" in os.environ:
    sys.path.append(os.environ["REZ_PRODUCTION_PATH"])
from %(module)s import %(import_name)s
if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(%(func)s())
'''
    shell_script_template = r"""@echo off
set /p _rez_python=< %%~dp0.rez_production_install
%%_rez_python:~2%% -E %%~dp0%(name)s.py
"""
    scripts = []
    for spec in get_specifications().values():
        entry = get_export_entry(spec)
        shell_script = os.path.join(target_dir, entry.name) + ".cmd"
        python_script = os.path.join(target_dir, entry.name) + ".py"

        with open(python_script, "w") as s:
            s.write(python_script_template % dict(
                module=entry.prefix,
                import_name=entry.suffix.split('.')[0],
                func=entry.suffix
            ))
        with open(shell_script, "w") as s:
            s.write(shell_script_template % dict(name=entry.name))
        scripts += [python_script, shell_script]

    validation_file = os.path.join(target_dir, ".rez_production_install")
    with open(validation_file, "w") as vfn:
        vfn.write("#!python\n")
        vfn.write("_rez_version")
    scripts.append(validation_file)

    return scripts


class install_rez_script(install_scripts.install_scripts):
    # TODO: change to get this class form rez
    def initialize_options(self):
        install_scripts.install_scripts.initialize_options(self)
        self.no_rez_bin = False

    def finalize_options(self):
        install_scripts.install_scripts.finalize_options(self)
        self.set_undefined_options('install', ('no_rez_bin', 'no_rez_bin'))

    def run(self):
        install_scripts.install_scripts.run(self)
        self.patch_rez_binaries()

    def patch_rez_binaries(self):
        if self.no_rez_bin:
            return
        build_path = os.path.join(self.build_dir, "rez")
        install_path = os.path.join(self.install_dir, "rez")
        self.mkpath(build_path)
        patch_production_scripts(build_path)
        self.outfiles += self.copy_tree(build_path, install_path)


with open(os.path.join(source_path, "README.md")) as f:
    long_description = f.read()


setup(
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
    cmdclass={
        "install_scripts": install_rez_script,
    },
    # install_requires=[
    #     "rez>=2.78.0",  # on development
    # ],
)
