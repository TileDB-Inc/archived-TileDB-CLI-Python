import tiledb

import numpy as np
import itertools
import pprint
import os
import pytest
import shutil
import tempfile

test_array_names = ["dense_25x12", "sparse_25x12"]


@pytest.fixture(scope="session")
def temp_rootdir():
    """
    Create the temporary directory that stores all test arrays.
    """
    dir = tempfile.mkdtemp()
    yield dir
    shutil.rmtree(dir)


@pytest.fixture(autouse=True, scope="session")
def create_test_array_dense_25x12(temp_rootdir):
    """
    Create a simple dense test array.
    """
    path = os.path.abspath(os.path.join(temp_rootdir, "dense_25x12"))

    ctx = tiledb.default_ctx()
    rows_dim = tiledb.Dim(ctx=ctx, domain=(1, 25), dtype=np.int64)
    cols_dim = tiledb.Dim(ctx=ctx, domain=(1, 12), dtype=np.int64)
    dom = tiledb.Domain(rows_dim, cols_dim, ctx=ctx)
    att = tiledb.Attr(ctx=ctx, dtype=np.int64)
    schema = tiledb.ArraySchema(ctx=ctx, domain=dom, attrs=(att,))

    tiledb.DenseArray.create(path, schema)

    with tiledb.DenseArray(path, mode="w") as A:
        data = np.arange(300)
        np.reshape(data, (25, 12))
        A[:] = data


@pytest.fixture(autouse=True, scope="session")
def create_test_array_sparse_25x12(temp_rootdir):
    """
    Create a simple sparse test array.
    """
    path = os.path.abspath(os.path.join(temp_rootdir, "sparse_25x12"))

    ctx = tiledb.default_ctx()
    rows_dim = tiledb.Dim(ctx=ctx, domain=(1, 25), dtype=np.int64)
    cols_dim = tiledb.Dim(ctx=ctx, domain=(1, 12), dtype=np.int64)
    dom = tiledb.Domain(rows_dim, cols_dim, ctx=ctx)
    att = tiledb.Attr(ctx=ctx, dtype=np.int64)
    schema = tiledb.ArraySchema(ctx=ctx, sparse=True, domain=dom, attrs=(att,))

    tiledb.SparseArray.create(path, schema)

    with tiledb.SparseArray(path, mode="w") as A:
        coords = np.array(list(itertools.product(np.arange(1, 26), np.arange(1, 13))))
        rows = coords[:, 0]
        cols = coords[:, 1]
        A[rows, cols] = np.arange(300)

    yield

    shutil.rmtree(path)


@pytest.fixture(scope="session")
def pp():
    """
    Initalize PrettyPrinter().
    """
    return pprint.PrettyPrinter()
