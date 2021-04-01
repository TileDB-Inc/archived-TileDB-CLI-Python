import tiledb

import collections
import click
import pprint as pp


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
@click.pass_context
def csv(ctx, csv_file, uri, attr_filters, coords_filters, dim_filters):
    """
    Convert a csv_file into a TileDB array located at uri.
    """
    kwargs = dict()

    kwargslist = []
    args_iter = iter(ctx.args)
    for arg in args_iter:
        dashedoption = arg
        rhs = next(args_iter)

        if dashedoption[:2] == "--":
            opt = dashedoption[2:]
        else:
            raise click.UsageError(f"Saw ill-formed option {arg}.")

        opt = opt.replace("-", "_")
        rhsvalues = rhs.split(",")

        for rhsval in rhsvalues:
            k, sep, v = rhsval.partition(":")

            if v:
                kwargslist.append((opt, (k, v)))
            else:
                kwargslist.append((opt, k))

    bool = {"True": True, "False": False}
    kwargscol = collections.defaultdict(list)
    for k, v in kwargslist:
        if isinstance(v, tuple):
            if v[1].isnumeric():
                v = (v[0], int(v[1]))
            elif v[1] in bool:
                v = (v[0], bool[v[1]])
            else:
                v = (v[0], str(v[1]))
        elif v.isnumeric():
            v = int(v)
        elif v in bool:
            v = bool[v]
        else:
            v = str(v)
        kwargscol[k].append(v)

    kwargs = dict()
    for k, v in kwargscol.items():
        if len(v) > 0 and isinstance(v[0], tuple):
            kwargs[k] = dict(v)
        elif len(v) == 1:
            kwargs[k] = v[0]
        else:
            kwargs[k] = v

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

    tiledb.from_csv(uri, csv_file, **kwargs)


convert_from.add_command(csv)
