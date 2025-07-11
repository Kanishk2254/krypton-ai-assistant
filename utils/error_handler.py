import logging
import traceback
import functools
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('krypton_errors.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('KRYPTON')

def error_handler(func):
    """Decorator to handle errors gracefully"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_msg = f"Error in {func.__name__}: {str(e)}"
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            return None
    return wrapper

def safe_execute(func, *args, **kwargs):
    """Execute function safely with error handling"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Safe execution failed: {e}")
        return None

class KryptonException(Exception):
    """Custom exception for Krypton-specific errors"""
    pass
