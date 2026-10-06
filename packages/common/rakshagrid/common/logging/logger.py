# shared/logging/logger.py
"""Centralized logging utility for Raksha Grid."""

import logging
import sys
import os

def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Configures and returns a standardized logger instance."""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        logger.propagate = False
        
    return logger
