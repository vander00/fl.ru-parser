import logging
from logging.handlers import RotatingFileHandler

LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"


def configure_logging(log_level: str = "INFO", log_file: str = "bot.log") -> None:
    formatter = logging.Formatter(fmt=LOG_FORMAT)

    file_handler = RotatingFileHandler(
        log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logging.basicConfig(level=log_level, handlers=[file_handler, stream_handler])
