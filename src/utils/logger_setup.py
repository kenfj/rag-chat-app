import logging

from uvicorn.logging import DefaultFormatter

from utils import settings

# https://zenn.dev/techflagcorp/articles/8d6327311e1e9f

# uvicorn.logging.DefaultFormatter for consistent log format
# https://stackoverflow.com/questions/62955750/what-does-do-in-python-log-config

# suppress log messages from third party libraries
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("LiteLLM").setLevel(logging.WARNING)
logging.getLogger("chainlit").setLevel(logging.WARNING)
logging.getLogger("azure.core").setLevel(logging.WARNING)

# for debug to find the logger name
# logging.basicConfig(format="%(levelname)s %(asctime)s %(name)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S", force=True)

# https://stackoverflow.com/questions/7173033/duplicate-log-output-when-using-python-logging-module
loggers = {}


def setup_logger(name):
    if name in loggers:
        return loggers[name]

    logger = logging.getLogger(name)
    logger.setLevel(settings.LOG_LEVEL)

    # Note: logger.hasHandlers() will not work as expected

    handler = logging.StreamHandler()
    handler.setLevel(settings.LOG_LEVEL)

    formatter = DefaultFormatter(
        fmt="%(levelprefix)s %(asctime)s %(name)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        use_colors=True,
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False

    loggers[name] = logger

    return logger
