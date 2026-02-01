#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Westy FileMaster PRO - Professional File Manager
# OpenATV Python 3 compatible version v2.1.0 - FIXED

from __future__ import print_function, absolute_import, division, unicode_literals

import os
import sys
import traceback

# ============================================================================
# PATH SETUP FOR IMPORTS
# ============================================================================
PLUGIN_PATH = os.path.dirname(os.path.abspath(__file__))
if PLUGIN_PATH not in sys.path:
    sys.path.insert(0, PLUGIN_PATH)

# ============================================================================
# DEBUG LOGGING - ADDED FOR BETTER DEBUGGING
# ============================================================================
DEBUG_LOG = "/tmp/westy_filemaster_debug.log"

def debug_log(message):
    """Write debug message to log file"""
    try:
        with open(DEBUG_LOG, 'a') as f:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {message}\n")
            f.flush()
    except:
        pass

debug_log("="*60)
debug_log("Westy FileMaster PRO - Plugin Starting (Fixed Version)")
debug_log("="*60)

# ============================================================================
# IMPORT PLUGIN UTILITIES - FIXED VERSION
# ============================================================================
try:
    # Try to import from our plugin's __init__.py
    import __init__ as plugin_init
    
    # Get the functions we need
    PLUGIN_NAME = plugin_init.PLUGIN_NAME
    PLUGIN_VERSION = plugin_init.PLUGIN_VERSION
    PLUGIN_DESCRIPTION = plugin_init.PLUGIN_DESCRIPTION
    PLUGIN_AUTHOR = plugin_init.PLUGIN_AUTHOR
    _ = plugin_init._
    debug_print = plugin_init.debug_print
    ensure_str = plugin_init.ensure_str
    ensure_unicode = plugin_init.ensure_unicode
    ENIGMA2_AVAILABLE = plugin_init.ENIGMA2_AVAILABLE
    
    debug_print(f"plugin.py: Imported from __init__.py v{PLUGIN_VERSION}")
    debug_log(f"plugin.py: Imported from __init__.py v{PLUGIN_VERSION}")
    
except ImportError as e:
    # Fallback if import fails
    def debug_print(*args, **kwargs):
        msg = " ".join(str(a) for a in args)
        print(msg)
        debug_log(msg)
    def _(text): return text
    def ensure_str(s, encoding='utf-8'): return str(s)
    ensure_unicode = ensure_str
    
    PLUGIN_NAME = "Westy FileMaster PRO"
    PLUGIN_VERSION = "2.1.0"
    PLUGIN_DESCRIPTION = "Professional File Manager with Advanced Features"
    PLUGIN_AUTHOR = "Westworld"
    ENIGMA2_AVAILABLE = False
    
    debug_print(f"plugin.py: Fallback mode - {e}")
    debug_log(f"plugin.py: Fallback mode - {e}")

# ============================================================================
# ENIGMA2/OPENATV IMPORTS WITH FALLBACKS
# ============================================================================
if ENIGMA2_AVAILABLE:
    try:
        from Plugins.Plugin import PluginDescriptor
        from Components.config import config, ConfigSubsection, ConfigYesNo, ConfigText, ConfigSelection, ConfigDirectory
        from Screens.MessageBox import MessageBox
        ENIGMA2_PLUGIN_AVAILABLE = True
        debug_print("plugin.py: Enigma2 plugin imports successful")
        debug_log("plugin.py: Enigma2 plugin imports successful")
    except ImportError as e:
        debug_print(f"plugin.py: Enigma2 plugin imports failed: {e}")
        debug_log(f"plugin.py: Enigma2 plugin imports failed: {e}")
        ENIGMA2_PLUGIN_AVAILABLE = False
else:
    ENIGMA2_PLUGIN_AVAILABLE = False

if not ENIGMA2_PLUGIN_AVAILABLE:
    debug_print("plugin.py: Using mock PluginDescriptor")
    debug_log("plugin.py: Using mock PluginDescriptor")
    
    # Mock PluginDescriptor
    class PluginDescriptor:
        WHERE_PLUGINMENU = 0
        WHERE_EXTENSIONSMENU = 1
        WHERE_MENU = 2
        WHERE_FILESCAN = 3
        WHERE_AUTOSTART = 4
        
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
    
    # Mock MessageBox
    class MessageBox:
        TYPE_INFO = 0
        TYPE_WARNING = 1
        TYPE_ERROR = 2
        
        def __init__(self, session, text, type=None, timeout=None):
            self.session = session
            self.text = text
            self.type = type
            self.timeout = timeout
    
    # Mock config
    class MockConfig:
        class plugins:
            class westyfilemaster:
                enabled = True
                add_mainmenu_entry = False
                add_extensionmenu_entry = True
                show_in_pluginmanager = True
    
    config = MockConfig()

# ============================================================================
# PLUGIN INFO
# ============================================================================
pname = _(PLUGIN_NAME)
pdesc = _(PLUGIN_DESCRIPTION)

# ============================================================================
# PLUGIN START FUNCTIONS - FIXED VERSION
# ============================================================================
def start_from_pluginmenu(session, **kwargs):
    """Start FileMaster from plugin menu - FIXED with path parameter"""
    debug_print("plugin.py: Starting FileMaster from plugin menu")
    debug_log("plugin.py: start_from_pluginmenu called")
    
    try:
        # Import UI module
        debug_print("plugin.py: Importing ui module...")
        debug_log("plugin.py: Importing ui module...")
        import ui
        
        # Check if screen class exists
        if not hasattr(ui, 'WestyFileMasterScreen'):
            error_msg = "WestyFileMasterScreen not found in ui module"
            debug_print(f"plugin.py: ERROR: {error_msg}")
            debug_log(f"plugin.py: ERROR: {error_msg}")
            
            if ENIGMA2_PLUGIN_AVAILABLE:
                try:
                    session.open(MessageBox, 
                               "FileMaster Error: Screen class not found\nCheck /tmp/westy_filemaster_debug.log",
                               MessageBox.TYPE_ERROR, timeout=10)
                except:
                    pass
            return None
        
        # Determine a good default path - FIX: Pass this as parameter to screen
        default_paths = ['/media/hdd', '/media/usb', '/home/root', '/tmp']
        start_path = None
        for path in default_paths:
            if os.path.isdir(path):
                start_path = path
                debug_print(f"plugin.py: Using start path: {start_path}")
                debug_log(f"plugin.py: Using start path: {start_path}")
                break
        
        if not start_path:
            start_path = "/tmp"
            debug_print("plugin.py: Using fallback path: /tmp")
            debug_log("plugin.py: Using fallback path: /tmp")
        
        # FIXED: Pass the path parameter to WestyFileMasterScreen
        debug_print(f"plugin.py: Opening WestyFileMasterScreen with path={start_path}")
        debug_log(f"plugin.py: Opening WestyFileMasterScreen with path={start_path}")
        
        # DEBUG
        try:
            with open("/tmp/westy_screen_init.log", "a") as f:
                from datetime import datetime
                f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] plugin.py: About to open screen\n")
        except:
            pass
        
        try:
            # This is the FIXED line - passing path as second parameter
            screen = session.open(ui.WestyFileMasterScreen, start_path)
            debug_print(f"plugin.py: Screen opened successfully")
            debug_log(f"plugin.py: Screen opened successfully")
            
            # DEBUG
            try:
                with open("/tmp/westy_screen_init.log", "a") as f:
                    from datetime import datetime
                    f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] plugin.py: session.open() returned: {screen}\n")
            except:
                pass
            
            return screen
        except Exception as e:
            print(f"CRITICAL ERROR opening screen: {e}")
            import traceback
            traceback.print_exc()
            debug_print(f"CRITICAL: {e}")
            debug_log(f"CRITICAL: {e}")
            debug_log(traceback.format_exc())
            
            if ENIGMA2_PLUGIN_AVAILABLE:
                try:
                    session.open(MessageBox,
                               f"FileMaster Error:\n{str(e)[:100]}\n\nCheck /tmp/westy_filemaster_debug.log",
                               MessageBox.TYPE_ERROR, timeout=15)
                except:
                    pass
            return None
            
    except ImportError as e:
        error_msg = f"Failed to import ui module: {e}"
        debug_print(f"plugin.py: ERROR: {error_msg}")
        debug_log(f"plugin.py: ERROR: {error_msg}")
        return None
    except Exception as e:
        error_msg = f"Error starting plugin: {e}"
        debug_print(f"plugin.py: ERROR: {error_msg}")
        debug_log(f"plugin.py: ERROR: {error_msg}")
        import traceback
        debug_log(traceback.format_exc())
        
        if ENIGMA2_PLUGIN_AVAILABLE:
            try:
                session.open(MessageBox,
                           f"FileMaster Error:\n{str(e)[:100]}\n\nCheck /tmp/westy_filemaster_debug.log",
                           MessageBox.TYPE_ERROR, timeout=15)
            except:
                pass
        return None
def show_cache_stats(session):
    """Show cache statistics (debug feature)"""
    try:
        from .CacheManager import get_cache_stats
        stats = get_cache_stats()
        
        message = "Cache Statistics:\n\n"
        message += f"File Info Cache:\n"
        message += f"  Size: {stats['file_info']['size']}/{stats['file_info']['max_size']}\n"
        message += f"  Hit Rate: {stats['file_info']['hit_rate']}\n"
        message += f"  Hits: {stats['file_info']['hits']}\n"
        message += f"  Misses: {stats['file_info']['misses']}\n\n"
        message += f"Image Cache:\n"
        message += f"  Size: {stats['image_cache']['size']}/{stats['image_cache']['max_size']}"
        
        if ENIGMA2_PLUGIN_AVAILABLE:
            session.open(MessageBox, message, MessageBox.TYPE_INFO)
        else:
            print(message)
    except Exception as e:
        debug_print(f"Error showing cache stats: {e}")

# ============================================================================
# PLUGIN REGISTRATION
# ============================================================================
def Plugins(**kwargs):
    """Main plugin registration function for OpenATV"""
    debug_print(f"plugin.py: Registering {pname} v{PLUGIN_VERSION}")
    debug_log(f"plugin.py: Registering {pname} v{PLUGIN_VERSION}")
    
    plugin_list = []
    
    # Check if plugin is enabled
    try:
        if not config.plugins.westyfilemaster.enabled:
            debug_print("plugin.py: Plugin is disabled in configuration")
            debug_log("plugin.py: Plugin is disabled in configuration")
            return plugin_list
    except:
        pass
    
    # Add to plugin menu
    try:
        desc_pluginmenu = PluginDescriptor(
            name=_(pname),
            description=_(pdesc),
            where=PluginDescriptor.WHERE_PLUGINMENU,
            fnc=start_from_pluginmenu,
            needsRestart=False
        )
        plugin_list.append(desc_pluginmenu)
        debug_print("plugin.py: ✓ Added to Plugin Browser")
        debug_log("plugin.py: ✓ Added to Plugin Browser")
    except Exception as e:
        debug_print(f"plugin.py: ✗ Failed to add to Plugin Browser: {e}")
        debug_log(f"plugin.py: ✗ Failed to add to Plugin Browser: {e}")
    
    # Add to extension menu if configured
    try:
        if config.plugins.westyfilemaster.add_extensionmenu_entry:
            desc_extensionmenu = PluginDescriptor(
                name=_(pname),
                description=_(pdesc),
                where=PluginDescriptor.WHERE_EXTENSIONSMENU,
                fnc=start_from_pluginmenu,
                needsRestart=False
            )
            plugin_list.append(desc_extensionmenu)
            debug_print("plugin.py: ✓ Added to extensions menu")
            debug_log("plugin.py: ✓ Added to extensions menu")
    except:
        pass
    
    debug_print(f"plugin.py: Registration complete - {len(plugin_list)} descriptors")
    debug_log(f"plugin.py: Registration complete - {len(plugin_list)} descriptors")
    return plugin_list

# ============================================================================
# TEST FUNCTION
# ============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print(f"{PLUGIN_NAME} v{PLUGIN_VERSION}")
    print(f"Description: {PLUGIN_DESCRIPTION}")
    print(f"Author: {PLUGIN_AUTHOR}")
    print(f"Python: {sys.version}")
    print(f"Plugin Path: {PLUGIN_PATH}")
    print("=" * 60)
    
    # Test plugin registration
    try:
        plugins = Plugins()
        print(f"Plugin registration test: {len(plugins)} descriptor(s)")
        for plugin in plugins:
            print(f"  - {plugin.name}")
    except Exception as e:
        print(f"Plugin registration test failed: {e}")
    
    print(f"\nplugin.py v{PLUGIN_VERSION} ready!")
