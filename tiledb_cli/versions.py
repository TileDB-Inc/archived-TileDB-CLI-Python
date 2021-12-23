import tiledb
import click


@click.group()
def versions():
    """
    Show the TileDB version information for both the Python package, and the
    embedded library.
    """


@click.command("tiledbpy")
def versions_tiledbpy():
    """
    Show the tiledb-py version
    """
    print(tiledb.version())


@click.command("embedded")
def versions_embedded():
    """
    Show the TileDB Embedded (aka "libtiledb") version
    """
    print(tiledb.libtiledb.version())


versions.add_command(versions_tiledbpy)
versions.add_command(versions_embedded)
