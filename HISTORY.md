# TileDB-CLI 0.0.2 Release Notes

## Command Changes
* `dump array` refactored to require a selection for each dimension; supports all dtypes [#19](https://github.com/TileDB-Inc/TileDB-CLI/pull/19)
* Addition of `delete-fragments` to remove a time range of fragments from a given array [#21](https://github.com/TileDB-Inc/TileDB-CLI/pull/21)

## Packaging Notes
* Remove NumPy dependency [#16](https://github.com/TileDB-Inc/TileDB-CLI/pull/16)
* Remove TileDB Cloud as a hard dependency [#19](https://github.com/TileDB-Inc/TileDB-CLI/pull/19)
* Bump minimum required version of TileDB-Py to 0.10.5 [#21](https://github.com/TileDB-Inc/TileDB-CLI/pull/21)

# TileDB-CLI 0.0.1 Release Notes

The initial release for the TileDB CLI. 🥳

## Features
* The hierarchical-based CLI is built using [TileDB-Py](https://github.com/TileDB-Inc/TileDB-Py) and [click](https://click.palletsprojects.com/en/8.0.x/) to dump information and perform tasks for [TileDB](https://github.com/TileDB-Inc/TileDB) arrays. For the full listing of commands, see the [README.md](README.md).
