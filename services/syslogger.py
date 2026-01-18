import logging
from colorama import Fore, Style, init
from pathlib import Path
import pprint

class Logger():
    COLORS = {
        "INFO": Fore.GREEN,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "DEBUG": Fore.CYAN,
        "CRITICAL": Fore.MAGENTA
    }
    
    def __init__(self, name="ARC ALERTS", level=logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        if not self.logger.handlers:
            # Console handler
            console_handler = logging.StreamHandler()
            console_formatter = logging.Formatter(
                "[%(asctime)s] [%(levelname)s] %(message)s",
                "%Y-%m-%d %H:%M:%S"
            )
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)


    def _log(self, level, msg):
        # Pretty-print dicts/lists/tuples/sets
        if isinstance(msg, (dict, list, tuple, set)):
            msg = pprint.pformat(msg)

        # Add color only for console output
        color = self.COLORS.get(level, "")
        for handler in self.logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                msg = color + msg + Style.RESET_ALL

        # Use the logger's own method to preserve timestamps and formatting
        try: 
            getattr(self.logger, level.lower())(msg)
        except Exception as e:
            print(f"Error encountered: {e}")
        
    def info(self, msg): self._log("INFO", msg)
    def warn(self, msg): self._log("WARNING", msg)
    def error(self, msg): self._log("ERROR", msg)
    def debug(self, msg): self._log("DEBUG", msg)
    def critical(self, msg): self._log("CRITICAL", msg)        
    
log = Logger()