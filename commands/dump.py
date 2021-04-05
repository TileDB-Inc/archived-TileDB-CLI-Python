import tiledb

import click
import pprint


@click.group()
def dump():
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
@click.option(
    "--attribute",
    "-A",
    metavar="<str>",
    help=(
        "Output data from given attribute. Multiple attributes may be provided "
        "by passing the flag multiple times e.g. '-A attr1 -A attr2'. "
        "By default, all attributes are output"
    ),
    multiple=True,
    default=[],
)
@click.option(
    "--rows",
    "-n",
    metavar="<start int> <end int>",
    help=(
        "Output data from the range of rows beginning with <start int> and "
        "ending with <end int>. By default, '-n 1 5' which outputs the first "
        "five rows"
    ),
    nargs=2,
    type=int,
    default=(1, 5),
)
@click.option(
    "--timestamp",
    "-t",
    metavar="<unix seconds>",
    help=("Output data from the array at the given TileDB timestamp."),
    type=int,
    default=None,
)
def array(uri, attribute, rows, timestamp):
    """
    Output the data of a TileDB array located at uri.
    """
    with tiledb.open(uri, timestamp=timestamp) as array:
        pp = pprint.PrettyPrinter()

        if rows[0] <= 0 or rows[1] <= 0:
            raise click.BadOptionUsage(
                option_name="rows",
                message="The arguments to --rows/-n needs to be positive integers.",
            )

        subarray = array[rows[0] : rows[1] + 1]

        if not array.schema.sparse and not array.schema.attr(0).name:
            click.echo(pp.pformat({"": subarray}))
        else:
            if not attribute:
                attribute = [
                    array.schema.attr(n).name for n in range(array.schema.nattr)
                ]
            filtered_subarray = {
                key: value for (key, value) in subarray.items() if key in attribute
            }
            click.echo(pp.pformat(filtered_subarray))


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
