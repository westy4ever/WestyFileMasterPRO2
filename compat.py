"""Compatibility layer for Enigma2/OpenATV"""

import os
import sys

# Check if running in Enigma2
def is_enigma2():
    return 'enigma' in sys.modules or hasattr(sys, 'argv') and 'enigma2' in str(sys.argv)

# Safe imports
def safe_import(module_name, class_name=None):
    try:
        module = __import__(module_name, fromlist=[''])
        if class_name:
            return getattr(module, class_name)
        return module
    except ImportError:
        return None