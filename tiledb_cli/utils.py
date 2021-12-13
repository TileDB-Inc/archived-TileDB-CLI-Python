import iso8601
import time


def to_unix_time(datestr: str) -> int:
    """Convert a string representing ISO 8601 or UNIX seconds to an int
    representing UNIX seconds.

    Args:
        timestamp (str): ISO 8601 or UNIX seconds

    Returns:
        int: UNIX seconds
    """
    if datestr.isdigit():
        timestamp = int(datestr)
    else:
        timestamp = int(iso8601.parse_date(datestr).timestamp())

    return timestamp
