"""
Structured Logger for JARVIS Multi-Engine Architecture.
"""
import logging
import sys
import os

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(f"jarvis.{name}")
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s]: %(message)s', datefmt='%H:%M:%S')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
