#!/usr/bin/env python

from setuptools import setup, find_packages


from cgod.version import version


setup(
    name="cgod",
    version=version,
    description="circuits Gopher Daemon",
    long_description=open("README.rst", "r").read(),
    author="James Mills",
    author_email="James Mills, prologic at shortcircuit dot net dot au",
    url="https://bitbucket.org/prologic/cgod",
    download_url="http://bitbucket.org/prologic/cgod/downloads/",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: POSIX :: BSD",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Internet",
    ],
    license="MIT",
    keywords="gopher daemon server",
    platforms="POSIX",
    packages=find_packages("."),
    install_requires=[
        "funcy",
        "bidict",
        "cidict",
        "pathlib",
        "pymills",
        "procname",
        "circuits",
        "python-magic",
    ],
    entry_points={
        "console_scripts": [
            "cgod=cgod.main:main"
        ]
    },
    zip_safe=True
)
