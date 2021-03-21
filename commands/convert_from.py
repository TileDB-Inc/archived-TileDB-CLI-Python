import tiledb

import click


@click.group()
def convert_from():
    pass


class OptionalInt(click.ParamType):
    name = "optional_int"

    def convert(self, value, param, ctx):
        try:
            return int(value)
        except ValueError:
            self.fail(f"{value!r} is not a valid integer", param, ctx)


class TileSpecifier(click.ParamType):
    name = "tile_specifier"

    def convert(self, value, param, ctx):
        values = str(value).split(":")
        if len(values) == 1:
            try:
                return int(values[0])
            except ValueError:
                self.fail(f"{values[0]!r} is not a valid integer", param, ctx)
        elif len(values) == 2:
            try:
                return (values[0], int(values[1]))
            except ValueError:
                self.fail(f"{values[0]!r} is not a valid integer", param, ctx)
        else:
            self.fail(f"Too many arguments provided", param, ctx)


@click.command()
@click.argument("csv_file")
@click.argument("uri")
@click.option(
    "--allows-duplicates/--no-duplicates",
    help=(
        "Generated schema should allow duplicates. "
        "By default, duplciates are allowed"
    ),
    default=True,
)
@click.option(
    "--capacity",
    "-c",
    metavar="<int>",
    help=("Schema capacity. By default, 0, which uses the libtiledb internal default"),
    type=int,
    default=0,
)
@click.option(
    "--cell-order",
    "-C",
    metavar="(row-major | column-major | global)",
    help=("Specify the cell ordering. By default, row-major"),
    type=click.Choice(["row-major", "column-major", "global"], case_sensitive=True),
    default="row-major",
)
@click.option(
    "--full-domain/--limited-domain",
    help=(
        "Specify whether dimensions should be created with full range of the dtype. "
        "By default, the limited-domain ranges from the min and max values of "
        "the ingested CSV file"
    ),
    default=False,
)
@click.option(
    "--date-spec",
    "-d",
    metavar="<column> <datetime format spec>",
    help=(
        "Apply a datetime format spec to the column. Format must be specified "
        "using the Python format codes: "
        "\n"
        "\thttps://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior"
        "\n"
        "Multiple columns may be provided by passing the flag multiple times "
        "(e.g. '-d col1 %d/%m/%y -d col2 %A %d. %B %Y')"
    ),
    multiple=True,
    nargs=2,
    type=str,
)
@click.option(
    "--mode",
    "-m",
    metavar="(ingest | schema_only | append)",
    help=("Specify the ingestion mode. By default, ingest"),
    type=click.Choice(["ingest", "schema_only", "append"], case_sensitive=True),
    default="ingest",
)
@click.option(
    "--row-start-idx",
    "-r",
    metavar="<int>",
    help=("Start index to start new write (for row-indexed ingestions). By default, 0"),
    type=int,
    default=0,
)
@click.option(
    "--sparse/--dense",
    help=(
        "Specify whether the resulting array should be sparse or dense. "
        "By default, sparse"
    ),
    default=True,
)
@click.option(
    "--tile",
    "-t",
    metavar="<int> | <column name>:<int>",
    help=(
        "Providing a single <int> will apply the tiling to each dimension. "
        "Assign tiling to a specific dimension by providing the <column name>:<int>. "
        "Alternatively, assign tilling to each dimension by passing the flag "
        "multiple times (e.g. '-t dim_x:5 -t dim_y:8')"
    ),
    multiple=True,
    type=TileSpecifier(),
    default=(),
)
@click.option(
    "--tile-order",
    "-T",
    metavar="ingest | schema_only | append",
    help=("Specify the tile ordering. By default, row-major"),
    type=click.Choice(["row-major", "column-major", "global"], case_sensitive=True),
    default="row-major",
)
@click.option(
    "--timestamp",
    "-u",
    metavar="<int>",
    help=(
        "Write TileDB array at specific UNIX timestamp. "
        "By default, the current system time"
    ),
    type=OptionalInt(),
    default=None,
)
def csv(
    csv_file,
    uri,
    # tiledb keyword args
    allows_duplicates,
    capacity,
    cell_order,
    date_spec,
    full_domain,
    mode,
    row_start_idx,
    sparse,
    tile,
    tile_order,
    timestamp,
    # pandas keyword args
):
    """
    Convert a csv_file into a TileDB array located at uri.
    """
    if tile:
        if len(tile) == 1:
            tile = tile[0]
        elif len(tile) > 1:
            if any(isinstance(t, int) for t in tile):
                raise click.BadOptionUsage(
                    "The --tile/-t flag can only be used once if using an <int> argument. "
                    "Multiple uses of the flag require <column name> <int> arguments."
                )
            tile = dict(tile)

    tiledb.from_csv(
        uri,
        csv_file,
        # tiledb keyword args
        allows_duplicates=allows_duplicates,
        capacity=capacity,
        date_spec=dict(date_spec) if date_spec else None,
        cell_order=cell_order,
        full_domain=full_domain,
        mode=mode,
        row_start_idx=row_start_idx,
        sparse=sparse,
        tile_order=tile_order,
        tile=tile if tile else None,
        timestamp=timestamp,
    )


convert_from.add_command(csv)