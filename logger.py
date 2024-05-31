import logging
from logging.handlers import TimedRotatingFileHandler
import sys

FORMATTER_STRING = "%(levelname)s (%(asctime)s): %(message)s (Line: %(lineno)d) %(name)s [%(filename)s]"
FORMATTER = logging.Formatter(FORMATTER_STRING)
LOG_FILE = "log_file.log"

def get_logger(logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    logger.addHandler(console_handler)

    file_handler = TimedRotatingFileHandler(LOG_FILE, when='midnight')
    file_handler.setFormatter(FORMATTER)
    logger.addHandler(file_handler)

    return logger
