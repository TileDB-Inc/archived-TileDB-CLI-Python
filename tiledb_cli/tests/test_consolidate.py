import tiledb
from common import test_array_names
from tiledb_cli.root import root

import itertools
import numpy as np
import os
import pytest
import shutil


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

    tiledb.DenseArray.create(path, schema)

    data = np.reshape(np.arange(300), (25, 12))

    with tiledb.DenseArray(path, mode="w", timestamp=1) as A:
        A.meta["meta_int"] = 1
        A[:] = {"a": data, "b": data}

    with tiledb.DenseArray(path, mode="w", timestamp=2) as A:
        A.meta["meta_int"] = 2
        A[:] = {"a": data / 2, "b": data * 2}

    yield path

    shutil.rmtree(path)


def test_fragments_consolidate_and_vacuum(runner, uri):
    """
    Test for command

        tiledb consolidate fragments [array_uri]
        tiledb vacuum fragments [array_uri]
    """
    fragments = tiledb.array_fragments(uri)
    assert len(fragments) == 2

    result = runner.invoke(root, ["consolidate", "fragments", uri])
    assert result.exit_code == 0

    fragments = tiledb.array_fragments(uri)
    assert len(fragments) == 1
    assert len(fragments.to_vacuum) == 2

    result = runner.invoke(root, ["vacuum", "fragments", uri])
    assert result.exit_code == 0

    fragments = tiledb.array_fragments(uri)
    assert len(fragments) == 1
    assert len(fragments.to_vacuum) == 0


def test_fragment_metadata_consolidate_and_vacuum(runner, uri):
    """
    Test for command

        tiledb consolidate fragment-metadata [array_uri]
        tiledb vacuum fragment-metadata [array_uri]
    """
    fragments = tiledb.array_fragments(uri)
    assert fragments.unconsolidated_metadata_num == 2

    result = runner.invoke(root, ["consolidate", "fragment-metadata", uri])
    assert result.exit_code == 0

    fragments = tiledb.array_fragments(uri)
    assert fragments.unconsolidated_metadata_num == 0

    result = runner.invoke(root, ["vacuum", "fragment-metadata", uri])
    assert result.exit_code == 0


def test_array_metadata_consolidate_and_vacuum(runner, uri):
    """
    Test for command

        tiledb consolidate array-metadata [array_uri]
        tiledb vacuum array-metadata [array_uri]
    """
    result = runner.invoke(root, ["consolidate", "array-metadata", uri])
    assert result.exit_code == 0

    result = runner.invoke(root, ["vacuum", "array-metadata", uri])
    assert result.exit_code == 0
