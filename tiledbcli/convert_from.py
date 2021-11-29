import tiledb

import collections
import click
import pprint as pp


@click.group()
def convert_from():
    """
    Convert to and from TileDB arrays and other common file formats.
    """
    pass


class FilterList(click.ParamType):
    """
    Support passing in TileDB's FilterList types to tiledb.from_csv().

    The input syntax is identical to how all other kwargs arguments are parsed.
    However, additional parsing and conversion is done here to ensure that the
    given Filters are valid, the window or compression value is passed to the
    Filter as necessary, and the resulting argument is casted to a FilterList type.
    """

    name = "filter_list"

    def convert(self, value, param, ctx):
        raw_filters = str(value).split(";")

        if len(raw_filters) == 1:
            return self._parse_filter_list(value, param, ctx)
        else:
            filters = dict()
            for f in raw_filters:
                if ":" not in f:
                    self.fail(
                        f"An attribute:FilterList mapping must be provided if using ; syntax.",
                        param,
                        ctx,
                    )
                filters.update(self._parse_filter_list(f, param, ctx))
            return filters

    def _parse_filter_list(self, value, param, ctx):
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
        "(e.g. --attr-filters LZ4Filter=10,BitShuffleFilter). Map an attribute with "
        "a given list of filters with a colon separated by a semicolon "
        "(e.g. --attr-filters attr1:LZ4Filter=10,BitShuffleFilter;"
        "attr2:DoubleDeltaFilter,PositiveDeltaFilter=3. Some filters "
        "take in a compression level or window size that can be assigned using the "
        "= operator as shown in the examples above."
    ),
    type=FilterList(),
)
@click.option(
    "--coords-filters",
    metavar="<filter[=opt]>,,...",
    help=(
        "Provide a comma separated list of filters to apply to each coordinate "
        "(e.g. --coords-filters LZ4Filter=10,BitShuffleFilter). "
        "Some filters take in a compression level or window size that can be "
        "assigned using the = operator as shown in the example above."
    ),
    type=FilterList(),
)
@click.option(
    "--dim-filters",
    metavar="<filter[=opt]>,... | <dim>:<filter[=opt]>;...",
    help=(
        "Provide a comma separated list of filters to apply to each dimension "
        "(e.g. --dim-filters LZ4Filter=10,BitShuffleFilter). Map a dimension with "
        "a given list of filters with a colon separated by a semicolon "
        "(e.g. --dim-filters dim1:LZ4Filter=10,BitShuffleFilter;"
        "dim2:DoubleDeltaFilter,PositiveDeltaFilter=3. Some filters "
        "take in a compression level or window size that can be assigned using the "
        "= operator as shown in the examples above."
    ),
    type=FilterList(),
)
@click.pass_context
def csv(ctx, csv_file, uri, attr_filters, coords_filters, dim_filters):
    """
    Convert a csv_file into a TileDB array located at uri.

    How To Pass Keyword Options
    ---------------------------

    Any keyword supported by TileDB's from_csv() or Panda's
    read_csv() functions that are not listed under the "Options" section of
    this help documentation below can be passed to this CLI command using the
    method described below.

    A keyword uses two dashes at the beginning and contains an argument that is
    separated by a single space. Any underscores in the keyword may be replaced
    with dashes. For example, passing the flags --allows-duplicates True and
    --allows_duplicates True are both valid calls to pass
    tiledb.from_csv(allows_duplicates=True).

    For primitive argument types, int types are any valid Python <int> and <bool>
    types are True or False. All other types will be considered <str>.

    --int 2
    --bool True
    --str helloworld

    To force <str> type, enclose the argument in double quotes.

    --int-is-str "2"
    --bool_is_str "False"

    Pass in lists using comma separated values.

    --list-abc a,b,c
    --list_123 1,2,3
    --list-bool True,True,False
    --list_mix False,"1",2

    Pass in dictionaries where each entry is separated by semicolons. Each entry
    is a key and value pairing separated by a colon.

    --dict-int hello:1
    --dict-strs hello:world;"1":"2"
    --dict-bools good:True;bye:False
    --dict_mix bool:False;str:"1";int:2;3:"three";list:hey,"hi",True,1

    An actual example using

        tiledb convert-from csv s3://tiledb-unittest/inputs/increment_sparse1.csv example_array_convert_from_csv.tdb --sparse True --mode ingest --timestamp 1

        tiledb dump array example_array_convert_from_csv.tdb --timestamp 1
        > {'a': array([21, 31, 41, 51, 61]),
        > 'b': array([22, 32, 42, 52, 62]),
        > 'c': array([23, 33, 43, 53, 63]),
        > 'x': array([2, 3, 4, 5, 6])}

    For more examples and usage of the kwargs syntax, please see view
    the TestCSV() unit tests located in tests/test_convert_from.py.


    (An Attempt at) Backus-Naur Form
    ---------------------------------

    "kwargs" are made up of one or more "kwarg" options. Multiple "kwarg" options
    are separated by a single space.

        kwargs ::= kwarg | kwarg kwargs

    A "kwarg" is made up of a "kw" and arg. The "kw" contains two dashes in front
    and is separated by the "arg" using a single space.

        kwarg ::= --kw arg

    "kw" is most* keywords supported by TileDB's from_csv() or Panda's
    read_csv() functions. Dashes may be used in lieu of underscores, but both
    are valid. For example, --allows-duplicates and --allows_duplicates both
    correctly refer to the same keyword argument.

    "kw" currently does NOT include attr_filters, coords_filters, and dim_filters.
    These require special parsing that cannot be generally handled using
    this function and are handled through Click though they still generally use the
    same syntax as described below. More keywords may need special parsing in the
    future.

    "arg" may be of type "argval", "list", or "dict".

        arg ::= argval | list | dict

    "argval" is of Python type <int>, <bool>, or <str>.

        argval ::= <int> | <bool> | <str>

    "list" is at least two "argval" symbols separated by a comma without
    any spaces.

        list ::= argval,argval | argval,list

    "dict" contains one or more "dictentry" symbols. Multiple "dictentry"
    symbols are separated by a semicolon with no spaces.

        dict ::=  dictentry | dictentry;dict

    "dictentry" is made up of a "dictkey" and "dictval" separated by a colon.

        dictentry ::= dictkey:dictval

    "dictkey" is an "argval" that is a Python hashtable type.

        dictkey ::= <str> | <int>

    "dictval" is an "argval" or "list".

        dictval ::= argval | list
    """
    kwargs = parse_kwargs(ctx.args)

    # there are options that require special parsing that cannot be generally
    # handled using the parse_kwargs() function above.
    if attr_filters:
        kwargs["attr_filters"] = attr_filters

    if coords_filters:
        kwargs["coords_filters"] = coords_filters

    if dim_filters:
        kwargs["dim_filters"] = dim_filters

    tiledb.from_csv(uri, csv_file, **kwargs)


def parse_kwargs(args):
    """
    Parse the given raw string of args into the kwargs dictionary. Details of the
    syntax can be found under the documentation for csv().

    :param args: A string containing all kwargs options and values to be parsed.
    :return: A dictionary containing the given kwargs options and values.
    """
    argslist = []

    argsiter = iter(args)
    for arg in argsiter:
        lhs, rhs = arg, next(argsiter)

        if lhs[:2] == "--":
            opt = lhs[2:].replace("-", "_")
        else:
            raise click.UsageError(f"Saw ill-formed option {arg}.")

        for values in rhs.split(";"):
            k, sep, v = values.partition(":")
            argslist.append((opt, (k, v) if v else k))

    kwargs = collections.defaultdict(list)
    for k, v in argslist:
        v = (
            (cast_kwargs(v[0], castbool=False), cast_kwargs(v[1]))
            if isinstance(v, tuple)
            else cast_kwargs(v)
        )
        kwargs[k].append(v)

    for k, v in kwargs.items():
        if len(v) > 0 and isinstance(v[0], tuple):
            kwargs[k] = dict(v)
        elif len(v) == 1:
            kwargs[k] = v[0]

    return kwargs


def cast_kwargs(token, castbool=True):
    """
    Cast the token to the appropriate type. Tokens may be of type list, int,
    Boolean, or string.

    Tokens that begin and end with double quotes are strings. Given that the
    token is not a string, tokens containing commas will be separated out into a
    list of tokens. Numberic tokens will be casted to ints and True and False
    are casted to Boolean values. Note that "123" and "False" are examples of
    strings because they are enclosed in double quotes. ""Hello"" is a string
    that represents the string \"Hello\" in quotes. Even if a token is not
    enclosed in double-quotes, if is definitely not a list, number, or Boolean
    type, then it is ultimately casted as a string.

    :param v: The token to cast.
    :param castbool: By default, castbool=True, casts token=True or token=False
                     to Boolean type. Otherwise, castbool=False casts to string
                     type.

    :return: The casted token of type list, int, Boolean, or string.
    """
    bool = {"True": True, "False": False}
    if "," in token and not isstring(token):
        token = [cast_kwargs(t, castbool=castbool) for t in token.split(",")]
    elif token.isnumeric():
        token = int(token)
    elif castbool and token in bool:
        token = bool[token]
    elif isstring(token):
        token = token[1:-1]

    return token


def isstring(token):
    """
    Determine if the token is a string.

    :param token: The token.

    :return: Boolean representing whether the token is a string.
    """
    return token[0] == '"' and token[-1] == '"'


convert_from.add_command(csv)
