import click

from encore_api_cli.client import Client
from encore_api_cli.settings import Settings


def get_client(profile):
    settings = Settings(profile)
    if not settings.is_ok():
        message = ' '.join([
            'The credentials is invalid or not set.',
            'Run "encore configure" to set credentials.'
        ])
        raise click.ClickException(message)
    return Client(settings.client_id, settings.client_secret, settings.url)
