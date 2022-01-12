import tiledb
from common import test_array_names
from tiledb_cli.root import root

import itertools
import numpy as np
import os
import pytest
import shutil
import sys


@pytest.fixture(scope="function")
def uri(temp_rootdir):
    """
    Create a simple dense test array.
    """
    path = os.path.abspath(os.path.join(temp_rootdir, "test_array"))

    ctx = tiledb.default_ctx()
    rows_dim = tiledb.Dim(ctx=ctx, domain=(1, 25), dtype=np.int64)
    cols_dim = tiledb.Dim(ctx=ctx, domain=(1, 12), dtype=np.int64)
    dom = tiledb.Domain(rows_dim, cols_dim, ctx=ctx)
    att1 = tiledb.Attr(name="a", ctx=ctx, dtype=np.float64)
    att2 = tiledb.Attr(name="b", ctx=ctx, dtype=np.float64)
    schema = tiledb.ArraySchema(ctx=ctx, domain=dom, attrs=(att1, att2))

    tiledb.Array.create(path, schema)

    data = np.reshape(np.arange(300), (25, 12))

    for ts in range(1, 4):
        with tiledb.open(path, mode="w", timestamp=ts) as A:
            A[:] = {"a": data, "b": data}

    yield path

    shutil.rmtree(path)


@pytest.mark.skipif(
    sys.platform == "win32", reason="VFS.copy() does not run on windows"
)
@pytest.mark.parametrize(
    "start_time,end_time",
    [("2", "3"), ("1970-01-01T00:00:02Z", "1970-01-01T00:00:03Z")],
)
def test_copy_fragments_to_new(runner, uri, temp_rootdir, start_time, end_time):
    """
    Test for command

        tiledb fragments copy [old_array_uri] [new_array_uri] [start_time] [end_time]
    """
    old_uri = uri
    new_uri = os.path.abspath(
        os.path.join(
            temp_rootdir,
            f"test_copy_fragments_to_new_{start_time}_{end_time}",
        )
    )

    result = runner.invoke(
        root,
        ["fragments", "copy", "-f", old_uri, new_uri, start_time, end_time],
    )
    assert result.exit_code == 0

    fragments = tiledb.array_fragments(old_uri)
    assert len(fragments) == 3
    assert fragments.timestamp_range == ((1, 1), (2, 2), (3, 3))

    fragments = tiledb.array_fragments(new_uri)
    assert len(fragments) == 2
    assert fragments.timestamp_range == ((2, 2), (3, 3))


@pytest.mark.skipif(
    sys.platform == "win32", reason="VFS.copy() does not run on windows"
)
@pytest.mark.parametrize(
    "start_time,end_time",
    [("2", "3"), ("1970-01-01T00:00:02Z", "1970-01-01T00:00:03Z")],
)
def test_copy_fragments_to_existing(runner, uri, temp_rootdir, start_time, end_time):
    """
    Test for command

        tiledb fragments copy [old_array_uri] [new_array_uri] [start_time] [end_time]
    """
    old_uri = uri
    new_uri = os.path.abspath(
        os.path.join(
            temp_rootdir,
            f"test_copy_fragments_to_existing_{start_time}_{end_time}",
        )
    )

    rows_dim = tiledb.Dim(domain=(1, 25), dtype=np.int64)
    cols_dim = tiledb.Dim(domain=(1, 12), dtype=np.int64)
    dom = tiledb.Domain(rows_dim, cols_dim)
    att1 = tiledb.Attr(name="a", dtype=np.float64)
    att2 = tiledb.Attr(name="b", dtype=np.float64)
    schema = tiledb.ArraySchema(domain=dom, attrs=(att1, att2))
    tiledb.Array.create(new_uri, schema)

    data = np.reshape(np.arange(300), (25, 12))
    for ts in range(4, 6):
        with tiledb.open(new_uri, mode="w", timestamp=ts) as A:
            A[:] = {"a": data, "b": data}

    result = runner.invoke(
        root,
        ["fragments", "copy", "-f", old_uri, new_uri, start_time, end_time],
    )
    assert result.exit_code == 0

    fragments = tiledb.array_fragments(old_uri)
    assert len(fragments) == 3
    assert fragments.timestamp_range == ((1, 1), (2, 2), (3, 3))

    fragments = tiledb.array_fragments(new_uri)
    assert len(fragments) == 4
    assert fragments.timestamp_range == ((2, 2), (3, 3), (4, 4), (5, 5))


@pytest.mark.parametrize("ts", [("1"), ("1970-01-01T00:00:01Z")])
def test_delete_fragments_unix(runner, uri, ts):
    """
    Test for command

        tiledb fragments delete [array_uri] [start_time] [end_time]
    """
    fragments = tiledb.array_fragments(uri)
    assert len(fragments) == 3
    assert fragments.timestamp_range == ((1, 1), (2, 2), (3, 3))

    result = runner.invoke(root, ["fragments", "delete", "-f", uri, ts, ts])
    assert result.exit_code == 0

    fragments = tiledb.array_fragments(uri)
    assert len(fragments) == 2
    assert fragments.timestamp_range == ((2, 2), (3, 3))
