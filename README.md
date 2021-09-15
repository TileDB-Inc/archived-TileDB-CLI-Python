# TileDB-CLI

TileDB-CLI is a heirachal CLI interface to the TileDB Storage Engine.

## Installation

TileDB can be installed using `pip` with:

```bash
pip install tiledb-cli
```

For development mode, in the top level directory run:

```bash
pip install .[dev]
```

This will create `tiledb` (in `/usr/local/bin`, or other paths specific to `venv` or `conda` if you are using those), which you can run.

## Commands

All commands begin with `tiledb` and are grouped into the follow command subgroups:
* [cloud](#cloud): Perform TileDB Cloud tasks.
* [convert_from](#convert_from): Convert to and from TileDB arrays and other common file formats.
* [consolidate](#consolidate): Consolidate TileDB array fragments.
* [dump](#dump): Output information about TileDB arrays.
* [vacuum](#vacuum): Vacuum TileDB array fragments that have already been consolidated.

### cloud
* array
    * register: Register an array located at uri to the TileDB cloud service.
    * deregister: Deregister an array located at uri to the TileDB cloud service. This does not physically delete the array. It will remain in your bucket. All access to the array and could metadata will be removed.
    * share: Share the TileDB array located at uri to the user at a given namespace. At least one of the persmission flags must be supplied.
    * unshare: Revokes access to a TileDB array located at uri for the user at a given namespace.
* dump
    * activity: Dump the array activity of an array located at a TileDB uri.
    * arrays: List array properties and their associated values for arrays in a TileDB user account.
    * orgs: List organization properties and their associated values for each organization a TileDB user account is a part of.
    * profile: Output the current logged in namespace's profile information.
    * task: List last task from TileDB cloud.
* login: Login into TileDB cloud under a given credential using either a token or username. By default, credential is read from the environmental variable `TILEDB_REST_TOKEN`.
* retry-task  Retry running the task with the given id.
### convert_from
* csv: Convert a csv_file into a TileDB array located at uri.
### consolidate
* array-metadata: Consolidate the array metadata in an array located at uri.
* fragment-metadata: Consolidate the fragments in an array located at uri.
* fragments: Consolidate the fragments in an array located at uri.
### dump
* array: Output the data of a TileDB array located at uri.
* config: Output TileDB's default configuration parameters and values.
* fragments: Output the fragment information of a TileDB array located at uri.
* metadata: Output the metadata of a TileDB array located at uri.
* nonemptydomain`: Output the non-empty domain of a TileDB array located at uri.
* schema: Output the schema of a TileDB array located at uri.
### vacuum
* array-metadata: Vacuum the already consolidated array metadata in an array located at uri.
* fragment-metadata: Vacuum the already consolidated fragments in an array located at uri.
* fragments: Vacuum the already consolidated fragments in an array located at uri.