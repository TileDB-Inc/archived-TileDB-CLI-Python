import click

from .cloud import cloud
from .convert_from import convert_from
from .dump import dump


@click.group()
def root():
    pass


root.add_command(cloud)
root.add_command(convert_from)
root.add_command(dump)
