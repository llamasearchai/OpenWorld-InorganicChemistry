from loguru import logger
import sys


def setup_logging(level: str = "INFO"):
    logger.remove()
    logger.add(sys.stderr, level=level, colorize=True,
               format="{time:YYYY-MM-DD HH:mm:ss} | {level: <7} | "
               "{name}:{function}:{line} - {message}",
               backtrace=True, diagnose=True)
    logger.add(
        "scipaper.log",
        level="DEBUG",
        rotation="10 MB",
        compression="zip")
    logger.opt(colors=True).info("Logging initialized")
