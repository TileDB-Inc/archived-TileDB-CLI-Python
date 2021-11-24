import tiledb
from common import test_array_names
from commands.root import root

import ast
from click.testing import CliRunner
import numpy as np
import os
import pytest
import tempfile


class TestConfig:
    def test(self, runner):
        """
        Test for command

            tiledb dump config
        """
        result = runner.invoke(root, ["dump", "config"])
        assert result.exit_code == 0
        assert result.stdout.split() == tiledb.Config().__repr__().split()


class TestMBRs:
    @pytest.mark.parametrize("array_name", test_array_names)
    def test(self, runner, temp_rootdir, array_name, pp):
        """
        Test for command

            tiledb dump mbr [array_uri]
        """
        uri = os.path.abspath(os.path.join(temp_rootdir, array_name))

        result = runner.invoke(root, ["dump", "mbrs", uri])
        assert result.exit_code == 0

        fragments = tiledb.array_fragments(uri, include_mbrs=True)
        assert result.stdout.split() == pp.pformat(fragments.mbrs).split()


class TestMetadata:
    @pytest.mark.parametrize("array_name", test_array_names)
    def test(self, runner, temp_rootdir, array_name, pp):
        """
        Test for command

            tiledb dump metadata [array_uri]
        """
        uri = os.path.abspath(os.path.join(temp_rootdir, array_name))

        result = runner.invoke(root, ["dump", "metadata", uri])
        assert result.exit_code == 0

        with tiledb.open(uri) as array:
            assert result.stdout.split() == pp.pformat(array.meta.items()).split()


class TestNonemptyDomain:
    @pytest.mark.parametrize("array_name", test_array_names)
    def test(self, runner, temp_rootdir, array_name, pp):
        """
        Test for command

            tiledb dump non-emptydomain [array_uri]
        """
        uri = os.path.abspath(os.path.join(temp_rootdir, array_name))

        result = runner.invoke(root, ["dump", "nonempty-domain", uri])
        assert result.exit_code == 0

        with tiledb.open(uri) as array:
            assert result.stdout.split() == pp.pformat(array.nonempty_domain()).split()


class TestSchema:
    @pytest.mark.parametrize("array_name", test_array_names)
    def test(self, runner, temp_rootdir, array_name, pp):
        """
        Test for command

            tiledb dump schema [array_uri]
        """
        uri = os.path.abspath(os.path.join(temp_rootdir, array_name))

        result = runner.invoke(root, ["dump", "schema", uri])
        assert result.exit_code == 0

        with tiledb.open(uri) as array:
            assert result.stdout.split() == pp.pformat(array.schema).split()


class TestArray:
    @pytest.mark.parametrize("sparse", [True, False])
    @pytest.mark.parametrize(
        "dtype",
        [
            np.int8,
            np.uint8,
            np.int16,
            np.uint16,
            np.int32,
            np.uint32,
            np.int64,
            np.uint64,
        ],
    )
    def test_int_dtypes(self, runner, temp_rootdir, sparse, dtype):
        uri = os.path.abspath(
            os.path.join(
                temp_rootdir,
                tempfile.mkdtemp(),
                "test_int_dtypes_"
                f"{'sparse' if sparse else 'dense'}_"
                f"{np.dtype(dtype).name}",
            )
        )

        dom = tiledb.Domain(tiledb.Dim(domain=(1, 10), dtype=dtype))
        att = tiledb.Attr(dtype=dtype)
        schema = tiledb.ArraySchema(domain=dom, attrs=(att,), sparse=sparse)
        tiledb.Array.create(uri, schema)

        with tiledb.open(uri, mode="w") as A:
            if sparse:
                A[np.arange(1, 11)] = np.random.randint(10, size=10, dtype=dtype)
            else:
                A[:] = np.random.randint(10, size=10, dtype=dtype)

        result = runner.invoke(root, ["dump", "array", uri, "5"])
        assert result.exit_code == 0

        result = runner.invoke(root, ["dump", "array", uri, "1:10"])
        assert result.exit_code == 0

    @pytest.mark.parametrize("dtype", [np.float32, np.float64])
    def test_float_dtypes(self, runner, temp_rootdir, dtype):
        uri = os.path.abspath(
            os.path.join(
                temp_rootdir,
                tempfile.mkdtemp(),
                f"test_float_dtypes_{np.dtype(dtype).name}",
            )
        )

        dom = tiledb.Domain(tiledb.Dim(domain=(1, 10), dtype=dtype))
        att = tiledb.Attr(dtype=dtype)
        schema = tiledb.ArraySchema(domain=dom, attrs=(att,), sparse=True)
        tiledb.Array.create(uri, schema)

        with tiledb.open(uri, mode="w") as A:
            A[np.arange(1, 11)] = np.random.rand(10)

        result = runner.invoke(root, ["dump", "array", uri, "5"])
        assert result.exit_code == 0

        result = runner.invoke(root, ["dump", "array", uri, "1:10"])
        assert result.exit_code == 0

    @pytest.mark.parametrize(
        "dtype",
        [
            "datetime64[Y]",
            "datetime64[M]",
            "datetime64[W]",
            "datetime64[D]",
            "datetime64[h]",
            "datetime64[m]",
            "datetime64[s]",
            "datetime64[ms]",
            "datetime64[us]",
            "datetime64[ns]",
            # "datetime64[ps]",
            # "datetime64[fs]",
            # "datetime64[as]",
        ],
    )
    def test_datetime_dtype(self, runner, temp_rootdir, dtype):
        uri = os.path.abspath(
            os.path.join(
                temp_rootdir,
                tempfile.mkdtemp(),
                f"test_datetime_dtype_{np.dtype(dtype).name}",
            )
        )

        dom = tiledb.Domain(
            tiledb.Dim(
                domain=(np.datetime64("1970-01-01"), np.datetime64("1980-01-01")),
                dtype=dtype,
            )
        )
        att = tiledb.Attr(dtype=dtype)
        schema = tiledb.ArraySchema(domain=dom, attrs=(att,), sparse=True)
        tiledb.Array.create(uri, schema)

        with tiledb.open(uri, mode="w") as A:
            A[np.arange(1, 11)] = np.random.randint(low=1, high=10, size=10)

        result = runner.invoke(root, ["dump", "array", uri, "'1970-01-04'"])
        assert result.exit_code == 0

        result = runner.invoke(
            root, ["dump", "array", uri, "'1970-01-01':'1980-01-01'"]
        )
        assert result.exit_code == 0

    @pytest.mark.parametrize("dtype", [np.dtype("S"), np.dtype("U")])
    def test_string_dtypes(self, runner, temp_rootdir, dtype):
        uri = os.path.abspath(
            os.path.join(temp_rootdir, f"test_numeric_dtypes_{np.dtype(dtype).name}")
        )

        dom = tiledb.Domain(tiledb.Dim(domain=(1, 10), dtype=np.dtype("S")))
        att = tiledb.Attr(dtype=dtype)
        schema = tiledb.ArraySchema(domain=dom, attrs=(att,), sparse=True)
        tiledb.Array.create(uri, schema)

        with tiledb.open(uri, mode="w") as A:
            arr = np.char.mod("%d", np.random.randint(10, size=10))
            print(arr)
            A[np.arange(1, 11)] = arr

        result = runner.invoke(root, ["dump", "array", uri, "1:10"])
        assert result.exit_code == 0

    def test_dense_25x12(self, runner, temp_rootdir):
        """
        Test for command

            tiledb dump array [array_uri]
        """
        uri = os.path.abspath(os.path.join(temp_rootdir, "dense_25x12"))

        result = runner.invoke(root, ["dump", "array", uri, "1:25", "1:12"])
        assert result.exit_code == 0

    def test_dense_25x12_rows(self, runner, temp_rootdir):
        """
        Test for command

            tiledb dump array [array_uri]
        """
        uri = os.path.abspath(os.path.join(temp_rootdir, "dense_25x12"))

        result = runner.invoke(root, ["dump", "array", uri, "-d", "row", "1:25"])
        assert result.exit_code == 0

    def test_dense_25x12x3(self, runner, temp_rootdir):
        """
        Test for command

            tiledb dump array [array_uri]
        """
        uri = os.path.abspath(os.path.join(temp_rootdir, "dense_25x12x3"))

        result = runner.invoke(root, ["dump", "array", uri, "1:25", "1:12", "1:3"])
        assert result.exit_code == 0

    def test_dense_25x12x3_rows(self, runner, temp_rootdir):
        """
        Test for command

            tiledb dump array [array_uri]
        """
        uri = os.path.abspath(os.path.join(temp_rootdir, "dense_25x12x3"))

        result = runner.invoke(root, ["dump", "array", uri, "-d", "x", "2:3"])
        assert result.exit_code == 0

    def test_dense_25x12_mult(self, runner, temp_rootdir):
        """
        Test for command

            tiledb dump array [array_uri]
        """
        uri = os.path.abspath(os.path.join(temp_rootdir, "dense_25x12_mult"))

        result = runner.invoke(root, ["dump", "array", uri, "1:25", "1:12"])
        assert result.exit_code == 0

    def test_dense_25x12_mult_rows_attributes(self, runner, temp_rootdir):
        """
        Test for command

            tiledb dump array [array_uri]
        """
        uri = os.path.abspath(os.path.join(temp_rootdir, "dense_25x12_mult"))

        result = runner.invoke(
            root, ["dump", "array", uri, "-d", "row", "2:3", "-A", "b"]
        )
        assert result.exit_code == 0

    def test_sparse_25x12(self, runner, temp_rootdir):
        """
        Test for command

            tiledb dump array [array_uri]
        """
        uri = os.path.abspath(os.path.join(temp_rootdir, "sparse_25x12"))

        result = runner.invoke(root, ["dump", "array", uri, "1:25", "1:12"])
        assert result.exit_code == 0

    def test_sparse_25x12_rows(self, runner, temp_rootdir):
        """
        Test for command

            tiledb dump array [array_uri]
        """
        uri = os.path.abspath(os.path.join(temp_rootdir, "sparse_25x12"))

        result = runner.invoke(root, ["dump", "array", uri, "2:3", "-d", "row"])
        assert result.exit_code == 0

    def test_sparse_25x12_mult(self, runner, temp_rootdir):
        """
        Test for command

            tiledb dump array [array_uri]
        """
        uri = os.path.abspath(os.path.join(temp_rootdir, "sparse_25x12_mult"))

        result = runner.invoke(root, ["dump", "array", uri, "1:25", "1:12"])
        assert result.exit_code == 0

    def test_sparse_25x12_mult_rows_attributes(self, runner, temp_rootdir):
        """
        Test for command

            tiledb dump array [array_uri]
        """
        uri = os.path.abspath(os.path.join(temp_rootdir, "sparse_25x12_mult"))

        result = runner.invoke(
            root, ["dump", "array", uri, "-d", "row", "2:3", "-A", "b"]
        )
        assert result.exit_code == 0

    @pytest.mark.parametrize("array_name", ["dense_25x12_mult", "sparse_25x12_mult"])
    def test_timestamp(self, runner, temp_rootdir, array_name):
        """
        Test for command

            tiledb dump array [array_uri] -t <unix seconds>
        """
        uri = os.path.abspath(os.path.join(temp_rootdir, array_name))

        # check at timestamp=1
        result = runner.invoke(root, ["dump", "array", uri, "1:25", "1:12", "-t", 1])
        assert result.exit_code == 0

        # check at timestamp=2
        result = runner.invoke(root, ["dump", "array", uri, "1:25", "1:12", "-t", 2])
        assert result.exit_code == 0


class TestFragments:
    @pytest.mark.parametrize("array_name", ["dense_25x12_mult", "sparse_25x12_mult"])
    def test_number(self, runner, temp_rootdir, array_name):
        """
        Test for command

            tiledb dump fragments [array_uri] -n
        """
        uri = os.path.abspath(os.path.join(temp_rootdir, array_name))

        result = runner.invoke(root, ["dump", "fragments", uri, "-n"])
        assert result.exit_code == 0
        assert result.stdout.strip() == "2"

    @pytest.mark.parametrize("array_name", ["dense_25x12_mult", "sparse_25x12_mult"])
    def test_index(self, runner, temp_rootdir, array_name):
        """
        Test for command

            tiledb dump fragments [array_uri]
        """
        uri = os.path.abspath(os.path.join(temp_rootdir, array_name))

        result = runner.invoke(root, ["dump", "fragments", uri, "-i", "0"])
        assert result.exit_code == 0
        assert "'num': 0" in result.stdout

        result = runner.invoke(root, ["dump", "fragments", uri, "-i", "1"])
        assert result.exit_code == 0
        assert "'num': 1" in result.stdout

    def test_dense_25x12_mult(self, runner, temp_rootdir):
        """
        Test for command

            tiledb dump fragments [array_uri]
        """
        uri = os.path.abspath(os.path.join(temp_rootdir, "dense_25x12_mult"))

        result = runner.invoke(root, ["dump", "fragments", uri])
        assert result.exit_code == 0

        output = ast.literal_eval("".join(result.stdout.split()))
        assert output["array_uri"] == os.path.join(
            f"{temp_rootdir}", "dense_25x12_mult"
        )
        assert output["cell_num"] == (300, 300)
        assert output["sparse"] == (False, False)
        assert output["has_consolidated_metadata"] == (False, False)
        assert output["nonempty_domain"] == (((1, 25), (1, 12)), ((1, 25), (1, 12)))
        assert output["sparse"] == (False, False)
        assert output["to_vacuum"] == ()
        assert output["unconsolidated_metadata_num"] == 2

    def test_sparse_25x12_mult(self, runner, temp_rootdir):
        """
        Test for command

            tiledb dump fragments [array_uri]
        """
        uri = os.path.abspath(os.path.join(temp_rootdir, "sparse_25x12_mult"))

        result = runner.invoke(root, ["dump", "fragments", uri])
        assert result.exit_code == 0

        output = ast.literal_eval("".join(result.stdout.split()))
        assert output["array_uri"] == os.path.join(
            f"{temp_rootdir}", "sparse_25x12_mult"
        )
        assert output["cell_num"] == (300, 300)
        assert output["sparse"] == (True, True)
        assert output["has_consolidated_metadata"] == (False, False)
        assert output["nonempty_domain"] == (((1, 25), (1, 12)), ((1, 25), (1, 12)))
        assert output["sparse"] == (True, True)
        assert output["to_vacuum"] == ()
        assert output["unconsolidated_metadata_num"] == 2
