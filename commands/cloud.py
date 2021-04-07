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
    metavar="<str>",
    help=("Optional page for pagination"),
    default=None,
)
@click.option(
    "--per-page",
    "-n",
    metavar="<str>",
    help=("Optional per_page for pagination"),
    default=None,
)
@click.option(
    "--async-req/--no-async-req",
    help=("Return future instead of results for async support"),
    default=False,
    show_default=True,
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
    async_req,
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
        array_browser_data = tiledb.cloud.client.list_arrays(**kwargs)
    elif type_ == "public":
        array_browser_data = tiledb.cloud.client.list_public_arrays(**kwargs)
    elif type_ == "shared":
        array_browser_data = tiledb.cloud.client.list_shared_arrays(**kwargs)

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
    "--async-req/--no-async-req",
    help=("Return future instead of results for async support"),
    default=False,
    show_default=True,
)
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
def orgs(async_req, name, property_):
    """
    List organization properties and their associated values for each
    organization a TileDB user account is a part of.
    """
    if not name:
        all_orgs = tiledb.cloud.client.organizations(async_req=async_req)
    else:
        all_orgs = [
            tiledb.cloud.client.organization(n, async_req=async_req) for n in name
        ]

    if not property_:
        click.echo(all_orgs)
    else:
        pp = pprint.PrettyPrinter()
        for o in all_orgs:
            click.echo(
                pp.pformat({k: v for k, v in o.to_dict().items() if k in property_})
            )


cloud.add_command(login)
cloud.add_command(dump)
dump.add_command(arrays)
dump.add_command(orgs)
