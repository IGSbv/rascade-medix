import logging
import sys

def get_logger(name: str) -> logging.Logger:
    """
    Configures and returns a standard logger.

    Args:
        name (str): The name for the logger, typically __name__.

    Returns:
        logging.Logger: The configured logger instance.
    """
    # Create a logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Avoid adding handlers if they already exist
    if not logger.handlers:
        # Create a handler to write logs to the console (stdout)
        handler = logging.StreamHandler(sys.stdout)
        
        # Create a formatter and set it for the handler
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        # Add the handler to the logger
        logger.addHandler(handler)

    return logger