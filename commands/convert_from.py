import tiledb

import click


@click.group()
def convert_from():
    pass


class FilterList(click.ParamType):
    name = "filter_list"

    def convert(self, value, param, ctx):
        values = str(value).split(":")

        if len(values) == 1:
            return self.parse_filters(values[0], param, ctx)
        elif len(values) == 2:
            return (values[0], self.parse_filters(values[1], param, ctx))
        else:
            self.fail(f"Too many arguments provided", param, ctx)

    def parse_filters(self, filter_and_options, param, ctx):
        filter_name_to_function = {
            "GzipFilter": tiledb.GzipFilter,
            "ZstdFilter": tiledb.ZstdFilter,
            "LZ4Filter": tiledb.LZ4Filter,
            "Bzip2Filter": tiledb.Bzip2Filter,
            "RleFilter": tiledb.RleFilter,
            "DoubleDeltaFilter": tiledb.DoubleDeltaFilter,
            "BitShuffleFilter": tiledb.BitShuffleFilter,
            "ByteShuffleFilter": tiledb.ByteShuffleFilter,
            "BitWidthReductionFilter": tiledb.BitWidthReductionFilter,
            "PositiveDeltaFilter": tiledb.PositiveDeltaFilter,
        }

        provided_filter_and_options = dict()
        for value in filter_and_options.split(","):
            filter_and_option = value.split("=")

            filter = filter_and_option[0]
            if len(filter_and_option) == 1:
                provided_filter_and_options[filter] = None
            elif len(filter_and_option) == 2:
                try:
                    provided_filter_and_options[filter] = int(filter_and_option[1])
                except ValueError:
                    self.fail(
                        f"{filter_and_option[1]} is not a valid integer "
                        f"for {provided_filter_and_options[filter]}",
                        param,
                        ctx,
                    )
            else:
                self.fail(
                    "Too many arguments provided for "
                    f"{provided_filter_and_options[filter]}",
                    param,
                    ctx,
                )

        bad_filters = set(provided_filter_and_options.keys()) - set(
            filter_name_to_function.keys()
        )
        if bad_filters:
            self.fail(
                f"Saw the following bad <filter names>: {bad_filters}",
                param,
                ctx,
            )

        filter_list = []
        for filter_name in provided_filter_and_options:
            filter_function = filter_name_to_function[filter_name]
            filter_option = provided_filter_and_options[filter_name]
            if filter_option is None:
                filter_list.append(filter_function())
            else:
                filter_list.append(filter_function(filter_option))

        return tiledb.FilterList(filter_list)


@click.command(
    name="csv",
    context_settings=dict(ignore_unknown_options=True, allow_extra_args=True),
)
@click.argument("csv_file")
@click.argument("uri")
@click.option(
    "--attr-filters",
    metavar="<filter name>,<filter name>,... | <attr name>:<filter name>,<filter name>,...",
    help=(
        "Provide a comma separated list of filters to apply to each attribute. "
        "Alternatively, assign filters to each attribute by passing the flag "
        "multiple times (e.g. '-A attr_x:5 -A attr_y:8'). Unspecified dimensions "
        "will use default."
    ),
    multiple=True,
    type=FilterList(),
    default=(),
)
@click.option(
    "--coords-filters",
    metavar="<filter name>,<filter name>,...",
    help=("Provide a comma separated list of filters to apply to each coordinate. "),
    type=FilterList(),
)
@click.option(
    "--dim-filters",
    metavar="<filter name>,<filter name>,... | <attr name>:<filter name>,<filter name>,...",
    help=(
        "Provide a comma separated list of filters to apply to each dimension. "
        "Alternatively, assign filters to each dimension by passing the flag "
        "multiple times (e.g. '-D attr_x:5 -D attr_y:8'). Unspecified dimensions "
        "will use default."
    ),
    multiple=True,
    type=FilterList(),
    default=(),
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
@click.pass_context
def csv(ctx, csv_file, uri, attr_filters, coords_filters, dim_filters, date_spec):
    """
    Convert a csv_file into a TileDB array located at uri.
    """

    kwargs = dict()

    bool = {"True": True, "False": False}

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
        kwargs["attr_filters"] = attr_filters

    if coords_filters:
        kwargs["coords_filters"] = coords_filters

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
        kwargs["dim_filters"] = dim_filters

    if date_spec:
        kwargs["date_spec"] = dict(date_spec)

    for arg in ctx.args:
        dashedoption, sep, rhs = arg.partition("=")

        if dashedoption[:2] == "--":
            opt = dashedoption[2:]
        else:
            raise click.UsageError(f"Saw ill-formed option {arg}.")

        opt = opt.replace("-", "_")
        rhsvalues = rhs.split(",")
        kwargsval = dict()
        for rhsval in rhsvalues:
            dictkey, sep, dictval = rhsval.partition(":")

            # TODO clean this
            if not dictval:
                if dictkey.isnumeric():
                    kwargs[opt] = int(dictkey)
                elif dictkey in bool:
                    kwargs[opt] = bool[dictkey]
                else:
                    kwargs[opt] = str(dictkey)
            else:
                if dictval.isnumeric():
                    kwargsval[dictkey] = int(dictval)
                elif dictval in bool:
                    kwargsval[dictkey] = bool[dictval]
                else:
                    kwargsval[dictkey] = str(dictval)
                kwargs[opt] = kwargsval

    tiledb.from_csv(
        uri,
        csv_file,
        **kwargs,
    )


convert_from.add_command(csv)
