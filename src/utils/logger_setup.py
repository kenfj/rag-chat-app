import logging
from uvicorn.logging import DefaultFormatter

# https://zenn.dev/techflagcorp/articles/8d6327311e1e9f

# uvicorn DefaultFormatter for consistent log format
# https://stackoverflow.com/questions/62955750/what-does-do-in-python-log-config


def setup_logger(name, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler()

        formatter = DefaultFormatter(
            fmt="%(levelprefix)s %(asctime)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            use_colors=True,
        )
        handler.setFormatter(formatter)

        logger.addHandler(handler)

    return logger
