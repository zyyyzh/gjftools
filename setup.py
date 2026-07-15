#!/usr/bin/env python

"""
The setup script.
Date: 2026-07-15
"""

from setuptools import setup, find_packages

setup(
    author="Zihao Ye",
    description="gjftools",
    name='gjftools',
    packages=find_packages(include=['gjftools']),
    package_data={'': []},
    include_package_data=True,
    version='0.1.6',
)
