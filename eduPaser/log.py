import logging

def setup_custom_logger(name):
    formatter = logging.Formatter(fmt='%(levelname)8s [%(module)8s]: %(lineno)s %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger