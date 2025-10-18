import logging
import sys
from . import config

def setup_logging():
    """Configures the root logger for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ]
    )

if __name__ == '__main__':
    setup_logging()
    logging.info("Logging has been configured.")
    logging.warning("This is a test warning.")
    logging.error("This is a test error.")
