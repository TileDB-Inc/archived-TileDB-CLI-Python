import tiledb
import tiledb.cloud

import click
import os


@click.group()
def cloud():
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
    kwargs = dict()

    if token:
        kwargs["token"] = credential
    else:
        kwargs["username"] = credential
        kwargs["password"] = password

    kwargs["host"] = host
    kwargs["verify_ssl"] = verify_ssl
    kwargs["no_session"] = no_session
    kwargs["threads"] = threads

    tiledb.cloud.login(**kwargs)


cloud.add_command(login)
