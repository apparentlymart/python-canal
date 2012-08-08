#!/usr/bin/env python

from distutils.core import setup

setup(
    name="canal",
    version="0.1",
    description="Simple graph processing abstraction",
    author="Martin Atkins",
    author_email="mart@degeneration.co.uk",
    url="https://github.com/apparentlymart/python-canal",
    packages=["canal"],
    requires=["greenlet"],
)
