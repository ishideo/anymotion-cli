import click

from ..config import Config


@click.group()
def cli():
    pass


@cli.group(invoke_without_command=True)
@click.option('--profile',
              default='default',
              help='Name of a named profile that you can configure.')
@click.pass_context
def configure(ctx, profile):
    """Configure your AnyMotion Access Token."""
    if ctx.invoked_subcommand is None:
        config = Config(profile)
        config.url = click.prompt('AnyMotion API URL', default=config.url)
        config.token = click.prompt('AnyMotion Access Token',
                                    default=config.token)
        config.update()


@configure.command()
def list():
    """Show the configuration you set."""
    config = Config()
    config.show()