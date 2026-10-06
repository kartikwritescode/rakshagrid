# packages/ai-crime/rakshagrid/crime/__init__.py
"""Compatibility layer providing rakshagrid.crime alias for rakshagrid.ai_crime."""

import sys
from rakshagrid.ai_crime import *
from rakshagrid.ai_crime import __all__ as _all_exports

__all__ = list(_all_exports)
