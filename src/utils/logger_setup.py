import logging

# https://zenn.dev/techflagcorp/articles/8d6327311e1e9f


def setup_logger(name, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler()
        logger.addHandler(handler)

    return logger
