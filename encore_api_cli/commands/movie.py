import click

from encore_api_cli.options import common_options
from encore_api_cli.state import pass_state
from encore_api_cli.utils import get_client


@click.group()
def cli() -> None:  # noqa: D103
    pass


@cli.group()
def movie():
    """Manege movies."""
    pass


@movie.command()
@common_options
@pass_state
def list(state):
    """Show movie list."""
    c = get_client(state)
    c.show_list("movies")
