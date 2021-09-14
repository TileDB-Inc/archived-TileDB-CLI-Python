import tiledb
import tiledb.cloud
from common import test_array_names
from commands.root import root

import os
import pytest


@pytest.fixture(autouse=True, scope="session")
def tiledb_cloud_login():
    """
    The TILEDB_REST_TOKEN for accessing the unittest TileDB Cloud namespace must
    be set by the user.
    """
    tiledb.cloud.login(token=os.environ["TILEDB_REST_TOKEN"])


@pytest.fixture(scope="session")
def key():
    """
    The AWS_ACCESS_KEY_ID environment variable for accessing the unittest
    S3 Bucket must be set by the user.
    """
    return os.environ["AWS_ACCESS_KEY_ID"]


@pytest.fixture(scope="session")
def secret():
    """
    The AWS_SECRET_ACCESS_KEY environment variable for accessing the unittest
    S3 Bucket must be set by the user.
    """
    return os.environ["AWS_SECRET_ACCESS_KEY"]


@pytest.fixture(scope="session")
def namespace():
    return "unittest"


@pytest.fixture(scope="session")
def bucket():
    return "tiledb-unittest"


class TestDump:
    @pytest.mark.parametrize("array_name", test_array_names)
    def test_activity(self, runner, namespace, array_name):
        """
        Test for command

            tiledb cloud dump activity <uri>
        """
        uri = f"tiledb://{namespace}/{array_name}"
        result = runner.invoke(root, ["cloud", "dump", "activity", uri])
        assert result.exit_code == 0

    def test_arrays(self, runner):
        """
        Test for command

            tiledb cloud dump arrays
        """
        result = runner.invoke(root, ["cloud", "dump", "arrays", "-P", "name"])
        assert result.exit_code == 0

        expected_array_names = [
            "sparse_25x12",
            "sparse_25x12_mult",
            "dense_25x12x3",
            "dense_25x12_mult",
            "dense_25x12",
        ]
        retrieved_array_names = []
        for idx, elem in enumerate(result.stdout.split()):
            if idx % 2 == 1:
                retrieved_array_names.append(elem[1:-2])

        assert set(expected_array_names).issubset(set(retrieved_array_names))

    def test_orgs(self, runner):
        """
        Test for command

            tiledb cloud dump orgs
        """
        result = runner.invoke(root, ["cloud", "dump", "orgs"])
        assert result.exit_code == 0

    def test_profile(self, runner):
        """
        Test for command

            tiledb cloud dump profile
        """
        result = runner.invoke(
            root,
            ["cloud", "dump", "profile", "-P", "default_s3_path", "-P", "username"],
        )
        assert result.exit_code == 0

        expected_values = ["s3://tiledb-unittest/", "unittest"]
        retrieved_values = []
        for idx, elem in enumerate(result.stdout.split()):
            if idx % 2 == 1:
                retrieved_values.append(elem[1:-2])

        assert expected_values == retrieved_values

    def test_task(self, runner):
        """
        Test for command

            tiledb cloud dump task
        """
        result = runner.invoke(root, ["cloud", "dump", "task"])
        assert result.exit_code == 0
