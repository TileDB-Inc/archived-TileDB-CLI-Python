import tiledb

import click


@click.group()
def convert_from():
    pass


class FilterList(click.ParamType):
    name = "filter_list"

    def convert(self, value, param, ctx):
        filter_name_to_function = {
            "GzipFilter": tiledb.GzipFilter(),
            "ZstdFilter": tiledb.ZstdFilter(),
            "LZ4Filter": tiledb.LZ4Filter(),
            "Bzip2Filter": tiledb.Bzip2Filter(),
            "RleFilter": tiledb.RleFilter(),
            "DoubleDeltaFilter": tiledb.DoubleDeltaFilter(),
            "BitShuffleFilter": tiledb.BitShuffleFilter(),
            "ByteShuffleFilter": tiledb.ByteShuffleFilter(),
            "BitWidthReductionFilter": tiledb.BitWidthReductionFilter(),
            "PositiveDeltaFilter": tiledb.PositiveDeltaFilter(),
        }

        values = str(value).split(":")

        if len(values) == 1:
            provided_filters = values[0].split(",")
            bad_filters = set(provided_filters) - set(filter_name_to_function.keys())
            if bad_filters:
                self.fail(
                    f"Saw the following bad <filter names>: {bad_filters}",
                    param,
                    ctx,
                )
            return tiledb.FilterList(
                [
                    filter_name_to_function[filter_name]
                    for filter_name in provided_filters
                ]
            )
        elif len(values) == 2:
            provided_filters = values[1].split(",")
            bad_filters = set(provided_filters) - set(filter_name_to_function.keys())
            if bad_filters:
                self.fail(
                    f"Saw the following bad <filter names>: {bad_filters}",
                    param,
                    ctx,
                )
            return (
                values[0],
                tiledb.FilterList(
                    [
                        filter_name_to_function[filter_name]
                        for filter_name in provided_filters
                    ]
                ),
            )
        else:
            self.fail(f"Too many arguments provided", param, ctx)


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
    "--cell-order",
    "-c",
    metavar="(row-major | column-major | global)",
    help=("Specify the cell ordering. By default, row-major"),
    type=click.Choice(["row-major", "column-major", "global"], case_sensitive=True),
    default="row-major",
)
@click.option(
    "--tile-order",
    "-t",
    metavar="ingest | schema_only | append",
    help=("Specify the tile ordering. By default, row-major"),
    type=click.Choice(["row-major", "column-major", "global"], case_sensitive=True),
    default="row-major",
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
    "--full-domain/--limited-domain",
    help=(
        "Specify whether dimensions should be created with full range of the dtype. "
        "By default, the limited-domain ranges from the min and max values of "
        "the ingested CSV file"
    ),
    default=False,
)
@click.option(
    "--attr-filters",
    "-A",
    metavar="<filter name>,<filter name>,... | <attr name>:<filter name>,<filter name>,...",
    help=(
        "Provide a comma separated list of filters to apply to each attribute. "
        "Alternatively, assign filters to each attribute by passing the flag "
        "multiple times (e.g. '-t attr_x:5 -t attr_y:8'). Unspecified dimensions "
        "will use default."
    ),
    multiple=True,
    type=FilterList(),
    default=(),
)
@click.option(
    "--dim-filters",
    "-D",
    metavar="<filter name>,<filter name>,... | <attr name>:<filter name>,<filter name>,...",
    help=(
        "Provide a comma separated list of filters to apply to each dimension. "
        "Alternatively, assign filters to each dimension by passing the flag "
        "multiple times (e.g. '-t attr_x:5 -t attr_y:8'). Unspecified dimensions "
        "will use default."
    ),
    multiple=True,
    type=FilterList(),
    default=(),
)
@click.option(
    "--coords-filters",
    "-C",
    metavar="<filter name>,<filter name>,...",
    help=("Provide a comma separated list of filters to apply to each coordinate. "),
    type=FilterList(),
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
    "-T",
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
    "--capacity",
    "-n",
    metavar="<int>",
    help=("Schema capacity. By default, 0, which uses the libtiledb internal default"),
    type=int,
    default=0,
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
@click.option(
    "--row-start-idx",
    "-r",
    metavar="<int>",
    help=("Start index to start new write (for row-indexed ingestions). By default, 0"),
    type=int,
    default=0,
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
def csv(
    csv_file,
    uri,
    # tiledb keyword args
    allows_duplicates,
    cell_order,
    tile_order,
    mode,
    full_domain,
    attr_filters,
    dim_filters,
    coords_filters,
    sparse,
    tile,
    capacity,
    timestamp,
    row_start_idx,
    date_spec,
    # pandas keyword args
):
    """
    Convert a csv_file into a TileDB array located at uri.

    Available <filter name> options: GzipFilter, ZstdFilter, LZ4Filter, Bzip2Filter, RleFilter, DoubleDeltaFilter, BitShuffleFilter, ByteShuffleFilter, BitWidthReductionFilter, PositiveDeltaFilter
    """
    if tile:
        if len(tile) == 1:
            tile = tile[0]
        elif len(tile) > 1:
            if any(isinstance(t, int) for t in tile):
                raise click.BadOptionUsage(
                    "The --tile/-t flag can only be used once if using an <int> argument. "
                    "Multiple uses of the flag require <column name>:<int> arguments."
                )
            tile = dict(tile)

    if attr_filters:
        if len(attr_filters) == 1:
            attr_filters = attr_filters[0]
        elif len(attr_filters) > 1:
            if any(isinstance(t, tiledb.FilterList) for t in attr_filters):
                raise click.BadOptionUsage(
                    "The --attr_filters/-A flag can only be used once if using only "
                    "<filter list> argument. Multiple uses of the flag require "
                    "<attr name>:<filter list> arguments."
                )
            attr_filters = dict(attr_filters)

    if dim_filters:
        if len(dim_filters) == 1:
            dim_filters = dim_filters[0]
        elif len(dim_filters) > 1:
            if any(isinstance(t, tiledb.FilterList) for t in dim_filters):
                raise click.BadOptionUsage(
                    "The --dim_filters/-D flag can only be used once if using only "
                    "<filter list> argument. Multiple uses of the flag require "
                    "<attr name>:<filter list> arguments."
                )
            dim_filters = dict(dim_filters)

    tiledb.from_csv(
        uri,
        csv_file,
        # tiledb keyword args
        allows_duplicates=allows_duplicates,
        cell_order=cell_order,
        tile_order=tile_order,
        mode=mode,
        full_domain=full_domain,
        attr_filters=attr_filters if attr_filters else None,
        dim_filters=dim_filters if dim_filters else None,
        coords_filters=coords_filters if coords_filters else None,
        sparse=sparse,
        tile=tile if tile else None,
        capacity=capacity,
        timestamp=timestamp,
        row_start_idx=row_start_idx,
        date_spec=dict(date_spec) if date_spec else None,
    )


convert_from.add_command(csv)
