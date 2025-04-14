import logging

logger = logging.getLogger('template')
logger.setLevel(logging.DEBUG)


ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)


fmt = logging.Formatter(fmt='%(asctime)s :: %(levelname)s :: %(message)s')
ch.setFormatter(fmt)

logger.addHandler(ch)
