#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division, unicode_literals

import os
import sys

# Add import fallbacks with try/except for better compatibility
try:
    from Screens.Screen import Screen
    from Components.ActionMap import ActionMap
    from Components.Label import Label
    from Components.Sources.StaticText import StaticText
    from Components.config import config, ConfigSubsection, ConfigYesNo, ConfigSelection, ConfigDirectory, getConfigListEntry
    from Components.ConfigList import ConfigListScreen
    from enigma import getDesktop
    
    ENIGMA2_AVAILABLE = True
except ImportError as e:
    # Fallback for testing or compatibility
    print(f"Warning: Some Enigma2 imports failed: {e}")
    
    # Mock classes for testing
    class Screen:
        def __init__(self, session):
            self.session = session
        
        def close(self):
            pass
    
    class ConfigListScreen:
        def __init__(self, *args, **kwargs):
            pass
        
        def keyOK(self):
            pass
    
    class ActionMap:
        def __init__(self, *args, **kwargs):
            pass
    
    class Label:
        def __init__(self, text=""):
            self.text = text
    
    class StaticText:
        def __init__(self, text=""):
            self.text = text
    
    class MockConfig:
        class plugins:
            class westyfilemaster:
                enabled = type('obj', (), {'value': True, 'save': lambda: None})()
                add_mainmenu_entry = type('obj', (), {'value': False, 'save': lambda: None})()
                add_extensionmenu_entry = type('obj', (), {'value': True, 'save': lambda: None})()
                show_in_pluginmanager = type('obj', (), {'value': True, 'save': lambda: None})()
                enable_tabs = type('obj', (), {'value': True, 'save': lambda: None})()
                pane_layout = type('obj', (), {'value': 'horizontal', 'save': lambda: None})()
                default_left_path = type('obj', (), {'value': '/media/hdd/', 'save': lambda: None})()
                default_right_path = type('obj', (), {'value': '/home/root/', 'save': lambda: None})()
                show_hidden_files = type('obj', (), {'value': False, 'save': lambda: None})()
                confirm_deletions = type('obj', (), {'value': True, 'save': lambda: None})()
    
    config = MockConfig()
    
    def getDesktop(screen):
        class Desktop:
            def size(self):
                class Size:
                    def width(self):
                        return 1920
                    def height(self):
                        return 1080
                return Size()
        return Desktop()
    
    def getConfigListEntry(description, config_item):
        return (description, config_item)
    
    class ConfigSubsection:
        pass
    
    class ConfigYesNo:
        def __init__(self, default=True):
            self.value = default
        
        def save(self):
            pass
        
        def cancel(self):
            pass
    
    class ConfigSelection:
        def __init__(self, default="", choices=None):
            self.value = default
            self.choices = choices or []
        
        def save(self):
            pass
        
        def cancel(self):
            pass
    
    class ConfigDirectory:
        def __init__(self, default=""):
            self.value = default
        
        def save(self):
            pass
        
        def cancel(self):
            pass
    
    ENIGMA2_AVAILABLE = False

# Import our plugin's utilities
try:
    # Changed from relative import to absolute import
    from __init__ import (
        _,
        debug_print,
        ensure_str,
        ensure_unicode,
        PLUGIN_NAME,
        PLUGIN_VERSION
    )
except ImportError as e:
    print(f"Warning: Could not import from __init__: {e}")
    # Fallback for testing
    def _(text):
        return text
    
    def debug_print(*args, **kwargs):
        if args:
            print(*args)
    
    def ensure_str(s, encoding='utf-8'):
        if s is None:
            return ""
        if isinstance(s, bytes):
            try:
                return s.decode(encoding)
            except UnicodeDecodeError as e:
                print(f"Error: {e}")
                return s.decode('latin-1', 'ignore')
        return str(s)
    
    ensure_unicode = ensure_str
    PLUGIN_NAME = "Westy FileMaster PRO"
    PLUGIN_VERSION = "2.1.0"

class WestyFileMasterSetup(ConfigListScreen, Screen):
    """Setup screen for Westy FileMaster PRO v2.1.0"""
    
    # Skin templates - will be selected based on resolution
    SKIN_FULLHD = """
    <screen position="center,center" size="1000,750" title="{title} v{version} - Setup">
        <widget name="config" position="50,50" size="900,550" itemHeight="35" scrollbarMode="showOnDemand"/>
        <widget source="key_red" render="Label" position="100,650" size="200,40" font="Regular;24" foregroundColor="#ffffff" backgroundColor="red" halign="center" valign="center"/>
        <widget source="key_green" render="Label" position="400,650" size="200,40" font="Regular;24" foregroundColor="#ffffff" backgroundColor="green" halign="center" valign="center"/>
        <widget source="key_blue" render="Label" position="700,650" size="200,40" font="Regular;24" foregroundColor="#ffffff" backgroundColor="blue" halign="center" valign="center"/>
        <widget name="version" position="50,700" size="900,20" font="Regular;16" foregroundColor="#888888" halign="center"/>
    </screen>
    """
    
    SKIN_SD = """
    <screen position="center,center" size="800,550" title="{title} v{version} - Setup">
        <widget name="config" position="50,50" size="700,400" itemHeight="30" scrollbarMode="showOnDemand"/>
        <widget source="key_red" render="Label" position="50,470" size="200,30" font="Regular;20" foregroundColor="#ffffff" backgroundColor="red" halign="center"/>
        <widget source="key_green" render="Label" position="300,470" size="200,30" font="Regular;20" foregroundColor="#ffffff" backgroundColor="green" halign="center"/>
        <widget source="key_blue" render="Label" position="550,470" size="200,30" font="Regular;20" foregroundColor="#ffffff" backgroundColor="blue" halign="center"/>
        <widget name="version" position="50,510" size="700,20" font="Regular;14" foregroundColor="#888888" halign="center"/>
    </screen>
    """
    
    def __init__(self, session):
        Screen.__init__(self, session)
        ConfigListScreen.__init__(self, [], session=session)
        
        # Determine screen resolution safely
        self.FULLHD = self._detect_screen_resolution()
        
        # Apply skin based on resolution
        skin_template = self.SKIN_FULLHD if self.FULLHD else self.SKIN_SD
        self.skin = skin_template.format(title=PLUGIN_NAME, version=PLUGIN_VERSION)
        
        debug_print(f"WestyFileMasterSetup: Initializing setup screen v{PLUGIN_VERSION}")
        debug_print(f"Screen resolution: {'FullHD (1920+)' if self.FULLHD else 'SD (<1920)'}")
        
        # Initialize configuration if not exists
        self.initConfig()
        
        # Create config list
        self.list = []
        self.createSetup()
        self["config"].list = self.list
        self["config"].l.setList(self.list)
        
        # Key labels
        self["key_red"] = StaticText(_("Cancel"))
        self["key_green"] = StaticText(_("Save"))
        self["key_blue"] = StaticText(_("Defaults"))
        
        # Version label
        self["version"] = Label(f"{PLUGIN_NAME} v{PLUGIN_VERSION}")
        
        # Actions - Use try/except for VirtualKeyBoard
        self["actions"] = ActionMap(["ColorActions", "SetupActions", "OkCancelActions"],
        {
            "cancel": self.cancel,
            "red": self.cancel,
            "green": self.save,
            "blue": self.defaults,
            "ok": self.keyOK,
        }, -1)
        
        self.onLayoutFinish.append(self.layoutFinished)
    
    def _detect_screen_resolution(self):
        """Safely detect screen resolution"""
        try:
            if ENIGMA2_AVAILABLE:
                desktop = getDesktop(0)
                width = desktop.size().width()
                debug_print(f"Detected screen width: {width}px")
                return width >= 1920
            else:
                # In test mode, assume FullHD
                return True
        except Exception as e:
            debug_print(f"Error detecting screen resolution: {e}")
            # Default to FullHD for safety
            return True
    
    def initConfig(self):
        """Initialize configuration if needed"""
        try:
            # Check if config exists using try/except
            _ = config.plugins.westyfilemaster.enabled
            debug_print("WestyFileMasterSetup: Configuration already exists")
        except AttributeError:
            # Create default config
            debug_print("WestyFileMasterSetup: Creating default configuration")
            
            try:
                config.plugins.westyfilemaster = ConfigSubsection()
                config.plugins.westyfilemaster.enabled = ConfigYesNo(default=True)
                config.plugins.westyfilemaster.add_mainmenu_entry = ConfigYesNo(default=False)
                config.plugins.westyfilemaster.add_extensionmenu_entry = ConfigYesNo(default=True)
                config.plugins.westyfilemaster.show_in_pluginmanager = ConfigYesNo(default=True)
                config.plugins.westyfilemaster.enable_tabs = ConfigYesNo(default=True)
                config.plugins.westyfilemaster.pane_layout = ConfigSelection(
                    default="horizontal", 
                    choices=[
                        ("horizontal", _("Horizontal Split")),
                        ("vertical", _("Vertical Split"))
                    ]
                )
                config.plugins.westyfilemaster.default_left_path = ConfigDirectory(default="/media/hdd/")
                config.plugins.westyfilemaster.default_right_path = ConfigDirectory(default="/home/root/")
                config.plugins.westyfilemaster.show_hidden_files = ConfigYesNo(default=False)
                config.plugins.westyfilemaster.confirm_deletions = ConfigYesNo(default=True)
                
                # NEW v2.1.0 Settings
                config.plugins.westyfilemaster.multi_select_enabled = ConfigYesNo(default=True)
                config.plugins.westyfilemaster.default_overwrite_prompt = ConfigYesNo(default=True)
                config.plugins.westyfilemaster.show_selection_numbers = ConfigYesNo(default=True)
                config.plugins.westyfilemaster.secure_delete_passes = ConfigSelection(
                    default="3",
                    choices=[
                        ("1", _("1 pass (Fast)")),
                        ("3", _("3 passes (Standard)")),
                        ("7", _("7 passes (Secure)")),
                    ]
                )
                # PERFORMANCE SETTINGS (NEW)
                config.plugins.westyfilemaster.show_icons = ConfigYesNo(default=True)
                config.plugins.westyfilemaster.compact_view = ConfigYesNo(default=False)
                config.plugins.westyfilemaster.enable_cache = ConfigYesNo(default=True)
                config.plugins.westyfilemaster.cache_size = ConfigSelection(
                   default="1000",
                   choices=[
                       ("500", _("500 items (Low Memory)")),
                       ("1000", _("1000 items (Standard)")),
                      ("2000", _("2000 items (High Memory)")),
                    ]
                )
                config.plugins.westyfilemaster.virtual_scroll = ConfigYesNo(default=True)
                debug_print("WestyFileMasterSetup: Configuration created successfully")
            except Exception as e:
                debug_print(f"WestyFileMasterSetup: Error creating config: {e}")
                # Create minimal config if full creation fails
                try:
                    config.plugins.westyfilemaster = ConfigSubsection()
                    config.plugins.westyfilemaster.enabled = ConfigYesNo(default=True)
                    config.plugins.westyfilemaster.show_hidden_files = ConfigYesNo(default=False)
                    config.plugins.westyfilemaster.confirm_deletions = ConfigYesNo(default=True)
                except Exception as e2:
                    debug_print(f"WestyFileMasterSetup: Critical config error: {e2}")
    
    def createSetup(self):
        """Create configuration list with sections"""
        self.list = []
        
        # Section headers function (if available)
        try:
            from Components.config import config
            # Some images have ConfigSelection with special handling for section headers
            pass
        except:
            pass
        
        # Section: General Settings
        self.list.append(getConfigListEntry(_("=== General Settings ==="), 
                     type('obj', (), {'value': '', 'save': lambda: None})()))
        
        self.list.append(getConfigListEntry(_("Plugin enabled"), config.plugins.westyfilemaster.enabled))
        self.list.append(getConfigListEntry(_("Show in plugin manager"), config.plugins.westyfilemaster.show_in_pluginmanager))
        self.list.append(getConfigListEntry(_("Add to main menu"), config.plugins.westyfilemaster.add_mainmenu_entry))
        self.list.append(getConfigListEntry(_("Add to extensions menu"), config.plugins.westyfilemaster.add_extensionmenu_entry))
        
        # Section: Display Settings
        self.list.append(getConfigListEntry(_("=== Display Settings ==="), 
                     type('obj', (), {'value': '', 'save': lambda: None})()))
        
        self.list.append(getConfigListEntry(_("Pane layout"), config.plugins.westyfilemaster.pane_layout))
        self.list.append(getConfigListEntry(_("Enable tabs"), config.plugins.westyfilemaster.enable_tabs))
        self.list.append(getConfigListEntry(_("Show hidden files"), config.plugins.westyfilemaster.show_hidden_files))

        # NEW: Performance Settings Section
        self.list.append(getConfigListEntry(_("=== Performance Settings ==="), 
                    type('obj', (), {'value': '', 'save': lambda: None})()))
      
        self.list.append(getConfigListEntry(_("Show file icons"), config.plugins.westyfilemaster.show_icons))
        self.list.append(getConfigListEntry(_("Compact view mode"), config.plugins.westyfilemaster.compact_view))
        self.list.append(getConfigListEntry(_("Enable file info cache"), config.plugins.westyfilemaster.enable_cache))
        self.list.append(getConfigListEntry(_("Cache size"), config.plugins.westyfilemaster.cache_size))
        self.list.append(getConfigListEntry(_("Virtual scrolling"), config.plugins.westyfilemaster.virtual_scroll))
        
        # Section: Default Paths
        self.list.append(getConfigListEntry(_("=== Default Paths ==="), 
                     type('obj', (), {'value': '', 'save': lambda: None})()))
        
        self.list.append(getConfigListEntry(_("Default left pane path"), config.plugins.westyfilemaster.default_left_path))
        self.list.append(getConfigListEntry(_("Default right pane path"), config.plugins.westyfilemaster.default_right_path))
        
        # Section: v2.1.0 New Features
        self.list.append(getConfigListEntry(_("=== v2.1.0 Multi-Selection ==="), 
                     type('obj', (), {'value': '', 'save': lambda: None})()))
        
        self.list.append(getConfigListEntry(_("Enable multi-selection"), config.plugins.westyfilemaster.multi_select_enabled))
        self.list.append(getConfigListEntry(_("Show selection numbers"), config.plugins.westyfilemaster.show_selection_numbers))
        
        # Section: Safety Settings
        self.list.append(getConfigListEntry(_("=== Safety Settings ==="), 
                     type('obj', (), {'value': '', 'save': lambda: None})()))
        
        self.list.append(getConfigListEntry(_("Confirm deletions"), config.plugins.westyfilemaster.confirm_deletions))
        self.list.append(getConfigListEntry(_("Prompt before overwrite"), config.plugins.westyfilemaster.default_overwrite_prompt))
        self.list.append(getConfigListEntry(_("Secure delete passes"), config.plugins.westyfilemaster.secure_delete_passes))
        
        self["config"].list = self.list
    
    def layoutFinished(self):
        """Called when layout is finished"""
        self.setTitle(f"{PLUGIN_NAME} v{PLUGIN_VERSION} - {_('Setup')}")
    
    def keyOK(self):
        """Handle OK button with try/except for VirtualKeyBoard"""
        current = self["config"].getCurrent()
        if current:
            # Allow editing of directory paths
            if hasattr(config.plugins.westyfilemaster, 'default_left_path') and \
               current[1] == config.plugins.westyfilemaster.default_left_path:
                self.openPathEditor(current[1], _("Enter left pane path"))
            elif hasattr(config.plugins.westyfilemaster, 'default_right_path') and \
                 current[1] == config.plugins.westyfilemaster.default_right_path:
                self.openPathEditor(current[1], _("Enter right pane path"))
            else:
                try:
                    ConfigListScreen.keyOK(self)
                except Exception as e:
                    debug_print(f"WestyFileMasterSetup: Error in keyOK: {e}")
    
    def openPathEditor(self, config_entry, title):
        """Open virtual keyboard for path editing with try/except"""
        try:
            from Screens.VirtualKeyBoard import VirtualKeyBoard
            self.session.openWithCallback(
                lambda newtext: self.pathEntered(config_entry, newtext),
                VirtualKeyBoard,
                title=title,
                text=config_entry.value
            )
        except ImportError:
            debug_print("WestyFileMasterSetup: VirtualKeyBoard not available")
            # Fallback to simple input
            from Screens.InputBox import InputBox
            self.session.openWithCallback(
                lambda newtext: self.pathEntered(config_entry, newtext),
                InputBox,
                title=title,
                windowTitle=title,
                text=config_entry.value
            )
        except Exception as e:
            debug_print(f"WestyFileMasterSetup: Error opening path editor: {e}")
    
    def pathEntered(self, config_entry, newtext):
        """Handle path entry from virtual keyboard"""
        if newtext:
            config_entry.value = newtext
            try:
                self["config"].invalidateCurrent()
            except:
                self["config"].setList(self.list)
    
    def save(self):
        """Save settings"""
        debug_print("WestyFileMasterSetup: Saving configuration")
        
        try:
            for x in self["config"].list:
                if hasattr(x[1], 'save'):
                    x[1].save()
            
            # Also save the main config
            if hasattr(config, 'save'):
                config.save()
            
            from Screens.MessageBox import MessageBox
            self.session.openWithCallback(
                self.saveCallback,
                MessageBox,
                _("Settings saved successfully.\nRestart plugin for changes to take effect."),
                MessageBox.TYPE_INFO
            )
        except Exception as e:
            debug_print(f"WestyFileMasterSetup: Error saving settings: {e}")
            from Screens.MessageBox import MessageBox
            self.session.open(
                MessageBox,
                _("Error saving settings: {}").format(str(e)),
                MessageBox.TYPE_ERROR
            )
    
    def saveCallback(self, result=None):
        """Callback after save message"""
        debug_print("WestyFileMasterSetup: Save completed")
        self.close()
    
    def cancel(self):
        """Cancel changes"""
        debug_print("WestyFileMasterSetup: Cancelling changes")
        try:
            for x in self["config"].list:
                if hasattr(x[1], 'cancel'):
                    x[1].cancel()
        except Exception as e:
            debug_print(f"WestyFileMasterSetup: Error cancelling: {e}")
        
        self.close()
    
    def defaults(self):
        """Reset to default values"""
        from Screens.MessageBox import MessageBox
        self.session.openWithCallback(
            self.defaultsConfirmed,
            MessageBox,
            _("Reset all settings to default values?"),
            MessageBox.TYPE_YESNO
        )
    
    def defaultsConfirmed(self, result):
        """Handle defaults confirmation"""
        if result:
            debug_print("WestyFileMasterSetup: Resetting to defaults")
            
            # General Settings
            config.plugins.westyfilemaster.enabled.value = True
            config.plugins.westyfilemaster.add_mainmenu_entry.value = False
            config.plugins.westyfilemaster.add_extensionmenu_entry.value = True
            config.plugins.westyfilemaster.show_in_pluginmanager.value = True
            config.plugins.westyfilemaster.enable_tabs.value = True
            
            # Display Settings
            config.plugins.westyfilemaster.pane_layout.value = "horizontal"
            config.plugins.westyfilemaster.show_hidden_files.value = False
            
            # Default Paths
            config.plugins.westyfilemaster.default_left_path.value = "/media/hdd/"
            config.plugins.westyfilemaster.default_right_path.value = "/home/root/"
            
            # v2.1.0 Settings
            if hasattr(config.plugins.westyfilemaster, 'multi_select_enabled'):
                config.plugins.westyfilemaster.multi_select_enabled.value = True
            
            if hasattr(config.plugins.westyfilemaster, 'show_selection_numbers'):
                config.plugins.westyfilemaster.show_selection_numbers.value = True
            
            if hasattr(config.plugins.westyfilemaster, 'default_overwrite_prompt'):
                config.plugins.westyfilemaster.default_overwrite_prompt.value = True
            
            if hasattr(config.plugins.westyfilemaster, 'secure_delete_passes'):
                config.plugins.westyfilemaster.secure_delete_passes.value = "3"
            
            # Safety Settings
            config.plugins.westyfilemaster.confirm_deletions.value = True
            
            # Update the config list
            self.createSetup()
            self["config"].setList(self.list)
            
            # Show confirmation
            from Screens.MessageBox import MessageBox
            self.session.open(
                MessageBox,
                _("Settings reset to defaults."),
                MessageBox.TYPE_INFO
            )


# Test function for standalone testing
if __name__ == "__main__":
    print("=" * 60)
    print(f"Westy FileMaster PRO Setup Test")
    print(f"Version: {PLUGIN_VERSION}")
    print("=" * 60)
    
    # Test config initialization
    print("Testing configuration initialization...")
    try:
        # Simulate config
        class TestConfig:
            class plugins:
                class westyfilemaster:
                    enabled = type('obj', (), {'value': True})()
        
        config = TestConfig()
        setup = WestyFileMasterSetup(None)
        print("✓ Setup class initialized successfully")
        print(f"✓ Plugin name: {PLUGIN_NAME}")
        print(f"✓ Plugin version: {PLUGIN_VERSION}")
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("=" * 60)