from __future__ import print_function, with_statement

import os.path
import sys


try:
    from setuptools import setup, find_packages
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

from cli_patch._install import get_specifications


setup(
    name="ship",
    version="0.1.0",
    description="Custom Rez cli tools",
    long_description=None,
    author="davidlatwe",
    author_email="davidlatwe@gmail.com",
    license="LGPL",
    entry_points={
        "console_scripts": get_specifications().values()
    },
    include_package_data=True,
    zip_safe=False,
    package_dir={"": "src"},
    packages=find_packages("src"),
)

# patch rez bin
