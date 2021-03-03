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
                "a,b,c\n"
                '1,"text",3.4\n'
                '2,"hello",1.234\n'
                '3,"goodbye",111.232\n'
                '4,"world",123123.12\n'
                '10,"raisins",14.232\n'
            )
        )


class TestCSV:
    def test(self, temp_rootdir):
        """
        Test for command

            tiledb convert_from [csv_file] [uri]
        """
        runner = CliRunner()
        result = runner.invoke(
            root,
            [
                "convert-from",
                "csv",
                os.path.join(temp_rootdir, "simple.csv"),
                os.path.join(temp_rootdir, "simple.tdb"),
            ],
        )

        print(result)
        print(result.stdout)

        assert result.exit_code == 0
