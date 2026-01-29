#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Westy FileMaster PRO - Professional File Manager
# OpenATV Python 3 compatible plugin
#

"""
Westy FileMaster PRO Plugin
Professional File Manager for Enigma2/OpenATV
"""

from __future__ import print_function, absolute_import, division, unicode_literals

import os
import sys
import gettext

# ============================================================================
# PLUGIN METADATA
# ============================================================================
PLUGIN_NAME = "Westy FileMaster PRO"
PLUGIN_VERSION = "2.1.0"
PLUGIN_DESCRIPTION = "Professional File Manager with Advanced Features"
PLUGIN_AUTHOR = "Westworld"
PLUGIN_LICENSE = "GPLv3"
PLUGIN_COPYRIGHT = "© 2024 Westworld"

# ============================================================================
# PATH CONFIGURATION
# ============================================================================
PLUGIN_PATH = os.path.dirname(os.path.abspath(__file__))
LOCALE_PATH = os.path.join(PLUGIN_PATH, 'locale')
IMAGES_PATH = os.path.join(PLUGIN_PATH, 'images')

# ============================================================================
# ENIGMA2 COMPATIBILITY CHECK
# ============================================================================
def is_enigma2():
    """Check if running in Enigma2 environment"""
    try:
        import enigma
        return True
    except ImportError:
        return False

ENIGMA2_AVAILABLE = is_enigma2()

# Python version check
PY3 = sys.version_info[0] >= 3
if PY3:
    # Python 3 specific imports
    import builtins
    unicode = str
    basestring = str
    long = int
else:
    # Python 2 specific imports
    import __builtin__ as builtins

# ============================================================================
# DEBUG MODE
# ============================================================================
DEBUG = os.environ.get('WESTY_DEBUG', '0') == '1'

def debug_print(*args, **kwargs):
    """Conditional debug printing"""
    if DEBUG:
        message = "[WestyFileMaster] " + " ".join(str(arg) for arg in args)
        print(message, **kwargs)

# ============================================================================
# INTERNATIONALIZATION (I18N)
# ============================================================================
def get_language():
    """Get current system language for Enigma2"""
    try:
        # Method 1: Try Enigma2 language
        if ENIGMA2_AVAILABLE:
            try:
                from Tools.Geolocation import geolocation
                lang = geolocation.getActiveLanguage()
                if lang:
                    return lang[:2]
            except:
                pass
        
        # Method 2: Try locale
        import locale
        lang = locale.getdefaultlocale()[0]
        if lang:
            return lang[:2]  # Return first 2 chars (e.g., 'en', 'de')
    except:
        pass
    
    return 'en'  # Default to English

def init_gettext():
    """Initialize gettext translations for OpenATV/Enigma2"""
    try:
        # Check if locale directory exists
        if os.path.exists(LOCALE_PATH):
            # Bind the text domain
            gettext.bindtextdomain('WestyFileMasterPRO', LOCALE_PATH)
            gettext.textdomain('WestyFileMasterPRO')
            
            # Get language
            lang = get_language()
            
            # Try to load specific translation
            try:
                translation = gettext.translation(
                    'WestyFileMasterPRO',
                    localedir=LOCALE_PATH,
                    languages=[lang],
                    fallback=True
                )
                return translation.gettext
            except:
                # Use system default
                return gettext.gettext
        else:
            # No locale directory, use identity function
            debug_print("Locale directory not found: {}".format(LOCALE_PATH))
            return lambda x: x
            
    except Exception as e:
        debug_print("Translation initialization failed: {}".format(e))
        # Fallback: identity function (returns string as-is)
        return lambda x: x

# Initialize translation function
_ = init_gettext()

# ============================================================================
# STRING COMPATIBILITY FUNCTIONS
# ============================================================================
def ensure_str(s, encoding='utf-8'):
    """
    Ensure string is unicode/str for Python 3 compatibility
    Args:
        s: Input string (str, bytes, or unicode)
        encoding: Encoding to use for bytes conversion
    Returns:
        str: Unicode string
    """
    if s is None:
        return ""
    
    if PY3:
        # Python 3: already str
        if isinstance(s, bytes):
            try:
                return s.decode(encoding)
            except UnicodeDecodeError:
                return s.decode(encoding, 'ignore')
        return str(s)
    else:
        # Python 2: convert to unicode
        if isinstance(s, str):
            return unicode(s, encoding, 'ignore')
        return unicode(s)

def ensure_unicode(s, encoding='utf-8'):
    """Alias for ensure_str for backward compatibility"""
    return ensure_str(s, encoding)

def bytes_to_str(b, encoding='utf-8'):
    """Convert bytes to string safely"""
    if isinstance(b, bytes):
        try:
            return b.decode(encoding)
        except UnicodeDecodeError:
            return b.decode(encoding, 'ignore')
    return str(b)

def str_to_bytes(s, encoding='utf-8'):
    """Convert string to bytes safely"""
    if isinstance(s, unicode):
        return s.encode(encoding)
    elif isinstance(s, str):
        if PY3:
            return s.encode(encoding)
        else:
            return s
    return bytes(s, encoding)

# ============================================================================
# FILE SYSTEM COMPATIBILITY FUNCTIONS
# ============================================================================
def listdir_unicode(path):
    """List directory with unicode support"""
    try:
        entries = os.listdir(path)
        if PY3:
            return entries
        else:
            return [ensure_unicode(entry) for entry in entries]
    except (OSError, IOError) as e:
        debug_print("Error listing directory {}: {}".format(path, e))
        return []

def path_exists(path):
    """Check if path exists with unicode support"""
    try:
        return os.path.exists(ensure_str(path))
    except Exception as e:
        debug_print("Error checking path {}: {}".format(path, e))
        return False

def isdir_unicode(path):
    """Check if path is directory with unicode support"""
    try:
        return os.path.isdir(ensure_str(path))
    except Exception as e:
        debug_print("Error checking directory {}: {}".format(path, e))
        return False

def isfile_unicode(path):
    """Check if path is file with unicode support"""
    try:
        return os.path.isfile(ensure_str(path))
    except Exception as e:
        debug_print("Error checking file {}: {}".format(path, e))
        return False

def get_recommended_directory(purpose="source"):
    """Get recommended starting directory for Enigma2"""
    # Common Enigma2 paths
    common_paths = [
        "/media/hdd/",
        "/media/usb/",
        "/media/sda1/",
        "/media/sdb1/",
        "/media/sdc1/",
        "/home/root/",
        "/tmp/",
        "/"
    ]
    
    for path in common_paths:
        if path_exists(path) and os.access(ensure_str(path), os.R_OK):
            return path
    
    return "/"

def shorten_path(path, max_length=50):
    """Shorten long paths for display"""
    if not path:
        return ""
    
    path_str = ensure_str(path)
    if len(path_str) <= max_length:
        return path_str
    
    # Try to keep the end of the path visible
    parts = path_str.split('/')
    if len(parts) > 3:
        return '.../' + '/'.join(parts[-3:])
    else:
        return path_str[:max_length-3] + '...'

# ============================================================================
# IMAGE PATH RESOLUTION
# ============================================================================
def get_icon_path(icon_name):
    """Get full path to icon file"""
    # Check multiple possible locations
    possible_paths = [
        os.path.join(IMAGES_PATH, icon_name),
        os.path.join(PLUGIN_PATH, "images", icon_name),
        "/usr/share/enigma2/skin_default/" + icon_name,
        "/usr/lib/enigma2/python/Plugins/Extensions/WestyFileMasterPRO/images/" + icon_name
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    debug_print("Icon not found: {}".format(icon_name))
    return None

# ============================================================================
# ENIGMA2 SPECIFIC HELPERS
# ============================================================================
def get_enigma_desktop_size():
    """Get screen size for Enigma2"""
    if ENIGMA2_AVAILABLE:
        try:
            from enigma import getDesktop
            desktop = getDesktop(0)
            return desktop.size()
        except:
            pass
    return None

def is_full_hd():
    """Check if screen is FullHD (1920x1080)"""
    size = get_enigma_desktop_size()
    if size:
        return size.width() >= 1920
    return False

# ============================================================================
# PLUGIN MODULE EXPORTS
# ============================================================================
__all__ = [
    # Plugin info
    'PLUGIN_NAME',
    'PLUGIN_VERSION',
    'PLUGIN_DESCRIPTION',
    'PLUGIN_AUTHOR',
    'PLUGIN_PATH',
    'LOCALE_PATH',
    'IMAGES_PATH',
    
    # Environment
    'ENIGMA2_AVAILABLE',
    'PY3',
    'DEBUG',
    
    # Functions
    '_',
    'debug_print',
    'ensure_str',
    'ensure_unicode',
    'bytes_to_str',
    'str_to_bytes',
    'listdir_unicode',
    'path_exists',
    'isdir_unicode',
    'isfile_unicode',
    'get_recommended_directory',
    'shorten_path',
    'get_icon_path',
    'is_full_hd',
    
    # Initialization
    'init_gettext',
    'get_language',
]

# ============================================================================
# MODULE INITIALIZATION
# ============================================================================
if __name__ != '__main__':
    # Install translation globally when imported as module
    try:
        builtins.__dict__['_'] = _
    except:
        pass

# Plugin initialization message
if __name__ == '__main__':
    print("=" * 60)
    print("{} - {}".format(PLUGIN_NAME, PLUGIN_DESCRIPTION))
    print("Version: {}".format(PLUGIN_VERSION))
    print("Author: {}".format(PLUGIN_AUTHOR))
    print("License: {}".format(PLUGIN_LICENSE))
    print("Enigma2: {}".format(ENIGMA2_AVAILABLE))
    print("Python: {}".format(sys.version))
    print("Plugin Path: {}".format(PLUGIN_PATH))
    print("Locale Path: {}".format(LOCALE_PATH))
    print("Images Path: {}".format(IMAGES_PATH))
    print("=" * 60)
    
    # Test functions
    print("\nTesting compatibility functions:")
    test_bytes = b"test bytes"
    test_str = "test string"
    print("Bytes to str: {}".format(bytes_to_str(test_bytes)))
    print("Str to bytes: {}".format(str_to_bytes(test_str)))
    
    print("\nTesting path functions:")
    test_path = "/tmp"
    print("Path exists {}: {}".format(test_path, path_exists(test_path)))
    print("Is directory {}: {}".format(test_path, isdir_unicode(test_path)))
    
    print("\nPlugin initialized successfully!")