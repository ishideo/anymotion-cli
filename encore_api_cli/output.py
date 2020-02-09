import json
import sys
from typing import Optional

import click
import requests
from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import JsonLexer


def echo(message: Optional[str] = None) -> None:
    """Output message."""
    if is_show():
        click.echo(message)


def echo_success(message: str) -> None:
    """Output success message."""
    if is_show():
        click.echo(f"{click.style('Success', fg='green')}: {message}")


def echo_warning(message: str) -> None:
    """Output warning message."""
    click.echo(f"{click.style('Warning', fg='yellow')}: {message}", err=True)


def echo_error(message: str) -> None:
    """Output error message."""
    click.echo(f"{click.style('Error', fg='red')}: {message}", err=True)


def echo_json(data: object, sort_keys: bool = False, pager: bool = False) -> None:
    """Output json data."""
    if is_show():
        click.echo()

    body = json.dumps(data, sort_keys=sort_keys, indent=2)
    body = highlight(body, JsonLexer(), TerminalFormatter())

    if pager:
        click.echo_via_pager(body)
    else:
        click.echo(body)


def echo_request(request: requests.Request) -> None:
    """Output http request.

    Examples:
        POST http://example.com
        Content-Type: application/json

        {
            "key": "value"
        }
    """
    url = click.style(request.url, fg="cyan")
    method = click.style(request.method, fg="green")
    click.echo(f"{method} {url}")

    if request.headers is not None:
        for key, value in request.headers.items():
            key = click.style(key, fg="cyan")
            click.echo(f"{key}: {value}")

    if request.json is not None:
        echo_json(request.json)

    click.echo()


def echo_response(response: requests.Response) -> None:
    """Output http response.

    Examples:
        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "id": 1
        }
    """
    status = click.style(str(response.status_code), fg="blue")
    reason = click.style(response.reason, fg="cyan")
    http_version = "HTTP"
    if response.raw.version == 10:
        http_version = "HTTP/1.0"
    elif response.raw.version == 11:
        http_version = "HTTP/1.1"
    http_version = click.style(http_version, fg="blue")
    click.echo(f"{http_version} {status} {reason}")

    if response.headers is not None:
        for key, value in response.headers.items():
            key = click.style(key, fg="cyan")
            click.echo(f"{key}: {value}")

    json = response.json()
    if json is not None:
        echo_json(json)

    click.echo()
    click.echo()


def is_show() -> bool:
    """Flag to show.

    It is True for terminals and False for pipes.
    If an environment variable has been set, its value is returned.
    """
    from encore_api_cli.utils import get_bool_env

    return get_bool_env("ANYMOTION_STDOUT_ISSHOW", sys.stdout.isatty())
