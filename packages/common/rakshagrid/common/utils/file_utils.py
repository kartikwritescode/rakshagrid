# shared/utils/file_utils.py
"""Centralized file manipulation utilities."""

import os
import shutil

def ensure_dir(path: str):
    """Ensure directory exists."""
    os.makedirs(path, exist_ok=True)

def safe_remove(path: str):
    """Safely remove a file if exists."""
    if os.path.exists(path):
        try:
            os.remove(path)
        except OSError:
            pass
