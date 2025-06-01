import logging

LINE_FORMAT = "[%(asctime)s] [%(levelname)-8s] [%(name)s:%(lineno)d] - %(message)s"


class LogFormatter(logging.Formatter):

    # thanks to https://stackoverflow.com/questions/384076/how-can-i-color-python-logging-output/56944256#56944256
    COLORS = {
        logging.DEBUG: '\x1b[36m',  # gray
        logging.INFO: '\x1b[38;20m',  # blue
        logging.WARNING: '\x1b[33;20m',  # yellow
        logging.ERROR: '\x1b[31;20m',  # red
        logging.CRITICAL: '\x1b[31;1m'  # bold red
    }

    def __init__(self):
        super().__init__(fmt=LINE_FORMAT)

    def formatMessage(self, record):
        # the literal is used to reset the format
        log_fmt = self.COLORS.get(record.levelno) + LINE_FORMAT + '\x1b[0m'
        formatter = logging.Formatter(log_fmt)
        return formatter.formatMessage(record)


def remove_handlers(logger: logging.Logger):
    for handler in logger.handlers:
        logger.removeHandler(handler)
        handler.close()


def configure_logging(log_file: str = None, debug: bool = False):

    logger = logging.getLogger()
    remove_handlers(logger)
    if debug:
        logger.setLevel(logging.DEBUG)
        logging.getLogger('sqlalchemy').setLevel(logging.INFO)
    else:
        logger.setLevel(logging.INFO)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(LogFormatter())
    logger.addHandler(stream_handler)

    if log_file is not None:
        file_handler = logging.FileHandler(log_file, mode='w')
        file_handler.setFormatter(logging.Formatter(LINE_FORMAT))
        logger.addHandler(file_handler)
