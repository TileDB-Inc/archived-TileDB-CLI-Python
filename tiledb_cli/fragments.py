import tiledb
from .utils import to_unix_time, prompt_poweruser

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
@click.argument("time-start")
@click.argument("time-end")
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
@click.option(
    "--force",
    "-f",
    help=("Bypass the poweruser warning"),
    is_flag=True,
    default=False,
)
def fragments_copy(uri_src, uri_dst, time_start, time_end, verbose, dry_run, force):
    """
    (POSIX only). Copy a range of fragments from time-start to time-end (inclusive)
    in an array located at uri-src to an array at uri-dst. If the array does not
    exist, it will be created. The range may be formatted in UNIX seconds or ISO 8601.
    """
    if not force:
        prompt_poweruser()

    if time_start:
        time_start = to_unix_time(time_start)

    if time_end:
        time_end = to_unix_time(time_end)

    copy_fragments_to_array = (
        tiledb.copy_fragments_to_existing_array
        if tiledb.array_exists(uri_dst)
        else tiledb.create_array_from_fragments
    )

    copy_fragments_to_array(
        uri_src,
        uri_dst,
        timestamp_range=(time_start, time_end),
        verbose=verbose,
        dry_run=dry_run,
    )


@click.command("delete")
@click.argument("uri")
@click.argument("time-start")
@click.argument("time-end")
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
@click.option(
    "--force",
    "-f",
    help=("Bypass the poweruser warning"),
    is_flag=True,
    default=False,
)
def fragments_delete(uri, time_start, time_end, verbose, dry_run, force):
    """
    Delete a range of fragments from time-start to time-end (inclusive) in an
    array located at uri. The range is a UNIX timestamp.
    """
    if not force:
        prompt_poweruser()

    if time_start:
        time_start = to_unix_time(time_start)

    if time_end:
        time_end = to_unix_time(time_end)

    tiledb.delete_fragments(
        uri,
        timestamp_range=(time_start, time_end),
        verbose=verbose,
        dry_run=dry_run,
    )


fragments.add_command(fragments_delete)
fragments.add_command(fragments_copy)
