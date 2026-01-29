#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division, unicode_literals

import os
import sys

# Import plugin utilities
try:
    from . import (
        _,
        debug_print,
        ensure_str,
        ensure_unicode,
        PLUGIN_NAME,
        PLUGIN_VERSION
    )
    debug_print(f"MediaPlayerSettings: Imported plugin utilities v{PLUGIN_VERSION}")
except ImportError:
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
            except:
                return s.decode('latin-1', 'ignore')
        return str(s)
    
    ensure_unicode = ensure_str
    
    PLUGIN_NAME = "Westy FileMaster PRO"
    PLUGIN_VERSION = "2.1.0"

# Import media utilities
try:
    from .media_utils import media_utils, media_config
    MEDIA_UTILS_AVAILABLE = True
    debug_print("MediaPlayerSettings: Media utilities available")
except ImportError:
    MEDIA_UTILS_AVAILABLE = False
    debug_print("MediaPlayerSettings: Media utilities not available")

# Try to import Screens with fallbacks
try:
    from Screens.Screen import Screen
    SCREEN_AVAILABLE = True
    debug_print("MediaPlayerSettings: Screen available")
except ImportError:
    SCREEN_AVAILABLE = False
    debug_print("MediaPlayerSettings: Screen not available")
    
    class Screen:
        def __init__(self, session):
            self.session = session
        
        def close(self):
            pass

try:
    from Components.ActionMap import ActionMap
    ACTIONMAP_AVAILABLE = True
    debug_print("MediaPlayerSettings: ActionMap available")
except ImportError:
    ACTIONMAP_AVAILABLE = False
    debug_print("MediaPlayerSettings: ActionMap not available")
    
    class ActionMap:
        def __init__(self, contexts, actions, prio=-1):
            pass

try:
    from Components.Label import Label
    from Components.Sources.StaticText import StaticText
    COMPONENTS_AVAILABLE = True
    debug_print("MediaPlayerSettings: Basic components available")
except ImportError:
    COMPONENTS_AVAILABLE = False
    debug_print("MediaPlayerSettings: Basic components not available")
    
    class Label:
        def setText(self, text):
            pass
    
    class StaticText:
        def __init__(self, text=""):
            self.text = text

try:
    from enigma import getDesktop
    ENIGMA_AVAILABLE = True
    debug_print("MediaPlayerSettings: Enigma available")
except ImportError:
    ENIGMA_AVAILABLE = False
    debug_print("MediaPlayerSettings: Enigma not available")
    
    def getDesktop(screen):
        class Desktop:
            def size(self):
                class Size:
                    def width(self):
                        return 1920
                return Size()
        return Desktop()

# Get screen size for skin
try:
    FULLHD = getDesktop(0).size().width() >= 1920
except:
    FULLHD = False

class WestyMediaPlayerSettings(Screen):
    """Media player settings - v2.1.0"""
    
    # Dynamic skin based on screen size
    @staticmethod
    def get_skin():
        """Generate skin based on desktop size"""
        try:
            desktop = getDesktop(0)
            screen_width, screen_height = desktop.size().width(), desktop.size().height()
        except:
            screen_width, screen_height = 800, 600
        
        return """
        <screen name="WestyMediaPlayerSettings" position="center,center" size="{width},{height}" title="{plugin_name} Media Player Settings v{version}">
            <widget name="title" position="{title_x},{title_y}" size="{title_width},40" font="Regular;{title_font}" halign="center"/>
            
            <!-- Settings -->
            <widget name="auto_resume_label" position="{label_x},100" size="300,30" font="Regular;{font_size}" text="Auto-resume"/>
            <widget name="auto_resume_toggle" position="{value_x},100" size="300,30" font="Regular;{font_size}"/>
            
            <widget name="subtitle_label" position="{label_x},150" size="300,30" font="Regular;{font_size}" text="Subtitles"/>
            <widget name="subtitle_toggle" position="{value_x},150" size="300,30" font="Regular;{font_size}"/>
            
            <widget name="aspect_label" position="{label_x},200" size="300,30" font="Regular;{font_size}" text="Aspect Ratio"/>
            <widget name="aspect_mode" position="{value_x},200" size="300,30" font="Regular;{font_size}"/>
            
            <widget name="deinterlace_label" position="{label_x},250" size="300,30" font="Regular;{font_size}" text="Deinterlace"/>
            <widget name="deinterlace_toggle" position="{value_x},250" size="300,30" font="Regular;{font_size}"/>
            
            <widget name="cache_label" position="{label_x},300" size="300,30" font="Regular;{font_size}" text="Cache Size"/>
            <widget name="cache_mode" position="{value_x},300" size="300,30" font="Regular;{font_size}"/>
            
            <widget name="volume_label" position="{label_x},350" size="300,30" font="Regular;{font_size}" text="Default Volume"/>
            <widget name="volume_value" position="{value_x},350" size="300,30" font="Regular;{font_size}"/>
            
            <!-- Key Help -->
            <widget source="key_red" render="Label" position="{key1_x},{key_y}" size="{key_width},40" font="Regular;{key_font}" backgroundColor="red" halign="center"/>
            <widget source="key_green" render="Label" position="{key2_x},{key_y}" size="{key_width},40" font="Regular;{key_font}" backgroundColor="green" halign="center"/>
            <widget source="key_blue" render="Label" position="{key3_x},{key_y}" size="{key_width},40" font="Regular;{key_font}" backgroundColor="blue" halign="center"/>
        </screen>
        """.format(
            width=screen_width,
            height=screen_height,
            title_x=50 if screen_width >= 800 else 20,
            title_y=30 if screen_height >= 600 else 20,
            title_width=screen_width-100 if screen_width >= 800 else screen_width-40,
            title_font=28 if screen_width >= 800 else 22,
            label_x=50 if screen_width >= 800 else 30,
            value_x=400 if screen_width >= 800 else 300,
            font_size=24 if screen_width >= 800 else 18,
            key_y=screen_height-80 if screen_height >= 600 else screen_height-60,
            key1_x=100 if screen_width >= 800 else 50,
            key2_x=350 if screen_width >= 800 else 225,
            key3_x=600 if screen_width >= 800 else 400,
            key_width=200 if screen_width >= 800 else 150,
            key_font=24 if screen_width >= 800 else 20,
            plugin_name=PLUGIN_NAME,
            version=PLUGIN_VERSION
        )
    
    skin = get_skin()
    
    def __init__(self, session):
        try:
            Screen.__init__(self, session)
            self.session = session
            
            # Load configuration
            self.config = {}
            if MEDIA_UTILS_AVAILABLE:
                self.config = media_config.get_config('mediaplayer')
            else:
                # Default configuration
                self.config = {
                    'auto_resume': True,
                    'subtitles': True,
                    'aspect_ratio': 'auto',
                    'deinterlace': True,
                    'cache_size': 'medium',
                    'volume': 80
                }
            
            self.setupWidgets()
            self.setupActions()
            self.updateDisplay()
            
            debug_print(f"MediaPlayerSettings v{PLUGIN_VERSION}: Initialized")
            
        except Exception as e:
            debug_print(f"MediaPlayerSettings init error: {e}")
            import traceback
            traceback.print_exc()
    
    def setupWidgets(self):
        """Setup screen widgets"""
        try:
            self["title"] = Label(_("Media Player Settings"))
            
            self["auto_resume_label"] = Label(_("Auto-resume playback:"))
            self["auto_resume_toggle"] = Label(_("On") if self.config.get('auto_resume', True) else _("Off"))
            
            self["subtitle_label"] = Label(_("Show subtitles:"))
            self["subtitle_toggle"] = Label(_("On") if self.config.get('subtitles', True) else _("Off"))
            
            self["aspect_label"] = Label(_("Aspect ratio:"))
            self["aspect_mode"] = Label(self.config.get('aspect_ratio', 'auto'))
            
            self["deinterlace_label"] = Label(_("Deinterlace video:"))
            self["deinterlace_toggle"] = Label(_("On") if self.config.get('deinterlace', True) else _("Off"))
            
            self["cache_label"] = Label(_("Cache size:"))
            self["cache_mode"] = Label(self.config.get('cache_size', 'medium'))
            
            self["volume_label"] = Label(_("Default volume:"))
            self["volume_value"] = Label(f"{self.config.get('volume', 80)}%")
            
            self["key_red"] = StaticText(_("Cancel"))
            self["key_green"] = StaticText(_("Save"))
            self["key_blue"] = StaticText(_("Defaults"))
            
        except Exception as e:
            debug_print(f"setupWidgets error: {e}")
    
    def setupActions(self):
        """Setup action map"""
        try:
            self["actions"] = ActionMap(["ColorActions", "SetupActions"],
            {
                "cancel": self.cancel,
                "red": self.cancel,
                "green": self.save,
                "blue": self.defaults,
                "ok": self.editSetting,
                "up": self.up,
                "down": self.down,
            }, -1)
        except Exception as e:
            debug_print(f"setupActions error: {e}")
    
    def updateDisplay(self):
        """Update display with current values"""
        try:
            self["auto_resume_toggle"].setText(_("On") if self.config.get('auto_resume', True) else _("Off"))
            self["subtitle_toggle"].setText(_("On") if self.config.get('subtitles', True) else _("Off"))
            self["aspect_mode"].setText(self.config.get('aspect_ratio', 'auto'))
            self["deinterlace_toggle"].setText(_("On") if self.config.get('deinterlace', True) else _("Off"))
            self["cache_mode"].setText(self.config.get('cache_size', 'medium'))
            self["volume_value"].setText(f"{self.config.get('volume', 80)}%")
        except Exception as e:
            debug_print(f"updateDisplay error: {e}")
    
    def editSetting(self):
        """Edit the selected setting"""
        try:
            from Screens.ChoiceBox import ChoiceBox
            
            settings = [
                (_("Auto-resume"), "auto_resume", "toggle"),
                (_("Subtitles"), "subtitles", "toggle"),
                (_("Aspect ratio"), "aspect_ratio", "choice"),
                (_("Deinterlace"), "deinterlace", "toggle"),
                (_("Cache size"), "cache_size", "choice"),
                (_("Default volume"), "volume", "number"),
            ]
            
            self.session.openWithCallback(
                self.settingSelected,
                ChoiceBox,
                title=_("Select setting to edit"),
                list=[(name, (key, type)) for name, key, type in settings]
            )
        except Exception as e:
            debug_print(f"editSetting error: {e}")
            self.showMessage(_("Error editing setting"))
    
    def settingSelected(self, choice):
        """Handle setting selection"""
        try:
            if choice:
                setting_key, setting_type = choice[1]
                
                if setting_type == "toggle":
                    # Toggle boolean setting
                    current = self.config.get(setting_key, True)
                    self.config[setting_key] = not current
                    self.updateDisplay()
                    debug_print(f"Toggled {setting_key}: {self.config[setting_key]}")
                
                elif setting_type == "choice":
                    # Show choices for selection setting
                    if setting_key == "aspect_ratio":
                        choices = [
                            ("auto", _("Auto")),
                            ("4:3", "4:3"),
                            ("16:9", "16:9"),
                            ("original", _("Original")),
                        ]
                    elif setting_key == "cache_size":
                        choices = [
                            ("small", _("Small")),
                            ("medium", _("Medium")),
                            ("large", _("Large")),
                        ]
                    else:
                        choices = []
                    
                    if choices:
                        self.session.openWithCallback(
                            lambda value: self.choiceSelected(setting_key, value),
                            ChoiceBox,
                            title=_("Select {}").format(setting_key.replace("_", " ")),
                            list=choices
                        )
                
                elif setting_type == "number":
                    # Edit numeric value
                    from Screens.InputBox import InputBox
                    current_value = self.config.get(setting_key, 80)
                    self.session.openWithCallback(
                        lambda value: self.numberSelected(setting_key, value),
                        InputBox,
                        title=_("Enter {} (0-100)").format(setting_key.replace("_", " ")),
                        text=str(current_value)
                    )
                    
        except Exception as e:
            debug_print(f"settingSelected error: {e}")
    
    def choiceSelected(self, setting_key, value):
        """Handle choice selection"""
        try:
            if value:
                self.config[setting_key] = value[1]
                self.updateDisplay()
                debug_print(f"Set {setting_key} to {value[1]}")
        except Exception as e:
            debug_print(f"choiceSelected error: {e}")
    
    def numberSelected(self, setting_key, value):
        """Handle number input"""
        try:
            if value:
                try:
                    num_value = int(value)
                    if setting_key == "volume":
                        num_value = max(0, min(100, num_value))
                    self.config[setting_key] = num_value
                    self.updateDisplay()
                    debug_print(f"Set {setting_key} to {num_value}")
                except ValueError:
                    self.showMessage(_("Invalid number"))
        except Exception as e:
            debug_print(f"numberSelected error: {e}")
    
    def save(self):
        """Save settings"""
        try:
            # Save to media config
            if MEDIA_UTILS_AVAILABLE:
                for key, value in self.config.items():
                    media_config.set_config('mediaplayer', key, value)
                
                # Save to file
                config_file = "/tmp/westy_media_config.json"
                media_config.save_to_file(config_file)
                debug_print(f"Settings saved to {config_file}")
            
            self.showMessage(_("Settings saved"))
            self.close()
            
        except Exception as e:
            debug_print(f"save error: {e}")
            self.showMessage(_("Error saving settings"))
    
    def cancel(self):
        """Cancel changes"""
        try:
            self.close()
            debug_print("Settings cancelled")
        except Exception as e:
            debug_print(f"cancel error: {e}")
    
    def defaults(self):
        """Reset to default values"""
        try:
            # Reset to defaults
            default_config = {
                'auto_resume': True,
                'subtitles': True,
                'aspect_ratio': 'auto',
                'deinterlace': True,
                'cache_size': 'medium',
                'volume': 80
            }
            
            self.config.update(default_config)
            self.updateDisplay()
            self.showMessage(_("Defaults restored"))
            debug_print("Settings reset to defaults")
            
        except Exception as e:
            debug_print(f"defaults error: {e}")
    
    def up(self):
        """Handle up navigation"""
        try:
            # Simple navigation
            pass
        except Exception as e:
            debug_print(f"up error: {e}")
    
    def down(self):
        """Handle down navigation"""
        try:
            # Simple navigation
            pass
        except Exception as e:
            debug_print(f"down error: {e}")
    
    def showMessage(self, message):
        """Show message to user"""
        try:
            from Screens.MessageBox import MessageBox
            self.session.open(MessageBox, message, MessageBox.TYPE_INFO, timeout=2)
        except Exception as e:
            debug_print(f"showMessage error: {e}")


# Test function
if __name__ == "__main__":
    print(f"{PLUGIN_NAME} Media Player Settings v{PLUGIN_VERSION}")
    print("=" * 60)
    
    print("Settings Configuration:")
    print("  • Auto-resume playback")
    print("  • Subtitle display")
    print("  • Aspect ratio control")
    print("  • Video deinterlace")
    print("  • Cache size settings")
    print("  • Default volume level")
    
    print("\n" + "=" * 60)
    print("MediaPlayerSettings module ready for v2.1.0 integration")