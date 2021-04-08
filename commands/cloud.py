import tiledb
import tiledb.cloud

import click
import os
import pprint


@click.group()
def cloud():
    pass


@click.group()
def dump():
    pass


@click.group()
def array():
    pass


def PromptPasswordIfUsername():
    """
    Referenced from answer here: https://stackoverflow.com/a/49603426
    """

    class prompt_password(click.Option):
        def handle_parse_result(self, ctx, opts, args):
            if "token" not in opts or opts["token"] != False:
                self.prompt = None

            return super(prompt_password, self).handle_parse_result(ctx, opts, args)

    return prompt_password


@click.command()
@click.argument("credential", default=lambda: os.environ.get("TILEDB_REST_TOKEN", ""))
@click.option(
    "--token/--username",
    "-t/-u",
    help=(
        "The provided credential may be the TileDB cloud token or username. "
        "By default, --token is used, and the credential is interpreted as "
        "a token. If using the --username flag, the credential will be "
        "interpreted as a username, and the user will be prompted to provide "
        "the password"
    ),
    default=True,
)
@click.password_option(
    confirmation_prompt=False, hidden=True, cls=PromptPasswordIfUsername()
)
@click.option(
    "--host",
    "-h",
    metavar="<name>",
    help=("Host to login to"),
    default=None,
)
@click.option(
    "--verify-ssl/--no-verify-ssl",
    help=("Enable strict SSL verification"),
    show_default=True,
    default=True,
)
@click.option(
    "--no-session/--session",
    help=("Don't create a session token on login. Store instead username/password"),
    show_default=True,
    default=False,
)
@click.option(
    "--threads",
    "-t",
    metavar="<int>",
    help=("Number of threads to enable for concurrent requests"),
    show_default=True,
    type=int,
    default=16,
)
def login(credential, token, password, host, verify_ssl, no_session, threads):
    """
    Login into TileDB cloud under a given credential using either a token or username.
    By default, credential is read from the environmental variable TILEDB_REST_TOKEN.
    """
    kwargs = locals()

    del kwargs["credential"]

    if token:
        kwargs["token"] = credential
    else:
        kwargs["username"] = credential
        kwargs["password"] = password

    tiledb.cloud.login(**kwargs)


@click.command()
@click.option(
    "--namespace",
    "-n",
    metavar="<str>",
    help=("List arrays in single namespace"),
    default=None,
)
@click.option(
    "--permissions",
    "-p",
    metavar="<str>",
    help=("Permissions to include"),
    default=None,
)
@click.option(
    "--tag",
    "-t",
    metavar="<str>",
    help=("Tags to include"),
    default=None,
)
@click.option(
    "--exclude-tag",
    "-e",
    metavar="<str>",
    help=("Tags to exclude"),
    default=None,
)
@click.option(
    "--search",
    "-s",
    metavar="<str>",
    help=("Search string is applied to values"),
    default=None,
)
@click.option(
    "--file-type",
    "-f",
    metavar="<str>",
    help=("file_types to include"),
    default=None,
)
@click.option(
    "--exclude-file-type",
    "-e",
    metavar="<str>",
    help=("file_types to exclude"),
    default=None,
)
@click.option(
    "--page",
    "-p",
    metavar="<int>",
    help=("Optional page for pagination"),
    default=None,
)
@click.option(
    "--per-page",
    "-n",
    metavar="<int>",
    help=("Optional per_page for pagination"),
    default=None,
)
@click.option(
    "--type",
    "-t",
    "type_",
    help=(
        "Owned arrays are all arrays owned by the user and organization they "
        "are a part of.\n"
        "\n"
        "Public arrays are arrays that live under the 'public' "
        "organization and are discoverable by every user on TileDB cloud. For "
        "more details see: https://docs.tiledb.com/cloud/console/arrays/public-arrays\n"
        "\n"
        "Shared arrays are arrays that have been shared with the user. For more "
        "details see: https://docs.tiledb.com/cloud/console/arrays/sharing-arrays"
    ),
    type=click.Choice(["owned", "public", "shared"], case_sensitive=False),
    show_default=True,
    default="owned",
)
@click.option(
    "--property",
    "-P",
    "property_",
    help=(
        "By default, output all properties from the arrays. Pass in the flag "
        "multiple times to retrieve multiple properties. "
        "Example: tiledb dump arrays -P name -P tiledb_uri"
    ),
    type=click.Choice(
        [
            "access_credentials_name",
            "allowed_actions",
            "file_properties",
            "file_type",
            "id",
            "last_accessed",
            "license_id",
            "license_text",
            "logo",
            "name",
            "namespace",
            "namespace_subscribed",
            "pricing",
            "public_share",
            "share_count",
            "size",
            "subscriptions",
            "tags",
            "tiledb_uri",
            "type",
            "uri",
        ]
    ),
    multiple=True,
    default=(),
)
def arrays(
    namespace,
    permissions,
    tag,
    exclude_tag,
    search,
    file_type,
    exclude_file_type,
    page,
    per_page,
    type_,
    property_,
):
    """
    List array properties and their associated values for arrays in a TileDB
    user account.
    """

    kwargs = locals()

    del kwargs["type_"]
    del kwargs["property_"]

    if type_ == "owned":
        array_browser_data = tiledb.cloud.list_arrays(**kwargs)
    elif type_ == "public":
        array_browser_data = tiledb.cloud.list_public_arrays(**kwargs)
    elif type_ == "shared":
        array_browser_data = tiledb.cloud.list_shared_arrays(**kwargs)

    all_arrays = array_browser_data.to_dict()["arrays"]

    if all_arrays:
        pp = pprint.PrettyPrinter()
        if not property_:
            click.echo(pp.pformat(all_arrays))
        else:
            for a in all_arrays:
                click.echo(pp.pformat({k: v for k, v in a.items() if k in property_}))


@click.command()
@click.option(
    "--name",
    "-n",
    help=(
        "List out properties for certain organization(s). By default, all "
        "organizations a user belongs to are listed. Pass the flag multiple "
        "times to retrieve multiple organizations. "
        "Example: tiledb dump orgs -n org1 -n org2"
    ),
    type=str,
    multiple=True,
    default=(),
)
@click.option(
    "--property",
    "-P",
    "property_",
    help=(
        "By default, output all properties from the organization. Pass the flag "
        "multiple times to retrieve multiple properties. "
        "Example: tiledb dump orgs -P name -P num_of_arrays"
    ),
    type=click.Choice(
        [
            "id",
            "role",
            "name",
            "created_at",
            "updated_at",
            "logo",
            "description",
            "users",
            "allowed_actions",
            "num_of_arrays",
            "enabled_features",
            "unpaid_subscription",
            "default_s3_path",
            "default_s3_path_credentials_name",
            "stripe_connect",
        ]
    ),
    multiple=True,
    default=(),
)
def orgs(name, property_):
    """
    List organization properties and their associated values for each
    organization a TileDB user account is a part of.
    """
    if not name:
        all_orgs = tiledb.cloud.client.organizations()
    else:
        all_orgs = [
            tiledb.cloud.client.organization(
                n,
            )
            for n in name
        ]

    if not property_:
        click.echo(all_orgs)
    else:
        pp = pprint.PrettyPrinter()
        for o in all_orgs:
            click.echo(
                pp.pformat({k: v for k, v in o.to_dict().items() if k in property_})
            )


@click.command()
@click.option(
    "--property",
    "-P",
    "property_",
    help=(
        "By default, output all properties from the user profile. Pass the flag "
        "multiple times to retrieve multiple properties. "
        "Example: tiledb dump profile -P company -P email"
    ),
    type=click.Choice(
        [
            "id",
            "username",
            "password",
            "name",
            "email",
            "is_valid_email",
            "stripe_connect",
            "company",
            "logo",
            "last_activity_date",
            "timezone",
            "organizations",
            "allowed_actions",
            "enabled_features",
            "unpaid_subscription",
            "default_s3_path",
            "default_s3_path_credentials_name",
            "default_namespace_charged",
        ]
    ),
    multiple=True,
    default=(),
)
def profile(property_):
    """
    Output the current logged in namespace's profile information.
    """
    whole_profile = tiledb.cloud.client.user_profile()

    if not property_:
        click.echo(whole_profile)
    else:
        pp = pprint.PrettyPrinter()
        click.echo(
            pp.pformat(
                {k: v for k, v in whole_profile.to_dict().items() if k in property_}
            )
        )


@click.command()
@click.argument("uri")
@click.option(
    "--last",
    "-n",
    type=int,
    metavar="<int>",
    help=("Limit output to the given number of activities"),
    default=5,
    show_default=True,
)
def activity(uri, last):
    """
    Dump the array activity of an array located at a TileDB uri.
    """
    activity = tiledb.cloud.array_activity(uri)

    pp = pprint.PrettyPrinter()
    click.echo(pp.pformat(activity[:last]))


@click.command(name="task")
@click.option(
    "--last",
    "-n",
    type=int,
    metavar="<int>",
    help=("Extend output to the given number of tasks"),
    default=1,
    show_default=True,
)
@click.option(
    "--namespace",
    "-N",
    type=str,
    metavar="<str>",
    help=("Filter tasks by namespace"),
    default=None,
)
@click.option(
    "--status",
    "-S",
    help=("Filter tasks by status"),
    type=click.Choice(["FAILED", "RUNNING", "COMPLETED"], case_sensitive=False),
    default=None,
)
@click.option(
    "--uri",
    "-u",
    "array",
    type=str,
    metavar="<str>",
    help=("Filter tasks by array at uri"),
    default=None,
)
@click.option(
    "--time-start",
    "-s",
    "start",
    type=int,
    metavar="<int>",
    help=("Upper range of time period to filter"),
    default=None,
)
@click.option(
    "--time-end",
    "-e",
    "end",
    type=int,
    metavar="<int>",
    help=("Lower range of time period to filter"),
    default=None,
)
@click.option(
    "--property",
    "-P",
    "property_",
    help=(
        "By default, output all properties from the task. Pass the flag "
        "multiple times to retrieve multiple properties. Pass none to not "
        "retrieve any properties. This might be useful if you're using one of "
        "the accumulator flags like --cost or --duration and only care about "
        "your total. Passing none will ignore all other passed in properties.\n"
        "Example 1: tiledb cloud dump tasks -P name -P subarray -P start_time\n"
        "Example 2: tiledb cloud dump tasks -c -P none"
    ),
    type=click.Choice(
        [
            "id",
            "name",
            "description",
            "array_metadata",
            "subarray",
            "memory",
            "cpu",
            "namespace",
            "status",
            "start_time",
            "finish_time",
            "cost",
            "egress_cost",
            "access_cost",
            "query_type",
            "udf_code",
            "udf_language",
            "sql_query",
            "type",
            "activity",
            "logs",
            "duration",
            "sql_init_commands",
            "sql_parameters",
            "none",
        ]
    ),
    multiple=True,
    default=(),
)
@click.option(
    "--cost",
    "-c",
    help=("Get the accumulated cost for all retrieved tasks."),
    is_flag=True,
)
@click.option(
    "--duration",
    "-d",
    help=("Get the accumulated duration time for all retrieved tasks."),
    is_flag=True,
)
def dump_task(property_, array, cost, duration, last, namespace, status, start, end):
    """
    List last task from TileDB cloud.
    """
    kwargs = locals()

    del kwargs["cost"]
    del kwargs["duration"]
    del kwargs["last"]
    del kwargs["property_"]

    if kwargs["status"]:
        kwargs["status"].upper()

    tasks = tiledb.cloud.tasks(**kwargs, page=1, per_page=last).to_dict()["array_tasks"]

    if cost:
        click.echo(f"Accumulated cost: {sum([t['cost'] for t in tasks])}")

    if duration:
        click.echo(f"Accumulated duration: {sum([t['duration'] for t in tasks])}")

    if "none" not in property_:
        pp = pprint.PrettyPrinter()
        if not property_:
            click.echo(pp.pformat(tasks))
        else:
            if cost and "cost" not in property_:
                property_.append("cost")

            for t in tasks:
                click.echo(pp.pformat({k: v for k, v in t.items() if k in property_}))


@click.command()
@click.argument("id")
def retry_task(id):
    """
    Retry running the task with the given id.
    """
    click.echo(tiledb.cloud.retry_task(id))


@click.command()
@click.argument("uri")
@click.option(
    "--namespace",
    "-N",
    type=str,
    metavar="<username or organization>",
    help=(
        "Username or organization array should be registered under. Defaults to the user"
    ),
    default=None,
)
@click.option(
    "--array-name",
    "-n",
    type=str,
    metavar="<str>",
    help=("Name of array"),
    default=None,
)
@click.option(
    "--description",
    "-d",
    type=str,
    metavar="<str>",
    help=("Description of array"),
    default=None,
)
@click.option(
    "--credentials",
    "-c",
    "access_credentials_name",
    type=str,
    metavar="<str>",
    help=(
        "Name of access credentials to use. Defaults to the default for given "
        "namespace as set on TileDB cloud"
    ),
    default=None,
)
def register(uri, namespace, array_name, description, access_credentials_name):
    """
    Register an array located at uri to the TileDB cloud service.
    """
    click.echo(tiledb.cloud.register_array(uri, **locals()))


@click.command()
@click.argument("uri")
@click.option(
    "--namespace",
    "-N",
    type=str,
    metavar="<username or organization>",
    help=(
        "Username or organization array should be registered under. Defaults to the user"
    ),
    default=None,
)
def deregister(uri):
    """
    Deregister an array located at uri to the TileDB cloud service. This does not
    physically delete the array. It will remain in your bucket. All access to the
    array and could metadata will be removed.
    """
    click.echo(tiledb.cloud.deregister_array(uri))


@click.command()
@click.argument("uri")
@click.argument("namespace")
@click.option(
    "--read", "-r", help=("Give namespace read permissions to array"), is_flag=True
)
@click.option(
    "--write", "-w", help=("Give namespace write permissions to array"), is_flag=True
)
def share(uri, namespace, read, write):
    """
    Share the TileDB array located at uri to the user at a given namespace. At least
    one of the persmission flags must be supplied.
    """
    permissions = []

    if read:
        permissions.append("read")

    if write:
        permissions.append("write")

    if not permissions:
        raise click.UsageError(f"You must supply one or more persmission flags.")

    tiledb.cloud.share_array(uri, namespace, permissions)


@click.command()
@click.argument("uri")
@click.argument("namespace")
def unshare(uri, namespace):
    """
    Revokes access to a TileDB array located at uri for the user at a given namespace.
    """
    tiledb.cloud.unshare_array(uri, namespace)


cloud.add_command(login)

cloud.add_command(dump)
dump.add_command(arrays)
dump.add_command(orgs)
dump.add_command(profile)
dump.add_command(activity)
dump.add_command(dump_task)

cloud.add_command(retry_task)

cloud.add_command(array)
array.add_command(register)
array.add_command(deregister)
array.add_command(share)
array.add_command(unshare)
