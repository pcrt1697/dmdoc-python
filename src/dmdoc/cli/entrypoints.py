import click

from dmdoc.utils.logging_manager import configure_logging


@click.group(
    context_settings=dict(
        # avoid truncation of help text
        max_content_width=130,
    ),
)
@click.option(
    '--log-file',
    type=bool,
    default=None,
    help="Output log file path."
)
@click.option(
    '--debug',
    type=bool,
    is_flag=True,
    default=False,
    help="Enable logging in debug mode."
)
def main(log_file: str, debug: bool):
    configure_logging(log_file, debug)


# noinspection PyTypeChecker
main.add_command()
