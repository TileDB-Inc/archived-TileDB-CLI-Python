import tiledb
from common import pp, test_array_names
from commands.root import root

import ast
from click.testing import CliRunner
import numpy as np
import os
import pytest
import re


class TestConfig:
    def test(self):
        """
        Test for command

            tiledb dump config
        """
        runner = CliRunner()
        result = runner.invoke(root, ["dump", "config"])
        assert result.exit_code == 0
        assert result.stdout.split() == tiledb.Config().__repr__().split()


class TestMetadata:
    @pytest.mark.parametrize("array_name", test_array_names)
    def test(self, temp_rootdir, array_name, pp):
        """
        Test for command

            tiledb dump metadata [array_uri]
        """
        uri = os.path.abspath(os.path.join(temp_rootdir, array_name))

        runner = CliRunner()
        result = runner.invoke(root, ["dump", "metadata", uri])
        assert result.exit_code == 0

        with tiledb.open(uri) as array:
            assert result.stdout.split() == pp.pformat(array.meta.items()).split()


class TestNonemptyDomain:
    @pytest.mark.parametrize("array_name", test_array_names)
    def test(self, temp_rootdir, array_name, pp):
        """
        Test for command

            tiledb dump non-emptydomain [array_uri]
        """
        uri = os.path.abspath(os.path.join(temp_rootdir, array_name))

        runner = CliRunner()
        result = runner.invoke(root, ["dump", "nonempty-domain", uri])
        assert result.exit_code == 0

        with tiledb.open(uri) as array:
            assert result.stdout.split() == pp.pformat(array.nonempty_domain()).split()


class TestSchema:
    @pytest.mark.parametrize("array_name", test_array_names)
    def test(self, temp_rootdir, array_name, pp):
        """
        Test for command

            tiledb dump schema [array_uri]
        """
        uri = os.path.abspath(os.path.join(temp_rootdir, array_name))

        runner = CliRunner()
        result = runner.invoke(root, ["dump", "schema", uri])
        assert result.exit_code == 0

        with tiledb.open(uri) as array:
            assert result.stdout.split() == pp.pformat(array.schema).split()


class TestArray:
    def test_dense_25x12(self, temp_rootdir):
        """
        Test for command

            tiledb dump array [array_uri]
        """
        uri = os.path.abspath(os.path.join(temp_rootdir, "dense_25x12"))

        runner = CliRunner()
        result = runner.invoke(root, ["dump", "array", uri])
        assert result.exit_code == 0

        raw_resulting_array = re.findall(r"array\(\[([\s\S]+)\].*\)", result.stdout)
        assert len(raw_resulting_array) == 1

        resulting_array = raw_resulting_array[0].split(",\n")
        assert len(resulting_array) == 5

        for row_idx, raw_row in enumerate(resulting_array):
            resulting_row = list(map(int, raw_row.strip()[1:-1].split(",")))
            assert resulting_row == list(range(row_idx * 12, (row_idx + 1) * 12))

    def test_dense_25x12_rows(self, temp_rootdir):
        """
        Test for command

            tiledb dump array [array_uri]
        """
        uri = os.path.abspath(os.path.join(temp_rootdir, "dense_25x12"))

        runner = CliRunner()
        result = runner.invoke(root, ["dump", "array", uri, "-n", "2", "3"])
        assert result.exit_code == 0

        raw_resulting_array = re.findall(r"array\(\[([\s\S]+)\].*\)", result.stdout)
        assert len(raw_resulting_array) == 1

        resulting_array = raw_resulting_array[0].split(",\n")
        assert len(resulting_array) == 2

        for row_idx, raw_row in enumerate(resulting_array, start=1):
            resulting_row = list(map(int, raw_row.strip()[1:-1].split(",")))
            assert resulting_row == list(range(row_idx * 12, (row_idx + 1) * 12))

    def test_dense_25x12x3(self, temp_rootdir):
        """
        Test for command

            tiledb dump array [array_uri]
        """
        uri = os.path.abspath(os.path.join(temp_rootdir, "dense_25x12x3"))

        runner = CliRunner()
        result = runner.invoke(root, ["dump", "array", uri])
        assert result.exit_code == 0

        raw_resulting_3rd_dim = re.findall(r"array\(\[([\s\S]+)\].*\)", result.stdout)
        assert len(raw_resulting_3rd_dim) == 1

        raw_resulting_2nd_dim = raw_resulting_3rd_dim[0].split(",\n\n")
        assert len(raw_resulting_2nd_dim) == 5

        for idx_x, raw_2nd_dim_row in enumerate(raw_resulting_2nd_dim):
            for idx_y, raw_row in enumerate(raw_2nd_dim_row.strip()[1:-1].split(",\n")):
                resulting_row = list(map(int, raw_row.strip()[1:-1].split(",")))
                expected_row = idx_x * 36 + idx_y * 3
                assert resulting_row == list(range(expected_row, expected_row + 3))

    def test_dense_25x12x3_rows(self, temp_rootdir):
        """
        Test for command

            tiledb dump array [array_uri]
        """
        uri = os.path.abspath(os.path.join(temp_rootdir, "dense_25x12x3"))

        runner = CliRunner()
        result = runner.invoke(root, ["dump", "array", uri, "-n", "2", "3"])
        assert result.exit_code == 0

        raw_resulting_3rd_dim = re.findall(r"array\(\[([\s\S]+)\].*\)", result.stdout)
        assert len(raw_resulting_3rd_dim) == 1

        raw_resulting_2nd_dim = raw_resulting_3rd_dim[0].split(",\n\n")
        assert len(raw_resulting_2nd_dim) == 2

        for idx_x, raw_2nd_dim_row in enumerate(raw_resulting_2nd_dim, start=1):
            for idx_y, raw_row in enumerate(raw_2nd_dim_row.strip()[1:-1].split(",\n")):
                resulting_row = list(map(int, raw_row.strip()[1:-1].split(",")))
                expected_row = idx_x * 36 + idx_y * 3
                assert resulting_row == list(range(expected_row, expected_row + 3))

    def test_dense_25x12_mult(self, temp_rootdir):
        """
        Test for command

            tiledb dump array [array_uri]
        """
        uri = os.path.abspath(os.path.join(temp_rootdir, "dense_25x12_mult"))

        runner = CliRunner()
        result = runner.invoke(root, ["dump", "array", uri])
        assert result.exit_code == 0

        raw_array = re.findall(r"array\(\[(.*?)\]\)", "".join(result.stdout.split()))
        assert len(raw_array) == 2

        raw_a_dim = re.findall(r"\[(.*?)\]", raw_array[0])
        for row_idx, raw_a_dim_row in enumerate(raw_a_dim):
            resulting_row = list(map(float, raw_a_dim_row.split(",")))
            expected_row = list(
                map(lambda x: x / 2, range(row_idx * 12, (row_idx + 1) * 12))
            )
            assert resulting_row == expected_row

        raw_b_dim = re.findall(r"\[(.*?)\]", raw_array[1])
        for row_idx, raw_b_dim_row in enumerate(raw_b_dim):
            resulting_row = list(map(float, raw_b_dim_row.split(",")))
            expected_row = list(
                map(lambda x: x * 2, range(row_idx * 12, (row_idx + 1) * 12))
            )
            assert resulting_row == expected_row

    def test_dense_25x12_mult_rows_attributes(self, temp_rootdir):
        """
        Test for command

            tiledb dump array [array_uri]
        """
        uri = os.path.abspath(os.path.join(temp_rootdir, "dense_25x12_mult"))

        runner = CliRunner()
        result = runner.invoke(root, ["dump", "array", uri, "-n", "2", "3", "-A", "b"])
        assert result.exit_code == 0

        raw_array = re.findall(r"array\(\[(.*?)\].*\)", "".join(result.stdout.split()))
        assert len(raw_array) == 1

        raw_b_dim = re.findall(r"\[(.*?)\]", raw_array[0])
        for row_idx, raw_b_dim_row in enumerate(raw_b_dim, start=1):
            resulting_row = list(map(float, raw_b_dim_row.split(",")))
            expected_row = list(
                map(lambda x: x * 2, range(row_idx * 12, (row_idx + 1) * 12))
            )
            assert resulting_row == expected_row

    def test_sparse_25x12(self, temp_rootdir):
        """
        Test for command

            tiledb dump array [array_uri]
        """
        uri = os.path.abspath(os.path.join(temp_rootdir, "sparse_25x12"))

        runner = CliRunner()
        result = runner.invoke(root, ["dump", "array", uri])
        assert result.exit_code == 0

        raw_resulting_array = re.findall(
            r"array\(\[(.*?)\].*\)", "".join(result.stdout.split())
        )
        assert len(raw_resulting_array) == 1
        resulting_row = list(map(int, raw_resulting_array[0].split(",")))
        assert resulting_row == list(range(60))

    def test_sparse_25x12_rows(self, temp_rootdir):
        """
        Test for command

            tiledb dump array [array_uri]
        """
        uri = os.path.abspath(os.path.join(temp_rootdir, "sparse_25x12"))

        runner = CliRunner()
        result = runner.invoke(root, ["dump", "array", uri, "-n", "2", "3"])
        assert result.exit_code == 0

        raw_resulting_array = re.findall(
            r"array\(\[(.*?)\].*\)", "".join(result.stdout.split())
        )
        assert len(raw_resulting_array) == 1
        resulting_row = list(map(int, raw_resulting_array[0].split(",")))
        assert resulting_row == list(range(12, 36))

    def test_sparse_25x12_mult(self, temp_rootdir):
        """
        Test for command

            tiledb dump array [array_uri]
        """
        uri = os.path.abspath(os.path.join(temp_rootdir, "sparse_25x12_mult"))

        runner = CliRunner()
        result = runner.invoke(root, ["dump", "array", uri])
        assert result.exit_code == 0

        raw_array = re.findall(r"array\(\[(.*?)\]\)", "".join(result.stdout.split()))
        assert len(raw_array) == 2

        raw_a_dim = re.findall(r"\[(.*?)\]", raw_array[0])
        for row_idx, raw_a_dim_row in enumerate(raw_a_dim):
            resulting_row = list(map(float, raw_a_dim_row.split(",")))
            expected_row = list(
                map(lambda x: x / 2, range(row_idx * 12, (row_idx + 1) * 12))
            )
            assert resulting_row == expected_row

        raw_b_dim = re.findall(r"\[(.*?)\]", raw_array[1])
        for row_idx, raw_b_dim_row in enumerate(raw_b_dim):
            resulting_row = list(map(float, raw_b_dim_row.split(",")))
            expected_row = list(
                map(lambda x: x * 2, range(row_idx * 12, (row_idx + 1) * 12))
            )
            assert resulting_row == expected_row

    def test_sparse_25x12_mult_rows_attributes(self, temp_rootdir):
        """
        Test for command

            tiledb dump array [array_uri]
        """
        uri = os.path.abspath(os.path.join(temp_rootdir, "sparse_25x12_mult"))

        runner = CliRunner()
        result = runner.invoke(root, ["dump", "array", uri, "-n", "2", "3", "-A", "b"])
        assert result.exit_code == 0

        raw_array = re.findall(r"array\(\[(.*?)\].*\)", "".join(result.stdout.split()))
        assert len(raw_array) == 1

        raw_b_dim = re.findall(r"\[(.*?)\]", raw_array[0])
        for row_idx, raw_b_dim_row in enumerate(raw_b_dim, start=1):
            resulting_row = list(map(float, raw_b_dim_row.split(",")))
            expected_row = list(
                map(lambda x: x * 2, range(row_idx * 12, (row_idx + 1) * 12))
            )
            assert resulting_row == expected_row


class TestFragments:
    @pytest.mark.parametrize("array_name", ["dense_25x12_mult", "sparse_25x12_mult"])
    def test_number(self, temp_rootdir, array_name):
        """
        Test for command

            tiledb dump fragments [array_uri] -n
        """
        uri = os.path.abspath(os.path.join(temp_rootdir, array_name))

        runner = CliRunner()
        result = runner.invoke(root, ["dump", "fragments", uri, "-n"])
        assert result.exit_code == 0
        assert result.stdout.strip() == "2"

    @pytest.mark.parametrize("array_name", ["dense_25x12_mult", "sparse_25x12_mult"])
    def test_index(self, temp_rootdir, array_name):
        """
        Test for command

            tiledb dump fragments [array_uri]
        """
        uri = os.path.abspath(os.path.join(temp_rootdir, array_name))

        runner = CliRunner()
        result = runner.invoke(root, ["dump", "fragments", uri, "-i", "0"])
        assert result.exit_code == 0
        assert "'num': 0" in result.stdout

        result = runner.invoke(root, ["dump", "fragments", uri, "-i", "1"])
        assert result.exit_code == 0
        assert "'num': 1" in result.stdout

    def test_dense_25x12_mult(self, temp_rootdir):
        """
        Test for command

            tiledb dump fragments [array_uri]
        """
        uri = os.path.abspath(os.path.join(temp_rootdir, "dense_25x12_mult"))

        runner = CliRunner()
        result = runner.invoke(root, ["dump", "fragments", uri])
        assert result.exit_code == 0

        output = ast.literal_eval("".join(result.stdout.split()))
        assert output["array_uri"] == os.path.join(
            f"{temp_rootdir}", "dense_25x12_mult"
        )
        assert output["cell_num"] == (300, 300)
        assert output["dense"] == (True, True)
        assert output["has_consolidated_metadata"] == (False, False)
        assert output["non_empty_domain"] == (((1, 25), (1, 12)), ((1, 25), (1, 12)))
        assert output["sparse"] == (False, False)
        assert output["to_vacuum_num"] == 0
        assert output["to_vacuum_uri"] == []
        assert output["unconsolidated_metadata_num"] == 2

    def test_sparse_25x12_mult(self, temp_rootdir):
        """
        Test for command

            tiledb dump fragments [array_uri]
        """
        uri = os.path.abspath(os.path.join(temp_rootdir, "sparse_25x12_mult"))

        runner = CliRunner()
        result = runner.invoke(root, ["dump", "fragments", uri])
        assert result.exit_code == 0

        output = ast.literal_eval("".join(result.stdout.split()))
        assert output["array_uri"] == os.path.join(
            f"{temp_rootdir}", "sparse_25x12_mult"
        )
        assert output["cell_num"] == (300, 300)
        assert output["dense"] == (False, False)
        assert output["has_consolidated_metadata"] == (False, False)
        assert output["non_empty_domain"] == (((1, 25), (1, 12)), ((1, 25), (1, 12)))
        assert output["sparse"] == (True, True)
        assert output["to_vacuum_num"] == 0
        assert output["to_vacuum_uri"] == []
        assert output["unconsolidated_metadata_num"] == 2
