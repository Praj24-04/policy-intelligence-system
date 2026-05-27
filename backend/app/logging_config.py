import logging
import sys

class LoggerStream:
    """
    A file-like object that redirects write operations to a Python logger.
    Used to intercept raw print statements and capture them in structured logs.
    """
    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level

    def write(self, buf):
        # Standard print statements append a newline; strip to avoid extra empty lines
        message = buf.rstrip()
        if message:
            self.logger.log(self.log_level, message)

    def flush(self):
        pass


def setup_logging():
    """
    Sets up global Python logging configuration with standard console streaming
    and styled, structured metadata tags.
    """
    # Dynamic log level configuration loaded directly from environment
    import os
    log_level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_name, logging.INFO)
    
    # Modern, readable, standardized visual logging format
    log_format = "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Reconfigure root logger to stream specifically to standard un-redirected stdout
    # to avoid infinite print loop recursion.
    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(sys.__stdout__)
        ],
        force=True  # Clear any pre-existing basicConfig handlers
    )
    
    logger = logging.getLogger("app")
    logger.info(f"Structured logging system initialized with level: {log_level_name}")

    # Redirect all raw sys.stdout write calls (e.g. print statements) to logger app.stdout
    stdout_logger = logging.getLogger("app.stdout")
    sys.stdout = LoggerStream(stdout_logger, logging.INFO)

    # Redirect all raw sys.stderr write calls to logger app.stderr
    stderr_logger = logging.getLogger("app.stderr")
    sys.stderr = LoggerStream(stderr_logger, logging.ERROR)
