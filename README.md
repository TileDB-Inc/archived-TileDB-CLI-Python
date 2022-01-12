# TileDB-CLI

TileDB-CLI is a hierarchical command-line interface to the TileDB Storage Engine.

## Installation

TileDB-CLI can be installed using `pip` with:

```bash
pip install tiledb-cli
```

For development mode, in the top level directory run:

```bash
pip install .[dev]
```

This will create `tiledb` (in `/usr/local/bin`, or other paths specific to `venv` or `conda` if you are using those), which you can run.

## Commands

All commands begin with `tiledb` and are grouped into the following subgroups:
* [cloud](#cloud): Perform TileDB Cloud tasks.
* [convert_from](#convert_from): Convert to and from TileDB arrays and other common file formats.
* [consolidate](#consolidate): Consolidate TileDB array fragments, fragment metadata, or and array metadata.
* [dump](#dump): Output information about TileDB arrays.
* [fragments](#fragments): Perform various tasks on TileDB array fragments.
* [vacuum](#vacuum): Vacuum TileDB array fragments, fragment metadata, or and array metadata that have already been consolidated.

### cloud
* array
    * register: Register an array to the TileDB cloud service.
    * deregister: Deregister an array to the TileDB cloud service. This does not physically delete the array. It will remain in your bucket. All access to the array and could metadata will be removed.
    * share: Share the TileDB array to the user at a given namespace. At least one of the persmission flags must be supplied.
    * unshare: Revokes access to a TileDB array for the user at a given namespace.
* dump
    * activity: Dump the array activity of an array located at a TileDB uri.
    * arrays: List array properties and their associated values for arrays in a TileDB user account.
    * orgs: List organization properties and their associated values for each organization a TileDB user account is a part of.
    * profile: Output the current logged in namespace's profile information.
    * task: List last task from TileDB cloud.
* login: Login into TileDB cloud under a given credential using either a token or username. By default, credential is read from the environmental variable `TILEDB_REST_TOKEN`.
* retry-task  Retry running the task with the given id.
### convert_from
* csv: Convert a csv_file into a TileDB array.
### consolidate
* array-metadata: Consolidate the array metadata in an array.
* fragment-metadata: Consolidate the fragments in an array.
* fragments: Consolidate the fragments in an array.
### dump
* array: Output the data of a TileDB array.
* config: Output TileDB's default configuration parameters and values.
* fragments: Output the fragment information of a TileDB array.
* mbrs: Output the minimum bounding rectangle for a sparse TileDB array.
* metadata: Output the metadata of a TileDB array.
* nonempty-domain`: Output the non-empty domain of a TileDB array.
* schema: Output the schema of a TileDB array.
* versions: Output the version information for the embedded library and Python package.
### fragments
* copy: Copy a range of fragments from an already existing array to another array.
* delete: Delete a range of fragments from an array.
### vacuum
* array-metadata: Vacuum the already consolidated array metadata in an array.
* fragment-metadata: Vacuum the already consolidated fragments in an array.
* fragments: Vacuum the already consolidated fragments in an array.

## Basic Usage
Create an array from a CSV file.
```
> cat example.csv
a,b
1,dog
2,cat
8,bird
20,elephant
> tiledb convert-from csv example.csv example.tdb
```

Output the array's schema.
```
> tiledb dump schema example.tdb
ArraySchema(
  domain=Domain(*[
    Dim(name='__tiledb_rows', domain=(0, 3), tile='3', dtype='uint64'),
  ]),
  attrs=[
    Attr(name='a', dtype='int64', var=False, nullable=False),
    Attr(name='b', dtype='<U0', var=True, nullable=False),
  ],
  cell_order='row-major',
  tile_order='row-major',
  capacity=10000,
  sparse=False,
)
```

Output data from the array.
```
> tiledb dump array example.tdb 0:4
OrderedDict([('__tiledb_rows', array([0, 1, 2, 3], dtype=uint64)),
             ('a', array([ 1,  2,  8, 20])),
             ('b', array(['dog', 'cat', 'bird', 'elephant'], dtype=object))])
```
