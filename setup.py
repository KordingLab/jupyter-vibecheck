#!/usr/bin/env python3

import os
import io
from setuptools import find_packages, setup

VERSION = "0.0.4"

here = os.path.abspath(os.path.dirname(__file__))
with io.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = "\n" + f.read()

setup(
    name="vibecheck",
    version=VERSION,
    author="Jordan Matelsky",
    author_email="opensource@matelsky.com",
    description=(
        "vibecheck is a Python library for getting hyperlocal feedback from notebook users."
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="Apache 2.0",
    keywords=["datatops", "serverless", "jupyter", "notebook"],
    url="https://github.com/KordingLab/vibecheck/tarball/" + VERSION,
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    classifiers=[],
    install_requires=[
        "datatops",
        "ipython",
        "ipywidgets",
    ],
)
