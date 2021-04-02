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
        raw_filters = str(value).split(";")

        if len(raw_filters) == 1:
            return self.parse_filter_list(value, param, ctx)
        else:
            filters = dict()
            for f in raw_filters:
                filters.update(self.parse_filter_list(f, param, ctx))
            return filters

    def parse_filter_list(self, value, param, ctx):
        values = str(value).split(":")
        if len(values) == 1:
            return self._parse_single_attr(values[0], param, ctx)
        elif len(values) == 2:
            return {values[0]: self._parse_single_attr(values[1], param, ctx)}
        else:
            self.fail(f"Too many arguments provided", param, ctx)

    def _parse_single_attr(self, filter_and_options, param, ctx):
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
    metavar="<filter[=opt]>,... | <attr>:<filter[=opt]>;...",
    help=(
        "Provide a comma separated list of filters to apply to each attribute "
        "(e.g. --attr-filters filter1,filter2=5,filter=3). Map an attribute with "
        "a given list of filters with a colon separated by a semicolon "
        "(e.g. --attr-filters attr1:filter1,filter2=4;attr2:filter1=0. Some filters "
        "take in a compression level or window size that can be assigned using the "
        "= operator as shown in the examples above."
    ),
    type=FilterList(),
)
@click.option(
    "--coords-filters",
    metavar="<filter[=opt]>,,...",
    help=(
        "Provide a comma separated list of filters to apply to each coordinate. "
        "Some filters take in a compression level or window size that can be assigned "
        "using the = operator."
    ),
    type=FilterList(),
)
@click.option(
    "--dim-filters",
    metavar="<filter[=opt]>,... | <dim>:<filter[=opt]>;...",
    help=(
        "Provide a comma separated list of filters to apply to each dimension "
        "(e.g. --dim-filters filter1,filter2=5,filter=3). Map a dimension with "
        "a given list of filters with a colon separated by a semicolon "
        "(e.g. --dim-filters dim1:filter1,filter2=4;dim2:filter1=0. Some filters "
        "take in a compression level or window size that can be assigned using the "
        "= operator as shown in the examples above."
    ),
    type=FilterList(),
)
@click.pass_context
def csv(ctx, csv_file, uri, attr_filters, coords_filters, dim_filters):
    """
    Convert a csv_file into a TileDB array located at uri.
    """
    kwargs = parse_kwargs(ctx)

    # there are options that require special parsing that cannot be generally
    # handled using the parse_kwargs() function above.
    if attr_filters:
        kwargs["attr_filters"] = attr_filters

    if coords_filters:
        kwargs["coords_filters"] = coords_filters

    if dim_filters:
        kwargs["dim_filters"] = dim_filters

    tiledb.from_csv(uri, csv_file, **kwargs)


def parse_kwargs(ctx):
    argslist = []

    argsiter = iter(ctx.args)
    for arg in argsiter:
        lhs, rhs = arg, next(argsiter)

        if lhs[:2] == "--":
            opt = lhs[2:].replace("-", "_")
        else:
            raise click.UsageError(f"Saw ill-formed option {arg}.")

        for values in rhs.split(","):
            k, sep, v = values.partition(":")
            argslist.append((opt, (k, v) if v else k))

    kwargs = collections.defaultdict(list)
    for k, v in argslist:
        v = (
            (v[0], cast_kwargs_value(v[1]))
            if isinstance(v, tuple)
            else cast_kwargs_value(v)
        )
        kwargs[k].append(v)

    for k, v in kwargs.items():
        if len(v) > 0 and isinstance(v[0], tuple):
            kwargs[k] = dict(v)
        elif len(v) == 1:
            kwargs[k] = v[0]

    return kwargs


def cast_kwargs_value(v):
    bool = {"True": True, "False": False}
    if v.isnumeric():
        v = int(v)
    elif v in bool:
        v = bool[v]
    return v


convert_from.add_command(csv)
