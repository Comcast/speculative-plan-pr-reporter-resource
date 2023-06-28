import logging

logging.basicConfig(
    format="%(levelname) -5s %(asctime)s %(funcName)- -20s: %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    level=logging.INFO,
)
logger = logging.getLogger("resourceLogger")
