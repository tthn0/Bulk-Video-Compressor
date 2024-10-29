import logging
from logging import Handler, Logger
from pathlib import Path


def create_logger(
    log_dir: Path,
    log_file_name: str = "log.log",
    output_to_console: bool = False,
) -> Logger:
    """Creates a directory for logs if it doesn't exist and returns a logger."""

    log_dir.mkdir(parents=True, exist_ok=True)

    handlers: list[Handler] = [logging.FileHandler(filename=log_dir / log_file_name)]
    if output_to_console:
        handlers.append(logging.StreamHandler())

    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] | %(levelname)s | %(filename)s:%(lineno)d | %(message)s",
        handlers=handlers,
    )
    return logging.getLogger(name=__name__)
