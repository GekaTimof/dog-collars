import logging
import sys
from logging.handlers import TimedRotatingFileHandler

FORMATTER_STRING = "%(levelname)s (%(asctime)s): %(message)s (Line: %(lineno)d) %(name)s [%(filename)s]"
FORMATTER = logging.Formatter(FORMATTER_STRING)
LOG_FILE = "log_file.log"

class ColoredFormatter(logging.Formatter):
    COLORS = {'DEBUG': '\033[94m', 'INFO': '\033[92m', 'WARNING': '\033[93m',
              'ERROR': '\033[91m', 'CRITICAL': '\033[95m'}

    def format(self, record):
        log_fmt = f"{self.COLORS.get(record.levelname, '')}%(levelname)s (%(asctime)s): %(message)s (Line: %(lineno)d) %(name)s [%(filename)s]"
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

def get_logger(logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(ColoredFormatter())
    logger.addHandler(console_handler)

    file_handler = TimedRotatingFileHandler(LOG_FILE, when='midnight')
    file_handler.setFormatter(FORMATTER)
    logger.addHandler(file_handler)

    return logger
