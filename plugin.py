#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Westy FileMaster PRO - Professional File Manager
# OpenATV Python 3 compatible version v2.1.0

from __future__ import print_function, absolute_import, division, unicode_literals

import os
import sys

# ============================================================================
# PATH SETUP FOR IMPORTS
# ============================================================================
PLUGIN_PATH = os.path.dirname(os.path.abspath(__file__))
if PLUGIN_PATH not in sys.path:
    sys.path.insert(0, PLUGIN_PATH)

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
    
except ImportError as e:
    # Fallback if import fails
    debug_print = print
    def _(text): return text
    def ensure_str(s, encoding='utf-8'): return str(s)
    ensure_unicode = ensure_str
    
    PLUGIN_NAME = "Westy FileMaster PRO"
    PLUGIN_VERSION = "2.1.0"
    PLUGIN_DESCRIPTION = "Professional File Manager with Advanced Features"
    PLUGIN_AUTHOR = "Westworld"
    ENIGMA2_AVAILABLE = False
    
    debug_print(f"plugin.py: Fallback mode - {e}")

# ============================================================================
# ENIGMA2/OPENATV IMPORTS WITH FALLBACKS
# ============================================================================
if ENIGMA2_AVAILABLE:
    try:
        from Plugins.Plugin import PluginDescriptor
        from Components.config import config, ConfigSubsection, ConfigYesNo, ConfigText, ConfigSelection, ConfigDirectory
        ENIGMA2_PLUGIN_AVAILABLE = True
        debug_print("plugin.py: Enigma2 plugin imports successful")
    except ImportError as e:
        debug_print(f"plugin.py: Enigma2 plugin imports failed: {e}")
        ENIGMA2_PLUGIN_AVAILABLE = False
else:
    ENIGMA2_PLUGIN_AVAILABLE = False

if not ENIGMA2_PLUGIN_AVAILABLE:
    debug_print("plugin.py: Using mock PluginDescriptor")
    
    # Mock PluginDescriptor
    class PluginDescriptor:
        WHERE_PLUGINMENU = 0
        WHERE_EXTENSIONSMENU = 1
        WHERE_MENU = 2
        WHERE_FILESCAN = 3
        WHERE_AUTOSTART = 4
        
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
    
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
# PLUGIN START FUNCTIONS
# ============================================================================
def start_from_pluginmenu(session, **kwargs):
    """Start FileMaster from plugin menu"""
    debug_print("plugin.py: Starting FileMaster from plugin menu")
    
    try:
        # Import UI module
        import ui
        return session.open(ui.WestyFileMasterScreen)
    except ImportError as e:
        debug_print(f"plugin.py: Failed to import ui module: {e}")
        return None
    except Exception as e:
        debug_print(f"plugin.py: Error starting plugin: {e}")
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
        
        from Screens.MessageBox import MessageBox
        session.open(MessageBox, message, MessageBox.TYPE_INFO)
    except Exception as e:
        debug_print(f"Error showing cache stats: {e}")
# ============================================================================
# PLUGIN REGISTRATION
# ============================================================================
def Plugins(**kwargs):
    """Main plugin registration function for OpenATV"""
    debug_print(f"plugin.py: Registering {pname} v{PLUGIN_VERSION}")
    
    plugin_list = []
    
    # Check if plugin is enabled
    try:
        if not config.plugins.westyfilemaster.enabled:
            debug_print("plugin.py: Plugin is disabled in configuration")
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
    except Exception as e:
        debug_print(f"plugin.py: ✗ Failed to add to Plugin Browser: {e}")
    
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
    except:
        pass
    
    debug_print(f"plugin.py: Registration complete - {len(plugin_list)} descriptors")
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
