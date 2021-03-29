import os
from setuptools import setup


# Directory containing this file
CONTAINING_DIR = os.path.abspath(os.path.dirname(__file__))

# TileDB-CLI command source directory
TILEDB_PKG_DIR = os.path.join(CONTAINING_DIR, "commands")

with open("README.md") as f:
    README_MD = f.read()

setup(
    name="tiledb-cli",
    description="CLI to the TileDB array storage manager",
    long_description=README_MD,
    long_description_content_type="text/markdown",
    author="TileDB, Inc.",
    author_email="help@tiledb.io",
    maintainer="TileDB, Inc.",
    maintainer_email="help@tiledb.io",
    url="https://github.com/TileDB-Inc/TileDB-CLI",
    py_modules=["commands.root"],
    packages=["commands"],
    install_requires=[
        "click==7.1.2",
        "numpy>=1.16.*",
        "setuptools",
        "tiledb>=0.8.5",
    ],
    extras_require={
        "dev": [
            "black",
            "cmake >= 3.13",
            "cython",
            "pybind11",
            "wheel",
            "setuptools-scm",
            "dask",
            "pandas ; python_version > '3.5'",
            "pyarrow",
            "pytest",
        ]
    },
    license="MIT",
    use_scm_version={
        "version_scheme": "guess-next-dev",
        "local_scheme": "dirty-tag",
        "write_to": "./version.py",
    },
    entry_points="""
        [console_scripts]
        tiledb=commands.root:root
    """,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Operating System :: Unix",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
