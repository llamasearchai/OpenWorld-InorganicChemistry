from __future__ import annotations

import logging
import logging.handlers
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output."""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        if sys.stdout.isatty():  # Only colorize if outputting to terminal
            color = self.COLORS.get(record.levelname, '')
            record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


class StructuredFormatter(logging.Formatter):
    """Structured formatter for file logging."""
    
    def format(self, record):
        # Add structured fields
        record.timestamp = datetime.fromtimestamp(record.created).isoformat()
        record.module_path = f"{record.module}.{record.funcName}"
        return super().format(record)


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    enable_console: bool = True,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> None:
    """Setup comprehensive logging configuration.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        enable_console: Whether to enable console logging
        max_file_size: Maximum log file size before rotation
        backup_count: Number of backup files to keep
    """
    # Clear any existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    
    # Set root level
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Console handler with colors
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = ColoredFormatter(
            '%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
    
    # File handler with rotation
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_file_size,
            backupCount=backup_count
        )
        file_formatter = StructuredFormatter(
            '%(timestamp)s | %(name)s | %(levelname)s | %(module_path)s:%(lineno)d | %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    
    # Suppress noisy third-party loggers
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name."""
    return logging.getLogger(name)


class LoggingContext:
    """Context manager for temporary logging configuration."""
    
    def __init__(self, level: str = "DEBUG", prefix: str = ""):
        self.level = level
        self.prefix = prefix
        self.original_level = None
        self.original_handlers = None
    
    def __enter__(self):
        root_logger = logging.getLogger()
        self.original_level = root_logger.level
        self.original_handlers = root_logger.handlers.copy()
        
        # Set new level
        root_logger.setLevel(getattr(logging, self.level.upper()))
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore original configuration
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        root_logger.handlers.extend(self.original_handlers)
        root_logger.setLevel(self.original_level)


def setup_experiment_logging(experiment_name: str, output_dir: str = "logs") -> Path:
    """Setup logging for a specific experiment.
    
    Args:
        experiment_name: Name of the experiment
        output_dir: Directory to store log files
    
    Returns:
        Path to the log file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = Path(output_dir) / f"{experiment_name}_{timestamp}.log"
    
    setup_logging(
        level="DEBUG",
        log_file=str(log_file),
        enable_console=True
    )
    
    logger = get_logger("experiment")
    logger.info(f"Starting experiment: {experiment_name}")
    logger.info(f"Logging to: {log_file}")
    
    return log_file