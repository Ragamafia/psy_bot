import os  # noqa: E402,F401

os.environ["LOGURU_FORMAT"] = (
    "{time:DD.MM.YY HH:mm:ss} [<lvl>{level:^10}</lvl>] <lvl>{message}</lvl>"  # noqa
)
os.environ["LEVEL"] = "DEBUG"  # noqa
from loguru import logger

__all__ = ["logger"]
