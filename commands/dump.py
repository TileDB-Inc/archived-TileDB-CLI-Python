from numpy.lib.function_base import i0
import tiledb

import click
import pprint
import re
import sys


@click.group()
def dump():
    """
    Output information about TileDB arrays.
    """
    pass


@click.command()
def config():
    """
    Output TileDB's default configuration parameters and values.
    """
    click.echo(tiledb.Config())


@click.command()
@click.argument("uri")
def metadata(uri):
    """
    Output the metadata of a TileDB array located at uri.
    """
    with tiledb.open(uri) as array:
        pp = pprint.PrettyPrinter()
        click.echo(pp.pformat(array.meta.items()))


@click.command()
@click.argument("uri")
def nonempty_domain(uri):
    """
    Output the non-empty domain of a TileDB array located at uri.
    """
    with tiledb.open(uri) as array:
        pp = pprint.PrettyPrinter()
        click.echo(pp.pformat(array.nonempty_domain()))


@click.command()
@click.argument("uri")
def schema(uri):
    """
    Output the schema of a TileDB array located at uri.
    """
    with tiledb.open(uri) as array:
        click.echo(array.schema)


@click.command()
@click.argument("uri")
@click.argument("selection", nargs=-1)
@click.option(
    "--attribute",
    "-A",
    metavar="<str>",
    help=(
        "Output data from given attribute. Multiple attributes may be provided "
        "by passing the flag multiple times e.g. '-A attr1 -A attr2'. "
        "By default, all attributes are selected"
    ),
    multiple=True,
    default=[],
)
@click.option(
    "--dimension",
    "-d",
    metavar="<str>",
    help=(
        "Output data from given dimension. Multiple dimensions may be provided "
        "by passing the flag multiple times e.g. '-d dim1 -d dim2'. "
        "By default, all dimensions are selected"
    ),
    multiple=True,
    default=[],
)
@click.option(
    "--timestamp",
    "-t",
    metavar="<unix seconds>",
    help=("Output data from the array at the given TileDB timestamp."),
    type=int,
    default=None,
)
def array(uri, selection, attribute, dimension, timestamp):
    """
    Output the data of a TileDB array located at uri with a given selection.
    The selection is given per dimension and is a scalar or slice that matches
    the type of the underlying dimension.

    For datetime dimensions, select by enclose the datetime string in quotes.
    e.g. tiledb dump array uri_to_array '5-3-2020 12:00':"5-3-2021"

    Example:
        tiledb dump schema tiledb://TileDB-Inc/quickstart_sparse
        #
        # This array has two dimensions - rows and cols.
        #
        # ArraySchema(
        # domain=Domain(*[
        #     Dim(name='rows', domain=(1, 4), tile='4', dtype='int32'),
        #     Dim(name='cols', domain=(1, 4), tile='4', dtype='int32'),
        # ]),
        # ...

        tiledb dump array tiledb://TileDB-Inc/quickstart_sparse 2 3:4
        #
        # Read row 2 and columns 3 thru 4.
        #    rows  cols  a
        # 0     2     3  3
        # 1     2     4  2

        tiledb dump array tiledb://TileDB-Inc/quickstart_sparse 2 -d rows
        #
        # Select only "rows" dimension. Read row 2.
        #    rows  a
        # 0     2  3
        # 1     2  2
    """
    import numpy as np

    with tiledb.open(uri, timestamp=timestamp) as array:
        pp = pprint.PrettyPrinter()

        attrs = None if attribute == () else attribute
        sels = list(selection)
        dims = (
            [array.domain.dim(i).name for i in range(array.domain.ndim)]
            if dimension == ()
            else dimension
        )

        if len(dims) != len(sels):
            click.echo(
                f"Error: The number of selections ({len(sels)}) needs to match "
                f"the number of dimensions ({len(dims)})",
                err=True,
            )
            sys.exit(1)

        for i, dim in enumerate(dims):
            dt = np.dtype(array.domain.dim(dim).dtype)
            if np.issubdtype(dt, np.datetime64):
                quoted = re.compile("'[^']*'|\"[^\"]*\"")
                sel = [p[1:-1] if p else None for p in quoted.findall(sels[i])]
                if len(sel) == 0:
                    click.echo(
                        "Error: could not parse the selection for the datetime"
                        f"dimension '{dim}'. (Did you enclose the selection in "
                        "quotes?)",
                        err=True,
                    )
                sel = np.array(sel, dtype=dt)
                sels[i] = slice(*sel) if len(sel) > 1 else sel[0]
            else:
                sel = [p if p else None for p in sels[i].split(":")]
                sel = np.array(sel, dtype=dt)
                sels[i] = slice(*sel) if ":" in sels[i] else sel[0]

        query = array.query(attrs=attrs, dims=dims, use_arrow=False)
        subarray = query[tuple(sels)]
        click.echo(pp.pformat(subarray))


@click.command()
@click.argument("uri")
@click.option(
    "--index",
    "-i",
    metavar="<int>",
    help=(
        "Output data from the given fragment number. Zero indexing is used. "
        "By default, info from all fragments are shown"
    ),
    type=int,
    default=None,
)
@click.option("--number", "-n", help=("Output the number of fragments"), is_flag=True)
def fragments(uri, index, number):
    """
    Output the fragment information of a TileDB array located at uri.
    """
    pp = pprint.PrettyPrinter()

    fragments = tiledb.array_fragments(uri)

    if number:
        click.echo(len(fragments))
        exit()

    if index is not None:
        fragments = fragments[index]

    click.echo(pp.pformat(fragments))


dump.add_command(array)
dump.add_command(config)
dump.add_command(metadata)
dump.add_command(nonempty_domain)
dump.add_command(schema)
dump.add_command(fragments)
