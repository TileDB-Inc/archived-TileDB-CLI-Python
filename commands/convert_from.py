import tiledb

import click

@click.group()
def convert_from():
    pass


@click.command()
@click.argument("csv_file")
@click.argument("uri")
def csv(csv_file, uri):
    tiledb.from_csv(uri, csv_file)


convert_from.add_command(csv)