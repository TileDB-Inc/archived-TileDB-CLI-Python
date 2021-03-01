import tiledb
from common import test_array_names
from dump import root

from click.testing import CliRunner
import os
import pytest


def test_dump_config():
    """
    Test for command

        tiledb dump config
    """
    runner = CliRunner()
    result = runner.invoke(root, ["dump", "config"])
    assert result.exit_code == 0
    assert result.stdout.split() == tiledb.Config().__repr__().split()


@pytest.mark.parametrize("array_name", test_array_names)
def test_dump_metadata(temp_rootdir, array_name, pp):
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


@pytest.mark.parametrize("array_name", test_array_names)
def test_dump_nonempty_domain(temp_rootdir, array_name, pp):
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


@pytest.mark.parametrize("array_name", test_array_names)
def test_dump_schema(temp_rootdir, array_name, pp):
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


@pytest.mark.parametrize("array_name", test_array_names)
def test_dump_array(temp_rootdir, array_name):
    """
    Test for command

        tiledb dump array [array_uri]
    """
    uri = os.path.abspath(os.path.join(temp_rootdir, array_name))

    runner = CliRunner()
    result = runner.invoke(root, ["dump", "array", uri])
    assert result.exit_code == 0


@pytest.mark.parametrize("array_name", test_array_names)
def test_dump_fragments(temp_rootdir, array_name):
    """
    Test for command

        tiledb dump fragments [array_uri]
    """
    uri = os.path.abspath(os.path.join(temp_rootdir, array_name))

    runner = CliRunner()
    result = runner.invoke(root, ["dump", "fragments", uri])
    assert result.exit_code == 0