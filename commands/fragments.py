import tiledb

import click


@click.group()
def fragments():
    """
    Perform various tasks on TileDB array fragments. For more information, see

        https://docs.tiledb.com/main/concepts/terminology#fragment
    """


@click.command("copy")
@click.argument("uri-src")
@click.argument("uri-dst")
@click.argument("time-start", type=int)
@click.argument("time-end", type=int)
@click.option(
    "--verbose",
    "-v",
    help=("Output the fragment file names as they are copied"),
    is_flag=True,
    default=False,
)
@click.option(
    "--dry-run",
    "-n",
    help=("Perform a trial run with no changes made"),
    is_flag=True,
    default=False,
)
def fragments_copy(uri_src, uri_dst, time_start, time_end, verbose, dry_run):
    """
    (POSIX only). Copy a range of fragments from time-start to time-end (inclusive)
    in an array located at uri-src to create a new array at uri-dst. The range is
    a UNIX timestamp.
    """
    tiledb.create_array_from_fragments(
        uri_src,
        uri_dst,
        timestamp_range=(time_start, time_end),
        verbose=verbose,
        dry_run=dry_run,
    )


@click.command("delete")
@click.argument("uri")
@click.argument("time-start", type=int)
@click.argument("time-end", type=int)
@click.option(
    "--verbose",
    "-v",
    help=("Output the fragment file names as they are deleted"),
    is_flag=True,
    default=False,
)
@click.option(
    "--dry-run",
    "-n",
    help=("Perform a trial run with no changes made"),
    is_flag=True,
    default=False,
)
def fragments_delete(uri, time_start, time_end, verbose, dry_run):
    """
    Delete a range of fragments from time-start to time-end (inclusive) in an
    array located at uri. The range is a UNIX timestamp.
    """
    tiledb.delete_fragments(
        uri,
        timestamp_range=(time_start, time_end),
        verbose=verbose,
        dry_run=dry_run,
    )


fragments.add_command(fragments_delete)
fragments.add_command(fragments_copy)
