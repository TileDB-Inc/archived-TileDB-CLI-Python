import tiledb
from commands.root import root

from click.testing import CliRunner
import os
import pytest


@pytest.fixture(autouse=True, scope="session")
def create_test_simple_csv(temp_rootdir):
    """
    Create a simple dense test array.
    """
    path = os.path.abspath(os.path.join(temp_rootdir, "simple.csv"))

    with open(path, mode="w") as csv_input:
        csv_input.write(
            (
                "a,b,c,date\n"
                '1,"text",3.4,Mar/02/2021\n'
                '2,"hello",1.234,Apr/07/2021\n'
                '3,"goodbye",111.232,Dec/17/2021\n'
                '4,"world",123123.12,Jul/21/2021\n'
                '10,"raisins",14.232,Nov/09/2021\n'
            )
        )


class TestCSV:
    def test(self, temp_rootdir):
        """
        Test for command

            tiledb convert_from [csv_file] [uri]
        """
        test_name = "simple"
        input_path = os.path.join(temp_rootdir, f"{test_name}.csv")
        uri = os.path.join(temp_rootdir, "test.tdb")

        runner = CliRunner()
        result = runner.invoke(
            root,
            [
                "convert-from",
                "csv",
                input_path,
                uri,
            ],
        )

        assert result.exit_code == 0

        with tiledb.open(uri) as array:
            print(array[:])

    def test_sparse(self, temp_rootdir):
        """
        Test for command

            tiledb convert_from [csv_file] [uri] --sparse
        """
        test_name = "simple"
        input_path = os.path.join(temp_rootdir, f"{test_name}.csv")
        uri = os.path.join(temp_rootdir, "test_sparse.tdb")

        runner = CliRunner()
        result = runner.invoke(
            root,
            ["convert-from", "csv", input_path, uri, "--sparse"],
        )

        assert result.exit_code == 0

        with tiledb.open(uri) as array:
            assert array.schema.sparse == True

    def test_dense(self, temp_rootdir):
        """
        Test for command

            tiledb convert_from [csv_file] [uri] --dense
        """
        test_name = "simple"
        input_path = os.path.join(temp_rootdir, f"{test_name}.csv")
        uri = os.path.join(temp_rootdir, "test_dense.tdb")

        runner = CliRunner()
        result = runner.invoke(
            root,
            ["convert-from", "csv", input_path, uri, "--dense"],
        )

        assert result.exit_code == 0

        with tiledb.open(uri) as array:
            assert array.schema.sparse == False

    def test_allows_duplicates(self, temp_rootdir):
        """
        Test for command

            tiledb convert_from [csv_file] [uri] --allows-duplicates
        """
        test_name = "simple"
        input_path = os.path.join(temp_rootdir, f"{test_name}.csv")
        uri = os.path.join(temp_rootdir, "test_allows_duplicates.tdb")

        runner = CliRunner()
        result = runner.invoke(
            root,
            ["convert-from", "csv", input_path, uri, "--allows-duplicates"],
        )

        assert result.exit_code == 0

    def test_capacity(self, temp_rootdir):
        """
        Test for command

            tiledb convert_from [csv_file] [uri] -n <int>
        """
        test_name = "simple"
        input_path = os.path.join(temp_rootdir, f"{test_name}.csv")
        uri = os.path.join(temp_rootdir, "test_capacity.tdb")

        runner = CliRunner()
        result = runner.invoke(
            root,
            ["convert-from", "csv", input_path, uri, "-n", 1],
        )

        assert result.exit_code == 0

    def test_cell_order(self, temp_rootdir):
        """
        Test for command

            tiledb convert_from [csv_file] [uri] -c (row-major | column-major | global)
        """
        test_name = "simple"
        input_path = os.path.join(temp_rootdir, f"{test_name}.csv")
        uri = os.path.join(temp_rootdir, "test_cell_order.tdb")

        runner = CliRunner()
        result = runner.invoke(
            root,
            ["convert-from", "csv", input_path, uri, "-c", "global"],
        )

        assert result.exit_code == 0

    def test_full_domain(self, temp_rootdir):
        """
        Test for command

            tiledb convert_from [csv_file] [uri] --full-domain
        """
        test_name = "simple"
        input_path = os.path.join(temp_rootdir, f"{test_name}.csv")
        uri = os.path.join(temp_rootdir, "test_full_domain.tdb")

        runner = CliRunner()
        result = runner.invoke(
            root,
            ["convert-from", "csv", input_path, uri, "--full-domain"],
        )

        assert result.exit_code == 0

    def test_date_spec(self, temp_rootdir):
        """
        Test for command

            tiledb convert_from [csv_file] [uri] --date-spec <column> <datetime format spec>
        """
        test_name = "simple"
        input_path = os.path.join(temp_rootdir, f"{test_name}.csv")
        uri = os.path.join(temp_rootdir, "test_date_spec.tdb")

        runner = CliRunner()
        result = runner.invoke(
            root,
            ["convert-from", "csv", input_path, uri, "-d", "date", "%b/%d/%Y"],
        )

        assert result.exit_code == 0

    def test_mode(self, temp_rootdir):
        """
        Test for command

            tiledb convert_from [csv_file] [uri] -m (ingest | schema_only | append)
        """
        test_name = "simple"
        input_path = os.path.join(temp_rootdir, f"{test_name}.csv")
        uri = os.path.join(temp_rootdir, "test_mode.tdb")

        runner = CliRunner()
        result = runner.invoke(
            root,
            ["convert-from", "csv", input_path, uri, "-m", "schema_only"],
        )

        assert result.exit_code == 0

    def test_row_start_idx(self, temp_rootdir):
        """
        Test for command

            tiledb convert_from [csv_file] [uri] -r <int>
        """
        test_name = "simple"
        input_path = os.path.join(temp_rootdir, f"{test_name}.csv")
        uri = os.path.join(temp_rootdir, "test_row_start_idx.tdb")

        runner = CliRunner()
        result = runner.invoke(
            root,
            ["convert-from", "csv", input_path, uri, "-r", 5],
        )

        assert result.exit_code == 0

    def test_row_order(self, temp_rootdir):
        """
        Test for command

            tiledb convert_from [csv_file] [uri] -c (row-major | column-major | global)
        """
        test_name = "simple"
        input_path = os.path.join(temp_rootdir, f"{test_name}.csv")
        uri = os.path.join(temp_rootdir, "test_row_order.tdb")

        runner = CliRunner()
        result = runner.invoke(
            root,
            ["convert-from", "csv", input_path, uri, "-c", "global"],
        )

        assert result.exit_code == 0

    def test_tile_int(self, temp_rootdir):
        """
        Test for command

            tiledb convert_from [csv_file] [uri] -T <int>
        """
        test_name = "simple"
        input_path = os.path.join(temp_rootdir, f"{test_name}.csv")
        uri = os.path.join(temp_rootdir, "test_tile_int.tdb")

        runner = CliRunner()
        result = runner.invoke(
            root,
            ["convert-from", "csv", input_path, uri, "-T", 3],
        )

        assert result.exit_code == 0

    def test_tile_column_name(self, temp_rootdir):
        """
        Test for command

            tiledb convert_from [csv_file] [uri] -T <column name> <int>
        """
        test_name = "simple"
        input_path = os.path.join(temp_rootdir, f"{test_name}.csv")
        uri = os.path.join(temp_rootdir, "test_tile_column_name.tdb")

        runner = CliRunner()
        result = runner.invoke(
            root,
            ["convert-from", "csv", input_path, uri, "-T", "a:3", "-T", "b:2"],
        )

        assert result.exit_code == 0

    def test_timestamp(self, temp_rootdir):
        """
        Test for command

            tiledb convert_from [csv_file] [uri] -u <int>
        """
        test_name = "simple"
        input_path = os.path.join(temp_rootdir, f"{test_name}.csv")
        uri = os.path.join(temp_rootdir, "test_timestamp.tdb")

        runner = CliRunner()
        result = runner.invoke(
            root,
            ["convert-from", "csv", input_path, uri, "-u", 3],
        )

        assert result.exit_code == 0

    def test_attr_filters(self, temp_rootdir):
        """
        Test for command

            tiledb convert_from [csv_file] [uri] -A <filter name>,<filter name>,...
        """
        test_name = "simple"
        input_path = os.path.join(temp_rootdir, f"{test_name}.csv")
        uri = os.path.join(temp_rootdir, "test_attr_filters.tdb")

        runner = CliRunner()
        result = runner.invoke(
            root, ["convert-from", "csv", input_path, uri, "-A", "GzipFilter=9"]
        )
        assert result.exit_code == 0

    def test_attr_filters_multi(self, temp_rootdir):
        """
        Test for command

            tiledb convert_from [csv_file] [uri] -A <attr name>:<filter name>,<filter name>,...
        """
        test_name = "simple"
        input_path = os.path.join(temp_rootdir, f"{test_name}.csv")
        uri = os.path.join(temp_rootdir, "test_attr_filters_multi.tdb")

        runner = CliRunner()
        result = runner.invoke(
            root,
            [
                "convert-from",
                "csv",
                input_path,
                uri,
                "-A",
                "a:LZ4Filter=10,BitShuffleFilter",
                "-A",
                "b:DoubleDeltaFilter,PositiveDeltaFilter=3",
            ],
        )
        assert result.exit_code == 0

    def test_dim_filters(self, temp_rootdir):
        """
        Test for command

            tiledb convert_from [csv_file] [uri] -D <filter name>,<filter name>,...
        """
        test_name = "simple"
        input_path = os.path.join(temp_rootdir, f"{test_name}.csv")
        uri = os.path.join(temp_rootdir, "test_dim_filters.tdb")

        runner = CliRunner()
        result = runner.invoke(
            root, ["convert-from", "csv", input_path, uri, "-D", "GzipFilter=9"]
        )
        assert result.exit_code == 0

    def test_dim_filters_multi(self, temp_rootdir):
        """
        Test for command

            tiledb convert_from [csv_file] [uri] -D <dim name>:<filter name>,<filter name>,...
        """
        test_name = "simple"
        input_path = os.path.join(temp_rootdir, f"{test_name}.csv")
        uri = os.path.join(temp_rootdir, "test_dim_filters_multi.tdb")

        runner = CliRunner()
        result = runner.invoke(
            root,
            [
                "convert-from",
                "csv",
                input_path,
                uri,
                "-D",
                "a:LZ4Filter=10,BitShuffleFilter",
                "-D",
                "b:DoubleDeltaFilter,PositiveDeltaFilter=3",
            ],
        )
        assert result.exit_code == 0

    def test_coords_filters(self, temp_rootdir):
        """
        Test for command

            tiledb convert_from [csv_file] [uri] -C <filter name>,<filter name>,...
        """
        test_name = "simple"
        input_path = os.path.join(temp_rootdir, f"{test_name}.csv")
        uri = os.path.join(temp_rootdir, "test_coords_filters.tdb")

        runner = CliRunner()
        result = runner.invoke(
            root, ["convert-from", "csv", input_path, uri, "-C", "GzipFilter=9"]
        )
        assert result.exit_code == 0
