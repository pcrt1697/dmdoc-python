import click

from dmdoc.core.generator import generate_documentation


@click.command()
@click.option(
    "-s",
    "--source",
    "source",
    type=str,
    help="Path to the source configuration file."
)
@click.option(
    "-f",
    "--format",
    "format_",
    type=str,
    help="Path to the format configuration file."
)
def generate(source: str, format_: str):
    generate_documentation(source_filepath=source, format_filepath=format_)
