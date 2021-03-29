import click

from .dump import dump
from .convert_from import convert_from


@click.group()
def root():
    pass


root.add_command(dump)
root.add_command(convert_from)
