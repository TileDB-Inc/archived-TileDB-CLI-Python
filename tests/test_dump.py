import tiledb
from common import pp, test_array_names
from dump import root

from click.testing import CliRunner
import numpy as np
import os
import pytest


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
    def test_dense_25x12(self, temp_rootdir, pp):
        """
        Test for command

            tiledb dump array [array_uri]
        """
        uri = os.path.abspath(os.path.join(temp_rootdir, "dense_25x12"))

        runner = CliRunner()
        result = runner.invoke(root, ["dump", "array", uri])
        assert result.exit_code == 0

        expected_output = {"": np.reshape(np.arange(60), (5, 12))}
        assert result.stdout.split() == pp.pformat(expected_output).split()

    def test_dense_25x12_rows(self, temp_rootdir, pp):
        """
        Test for command

            tiledb dump array [array_uri]
        """
        uri = os.path.abspath(os.path.join(temp_rootdir, "dense_25x12"))

        runner = CliRunner()
        result = runner.invoke(root, ["dump", "array", uri, "-n", "2", "3"])
        assert result.exit_code == 0

        expected_output = {"": np.reshape(np.arange(12, 36), (2, 12))}
        assert result.stdout.split() == pp.pformat(expected_output).split()

    def test_dense_25x12x3(self, temp_rootdir, pp):
        """
        Test for command

            tiledb dump array [array_uri]
        """
        uri = os.path.abspath(os.path.join(temp_rootdir, "dense_25x12x3"))

        runner = CliRunner()
        result = runner.invoke(root, ["dump", "array", uri])
        assert result.exit_code == 0

        expected_output = {"": np.reshape(np.arange(180), (5, 12, 3))}
        assert result.stdout.split() == pp.pformat(expected_output).split()

    def test_dense_25x12x3_rows(self, temp_rootdir, pp):
        """
        Test for command

            tiledb dump array [array_uri]
        """
        uri = os.path.abspath(os.path.join(temp_rootdir, "dense_25x12x3"))

        runner = CliRunner()
        result = runner.invoke(root, ["dump", "array", uri, "-n", "2", "3"])
        assert result.exit_code == 0

        expected_output = {"": np.reshape(np.arange(36, 108), (2, 12, 3))}
        assert result.stdout.split() == pp.pformat(expected_output).split()

    def test_dense_25x12_mult(self, temp_rootdir, pp):
        """
        Test for command

            tiledb dump array [array_uri]
        """
        uri = os.path.abspath(os.path.join(temp_rootdir, "dense_25x12_mult"))

        runner = CliRunner()
        result = runner.invoke(root, ["dump", "array", uri])
        assert result.exit_code == 0

        data = np.reshape(np.arange(60, dtype=np.float64), (5, 12))
        expected_output = {"a": data / 2, "b": data * 2}
        assert result.stdout.split() == pp.pformat(expected_output).split()

    def test_dense_25x12_mult_rows_attributes(self, temp_rootdir, pp):
        """
        Test for command

            tiledb dump array [array_uri]
        """
        uri = os.path.abspath(os.path.join(temp_rootdir, "dense_25x12_mult"))

        runner = CliRunner()
        result = runner.invoke(root, ["dump", "array", uri, "-n", "2", "3", "-A", "b"])
        assert result.exit_code == 0

        data = np.reshape(np.arange(12, 36, dtype=np.float64), (2, 12))
        expected_output = {"b": data * 2}
        assert result.stdout.split() == pp.pformat(expected_output).split()

    def test_sparse_25x12(self, temp_rootdir, pp):
        """
        Test for command

            tiledb dump array [array_uri]
        """
        uri = os.path.abspath(os.path.join(temp_rootdir, "sparse_25x12"))

        runner = CliRunner()
        result = runner.invoke(root, ["dump", "array", uri])
        assert result.exit_code == 0

        expected_output = {"": np.arange(60)}
        assert result.stdout.split() == pp.pformat(expected_output).split()

    def test_sparse_25x12_rows(self, temp_rootdir, pp):
        """
        Test for command

            tiledb dump array [array_uri]
        """
        uri = os.path.abspath(os.path.join(temp_rootdir, "sparse_25x12"))

        runner = CliRunner()
        result = runner.invoke(root, ["dump", "array", uri, "-n", "2", "3"])
        assert result.exit_code == 0

        expected_output = {"": np.arange(12, 36)}
        assert result.stdout.split() == pp.pformat(expected_output).split()

    def test_sparse_25x12_mult(self, temp_rootdir, pp):
        """
        Test for command

            tiledb dump array [array_uri]
        """
        uri = os.path.abspath(os.path.join(temp_rootdir, "sparse_25x12_mult"))

        runner = CliRunner()
        result = runner.invoke(root, ["dump", "array", uri])
        assert result.exit_code == 0

        data = np.arange(60, dtype=np.float64)
        expected_output = {"a": data / 2, "b": data * 2}
        assert result.stdout.split() == pp.pformat(expected_output).split()

    def test_sparse_25x12_mult_rows_attributes(self, temp_rootdir, pp):
        """
        Test for command

            tiledb dump array [array_uri]
        """
        uri = os.path.abspath(os.path.join(temp_rootdir, "sparse_25x12_mult"))

        runner = CliRunner()
        result = runner.invoke(root, ["dump", "array", uri, "-n", "2", "3", "-A", "b"])
        assert result.exit_code == 0

        data = np.arange(12, 36, dtype=np.float64)
        expected_output = {"b": data * 2}
        assert result.stdout.split() == pp.pformat(expected_output).split()


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
        assert f"'array_uri': '{temp_rootdir}/dense_25x12_mult'" in result.stdout
        assert "'cell_num': (300, 300)" in result.stdout
        assert "'dense': (True, True)" in result.stdout
        assert "'has_consolidated_metadata': (False, False)" in result.stdout
        assert (
            "'non_empty_domain': (((1, 25), (1, 12)), ((1, 25), (1, 12)))"
            in result.stdout
        )
        assert "'sparse': (False, False)" in result.stdout
        assert "'to_vacuum_num': 0" in result.stdout
        assert "'to_vacuum_uri': []" in result.stdout
        assert "'unconsolidated_metadata_num': 2" in result.stdout

    def test_sparse_25x12_mult(self, temp_rootdir):
        """
        Test for command

            tiledb dump fragments [array_uri]
        """
        uri = os.path.abspath(os.path.join(temp_rootdir, "sparse_25x12_mult"))

        runner = CliRunner()
        result = runner.invoke(root, ["dump", "fragments", uri])
        assert result.exit_code == 0
        assert f"'array_uri': '{temp_rootdir}/sparse_25x12_mult'" in result.stdout
        assert "'cell_num': (300, 300)" in result.stdout
        assert "'dense': (False, False)" in result.stdout
        assert "'has_consolidated_metadata': (False, False)" in result.stdout
        assert (
            "'non_empty_domain': (((1, 25), (1, 12)), ((1, 25), (1, 12)))"
            in result.stdout
        )
        assert "'sparse': (True, True)" in result.stdout
        assert "'to_vacuum_num': 0" in result.stdout
        assert "'to_vacuum_uri': []" in result.stdout
        assert "'unconsolidated_metadata_num': 2" in result.stdout
