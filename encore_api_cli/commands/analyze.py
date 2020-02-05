import io
from typing import Optional

import click
from yaspin import yaspin

from ..options import common_options
from ..output import echo, echo_success
from ..state import State, pass_state
from ..utils import color_id, get_client, parse_rule
from .analysis import show


@click.group()
def cli() -> None:  # noqa: D103
    pass


@cli.command()
@click.argument("keypoint_id", type=int)
@click.option("--rule", "rule_str", help="Analysis rules in JSON format.")
@click.option(
    "--rule-file", type=click.File(), help="Analysis rules file in JSON format."
)
@click.option("--show-result", is_flag=True)
@common_options
@pass_state
@click.pass_context
def analyze(
    ctx: click.Context,
    state: State,
    keypoint_id: int,
    rule_str: Optional[str],
    rule_file: Optional[io.TextIOWrapper],
    show_result: bool,
) -> None:
    """Analyze the extracted keypoint data."""
    if rule_str is not None and rule_file is not None:
        raise click.UsageError(
            '"rule" and "rule-file" options cannot be used at the same time.'
        )
    if rule_str is None and rule_file is None:
        raise click.UsageError('Either "rule" or "rule-file" options is required.')

    rule = None
    if rule_str is not None:
        rule = parse_rule(rule_str)
    elif rule_file is not None:
        rule = parse_rule(rule_file.read())

    if rule is None:
        raise

    client = get_client(state)
    analysis_id = client.analyze_keypoint(keypoint_id, rule)

    echo(f"Analysis started. (analysis id: {color_id(analysis_id)})")
    if state.use_spinner:
        with yaspin(text="Processing..."):
            response = client.wait_for_analysis(analysis_id)
    else:
        response = client.wait_for_analysis(analysis_id)

    if response.status == "SUCCESS":
        echo_success("Analysis is complete.")
        if show_result:
            ctx.invoke(show, analysis_id=analysis_id)
    elif response.status == "TIMEOUT":
        echo("Analysis is timed out.")
    else:
        echo(f"Analysis failed: {response.failure_detail}")
