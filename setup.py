#!/usr/bin/env python3
"""
Setup script for IP-HUNTER
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ultimate-flooder",
    version="2.0.0",
    author="JonusNattapong",
    author_email="",
    description="Advanced DDoS Tool for Educational Purposes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JonusNattapong/Ultimate-Flooder",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests>=2.25.0",
        "aiohttp>=3.7.0",
        "scapy>=2.4.0",
    ],
    entry_points={
        "console_scripts": [
            "ultimate-flooder=ultimate_flooder.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)