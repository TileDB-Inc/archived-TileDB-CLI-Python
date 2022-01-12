import click
import iso8601
import sys
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


def prompt_poweruser():
    poweruser_statement = (
        "This is a power command intended for advanced users only. Enter yes "
        "to acknowledge this statement and continue or no to abort. Pass the "
        "--force/-f flag to bypass this prompt in the future."
    )

    if not click.confirm(poweruser_statement, default="no"):
        sys.exit()
