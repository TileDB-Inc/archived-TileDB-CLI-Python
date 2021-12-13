from tiledb_cli.utils import to_unix_time


def test_to_unix_time():
    assert to_unix_time("1970-01-01T00:00:01Z") == 1
    assert to_unix_time("1970-01-01T00:00:02Z") == 2
    assert to_unix_time("1970-01-01T00:00:03Z") == 3
