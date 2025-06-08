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
    "formatter",
    type=str,
    help="Path to the formatter configuration file."
)
def generate(source: str, formatter: str):
    generate_documentation(source_filepath=source, formatter_filepath=formatter)
