import tiledb

import click
import pprint


@click.group()
def tiledb_top_level_entry():
    pass


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
def array(uri, attribute):
    """
    Output the data of a TileDB array located at uri.
    """
    with tiledb.open(uri) as array:
        pp = pprint.PrettyPrinter()
        subarray = array[:10]

        if not attribute:
            click.echo(pp.pformat(dict(subarray)))
        else:
            filtered_subarray = {
                key: value for (key, value) in subarray.items() if key in attribute
            }
            click.echo(pp.pformat(filtered_subarray))


tiledb_top_level_entry.add_command(dump)
dump.add_command(array)
dump.add_command(config)
dump.add_command(metadata)
dump.add_command(nonempty_domain)
dump.add_command(schema)
