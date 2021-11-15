import tiledb

import click


@click.group()
def consolidate():
    """
    Consolidate TileDB array fragments. For more information, see

        https://docs.tiledb.com/main/solutions/tiledb-embedded/internal-mechanics/consolidation
    """


@click.group()
def vacuum():
    """
    Vacuum TileDB array fragments that have already been consolidated. For more information, see

        https://docs.tiledb.com/main/solutions/tiledb-embedded/internal-mechanics/consolidation#vacuuming
    """
    pass


@click.command("fragments")
@click.argument("uri")
@click.option(
    "--amplification",
    "-a",
    metavar="<int>",
    help=(
        "Applicable to the case where the fragment subset to be consolidated "
        "contains at least one dense fragment. Sets the amplification factor "
        "which is the ratio between the consolidated fragment size and the sum "
        "of sizes of the original fragments. The default value 1.0 means that "
        "the fragments will be consolidated if there is no amplification at all"
    ),
    default=1.0,
    show_default=True,
)
@click.option(
    "--buffer-size",
    "-b",
    metavar="<int>",
    help=("Set the buffer size used when consolidating"),
    default=50000000,
    show_default=True,
)
@click.option(
    "--step-max-frags",
    "--max",
    metavar="<int>",
    help=("Set the maximum number of fragments to consolidate in each step"),
    default=4294967295,
    show_default=True,
)
@click.option(
    "--step-min-frags",
    "--min",
    metavar="<int>",
    help=("Set the minimum number of fragments to consolidate in each step"),
    default=4294967295,
    show_default=True,
)
@click.option(
    "--step-size-ratio",
    "-r",
    metavar="<int>",
    help=(
        "Set the comparative fragment size. Ideally, we must consolidate "
        "fragments of approximately equal size. Otherwise, we may end up in a "
        "situation where, for example, a 100GB fragment gets consolidated with "
        "a 1MB one, which would unnecessarily waste consolidation time. "
        "If the size ratio of two adjacent fragments is larger than this "
        "parameter, then no fragment subset that contains those two fragments "
        "will be considered for consolidation."
    ),
    default=0.0,
    show_default=True,
)
@click.option(
    "--steps",
    "-s",
    metavar="<int>",
    help=(
        "The consolidation algorithm is performed in steps. In each step, a "
        "subset of adjacent (in the timeline) fragments is selected for "
        "consolidation. The algorithm proceeds until a determined number of "
        "steps were executed, or until the algorithm specifies that no further "
        "fragments are to be consolidated"
    ),
    default=4294967295,
    show_default=True,
)
@click.option(
    "--vacuum",
    "-v",
    help=("Vacuum the fragments after consolidating"),
    is_flag=True,
)
def consolidate_fragments(
    uri,
    amplification,
    buffer_size,
    step_max_frags,
    step_min_frags,
    step_size_ratio,
    steps,
    vacuum,
):
    """
    Consolidate the fragments in an array located at uri.
    """
    config = tiledb.Config()
    config["sm.consolidation.mode"] = "fragments"
    config["sm.consolidation.amplification"] = amplification
    config["sm.consolidation.buffer_size"] = buffer_size
    config["sm.consolidation.step_max_frags"] = step_max_frags
    config["sm.consolidation.step_min_frags"] = step_min_frags
    config["sm.consolidation.step_size_ratio"] = step_size_ratio
    config["sm.consolidation.steps"] = steps
    ctx = tiledb.Ctx(config)

    tiledb.consolidate(uri, ctx=ctx)

    print(vacuum)
    if vacuum:
        config = tiledb.Config({"sm.vacuum.mode": "fragments"})
        tiledb.vacuum(uri, ctx=tiledb.Ctx(config))
        print("here?")


@click.command("fragment-metadata")
@click.argument("uri")
@click.option(
    "--vacuum",
    "-v",
    help=("Vacuum the fragment metadata after consolidating"),
    is_flag=True,
)
def consolidate_fragment_metadata(uri, vacuum):
    """
    Consolidate the fragment metadata in an array located at uri.
    """
    config = tiledb.Config()
    config["sm.consolidation.mode"] = "fragment_meta"
    ctx = tiledb.Ctx(config)

    tiledb.consolidate(uri, ctx=ctx)

    if vacuum:
        config = tiledb.Config({"sm.vacuum.mode": "fragment_meta"})
        tiledb.vacuum(uri, ctx=tiledb.Ctx(config))


@click.command("array-metadata")
@click.argument("uri")
@click.option(
    "--vacuum",
    "-v",
    help=("Vacuum the array metadata after consolidating"),
    is_flag=True,
)
def consolidate_array_metadata(uri, vacuum):
    """
    Consolidate the array metadata in an array located at uri.
    """
    config = tiledb.Config()
    config["sm.consolidation.mode"] = "array_meta"
    ctx = tiledb.Ctx(config)

    tiledb.consolidate(uri, ctx=ctx)

    if vacuum:
        config = tiledb.Config({"sm.vacuum.mode": "array_meta"})
        tiledb.vacuum(uri, ctx=tiledb.Ctx(config))


@click.command("fragments")
@click.argument("uri")
def vacuum_fragments(uri):
    """
    Vacuum the already consolidated fragments in an array located at uri.
    """
    config = tiledb.Config({"sm.vacuum.mode": "fragments"})
    tiledb.vacuum(uri, ctx=tiledb.Ctx(config))


@click.command("fragment-metadata")
@click.argument("uri")
def vacuum_fragment_metadata(uri):
    """
    Vacuum the already consolidated fragment metadata in an array located at uri.
    """
    config = tiledb.Config({"sm.vacuum.mode": "fragment_meta"})
    tiledb.vacuum(uri, ctx=tiledb.Ctx(config))


@click.command("array-metadata")
@click.argument("uri")
def vacuum_array_metadata(uri):
    """
    Vacuum the already consolidated array metadata in an array located at uri.
    """
    config = tiledb.Config({"sm.vacuum.mode": "array_meta"})
    tiledb.vacuum(uri, ctx=tiledb.Ctx(config))


consolidate.add_command(consolidate_fragments)
consolidate.add_command(consolidate_fragment_metadata)
consolidate.add_command(consolidate_array_metadata)
vacuum.add_command(vacuum_fragments)
vacuum.add_command(vacuum_fragment_metadata)
vacuum.add_command(vacuum_array_metadata)
