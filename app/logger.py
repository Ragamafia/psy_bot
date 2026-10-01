import os

# loguru читает формат из окружения при импорте, поэтому задаём его раньше.
os.environ["LOGURU_FORMAT"] = (
    "{time:DD.MM.YY HH:mm:ss} [<lvl>{level:^10}</lvl>] <lvl>{message}</lvl>"  # noqa
)
from loguru import logger  # noqa: E402

__all__ = ["logger"]
