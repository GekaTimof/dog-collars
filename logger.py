'''import logging

FORMATTER_STRING = "%(levelname)s (%(asctime)s): %(message)s (Line: %(lineno)d) [%(filename)s]"
FORMATTER = logging.Formatter(FORMATTER_STRING)
LOG_FILE = "log_file.log"

def get_logger(logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    logger.addHandler(console_handler)

    logging.basicConfig(level=logging.DEBUG, filename='log_file.log',
                        format='%(levelname)s (%(asctime)s): %(message)s (Line: %(lineno)d) [%(filename)s]',
                        datefmt='%d/%m/%Y %I:%M:%S',
                        encoding='utf-8', filemode='w')
    file_handler = TimedRotatingFileHandler(LOG_FILE, when='midnight')
    # file_handler.setFormatter(FORMATTER)
    logger.addHandler(file_handler)

    return logger




logging.debug('Дебаг')
logging.info('инфо')
logging.warning('Варнинг')
logging.error('Эррор')
logging.critical('Критикал')'''