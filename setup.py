from setuptools import setup

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
    url="https://github.com/TileDB-Inc/TileDB-Py",
    py_modules=["dump"],
    install_requires=[
        "Click",
        "cython>=0.27",
        "numpy==1.16.5 ; python_version < '3.9'",
        "numpy ; python_version >= '3.9'",
        "setuptools>=18.0",
        "setuptools_scm>=1.5.4",
        "wheel>=0.30",
        "pybind11>=2.6.2",
        "tiledb",
    ],
    license="MIT",
    use_scm_version={
        "version_scheme": "guess-next-dev",
        "local_scheme": "dirty-tag",
        "write_to": "./version.py",
    },
    extras_require={
        "dev": [
            "black",
            "Pytest",
            "pytest-lazy-fixture",
        ]
    },
    entry_points="""
        [console_scripts]
        tiledb=dump:tiledb_top_level_entry
    """,
)
