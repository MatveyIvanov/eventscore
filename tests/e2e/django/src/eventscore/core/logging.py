import logging
import sys

formatter = logging.Formatter(
    "PID=%(process)s,TID=%(thread)s: %(asctime)s [%(levelname)s] - %(message)s"
)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)

logger = logging.getLogger()
logger.handlers.clear()
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
logger.propagate = False
