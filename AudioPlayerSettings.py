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
    debug_print(f"AudioPlayerSettings: Imported plugin utilities v{PLUGIN_VERSION}")
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
    debug_print("AudioPlayerSettings: Media utilities available")
except ImportError:
    MEDIA_UTILS_AVAILABLE = False
    debug_print("AudioPlayerSettings: Media utilities not available")

# Try to import Screens with fallbacks
try:
    from Screens.Screen import Screen
    SCREEN_AVAILABLE = True
    debug_print("AudioPlayerSettings: Screen available")
except ImportError:
    SCREEN_AVAILABLE = False
    debug_print("AudioPlayerSettings: Screen not available")
    
    class Screen:
        def __init__(self, session):
            self.session = session
        
        def close(self):
            pass

try:
    from Components.ActionMap import ActionMap
    ACTIONMAP_AVAILABLE = True
    debug_print("AudioPlayerSettings: ActionMap available")
except ImportError:
    ACTIONMAP_AVAILABLE = False
    debug_print("AudioPlayerSettings: ActionMap not available")
    
    class ActionMap:
        def __init__(self, contexts, actions, prio=-1):
            pass

try:
    from Components.Label import Label
    from Components.Sources.StaticText import StaticText
    COMPONENTS_AVAILABLE = True
    debug_print("AudioPlayerSettings: Basic components available")
except ImportError:
    COMPONENTS_AVAILABLE = False
    debug_print("AudioPlayerSettings: Basic components not available")
    
    class Label:
        def setText(self, text):
            pass
    
    class StaticText:
        def __init__(self, text=""):
            self.text = text

try:
    from enigma import getDesktop
    ENIGMA_AVAILABLE = True
    debug_print("AudioPlayerSettings: Enigma available")
except ImportError:
    ENIGMA_AVAILABLE = False
    debug_print("AudioPlayerSettings: Enigma not available")
    
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

class WestyAudioPlayerSettings(Screen):
    """Audio player settings - v2.1.0"""
    
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
        <screen name="WestyAudioPlayerSettings" position="center,center" size="{width},{height}" title="{plugin_name} Audio Player Settings v{version}">
            <widget name="title" position="{title_x},{title_y}" size="{title_width},40" font="Regular;{title_font}" halign="center"/>
            
            <!-- Settings -->
            <widget name="auto_play_label" position="{label_x},100" size="300,30" font="Regular;{font_size}" text="Auto-play"/>
            <widget name="auto_play_toggle" position="{value_x},100" size="300,30" font="Regular;{font_size}"/>
            
            <widget name="crossfade_label" position="{label_x},150" size="300,30" font="Regular;{font_size}" text="Crossfade"/>
            <widget name="crossfade_toggle" position="{value_x},150" size="300,30" font="Regular;{font_size}"/>
            
            <widget name="replaygain_label" position="{label_x},200" size="300,30" font="Regular;{font_size}" text="Replay Gain"/>
            <widget name="replaygain_toggle" position="{value_x},200" size="300,30" font="Regular;{font_size}"/>
            
            <widget name="visualization_label" position="{label_x},250" size="300,30" font="Regular;{font_size}" text="Visualization"/>
            <widget name="visualization_toggle" position="{value_x},250" size="300,30" font="Regular;{font_size}"/>
            
            <widget name="gapless_label" position="{label_x},300" size="300,30" font="Regular;{font_size}" text="Gapless Playback"/>
            <widget name="gapless_toggle" position="{value_x},300" size="300,30" font="Regular;{font_size}"/>
            
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
                self.config = media_config.get_config('audioplayer')
            else:
                # Default configuration
                self.config = {
                    'auto_play': True,
                    'crossfade': False,
                    'replaygain': True,
                    'visualization': True,
                    'gapless': True,
                    'volume': 80
                }
            
            self.setupWidgets()
            self.setupActions()
            self.updateDisplay()
            
            debug_print(f"AudioPlayerSettings v{PLUGIN_VERSION}: Initialized")
            
        except Exception as e:
            debug_print(f"AudioPlayerSettings init error: {e}")
            import traceback
            traceback.print_exc()
    
    def setupWidgets(self):
        """Setup screen widgets"""
        try:
            self["title"] = Label(_("Audio Player Settings"))
            
            self["auto_play_label"] = Label(_("Auto-play next track:"))
            self["auto_play_toggle"] = Label(_("On") if self.config.get('auto_play', True) else _("Off"))
            
            self["crossfade_label"] = Label(_("Crossfade between tracks:"))
            self["crossfade_toggle"] = Label(_("On") if self.config.get('crossfade', False) else _("Off"))
            
            self["replaygain_label"] = Label(_("Replay Gain normalization:"))
            self["replaygain_toggle"] = Label(_("On") if self.config.get('replaygain', True) else _("Off"))
            
            self["visualization_label"] = Label(_("Visualization effects:"))
            self["visualization_toggle"] = Label(_("On") if self.config.get('visualization', True) else _("Off"))
            
            self["gapless_label"] = Label(_("Gapless playback:"))
            self["gapless_toggle"] = Label(_("On") if self.config.get('gapless', True) else _("Off"))
            
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
                "ok": self.toggleSetting,
                "up": self.up,
                "down": self.down,
            }, -1)
        except Exception as e:
            debug_print(f"setupActions error: {e}")
    
    def updateDisplay(self):
        """Update display with current values"""
        try:
            self["auto_play_toggle"].setText(_("On") if self.config.get('auto_play', True) else _("Off"))
            self["crossfade_toggle"].setText(_("On") if self.config.get('crossfade', False) else _("Off"))
            self["replaygain_toggle"].setText(_("On") if self.config.get('replaygain', True) else _("Off"))
            self["visualization_toggle"].setText(_("On") if self.config.get('visualization', True) else _("Off"))
            self["gapless_toggle"].setText(_("On") if self.config.get('gapless', True) else _("Off"))
            self["volume_value"].setText(f"{self.config.get('volume', 80)}%")
        except Exception as e:
            debug_print(f"updateDisplay error: {e}")
    
    def toggleSetting(self):
        """Toggle the selected setting"""
        try:
            from Screens.ChoiceBox import ChoiceBox
            
            settings = [
                (_("Auto-play"), "auto_play"),
                (_("Crossfade"), "crossfade"),
                (_("Replay Gain"), "replaygain"),
                (_("Visualization"), "visualization"),
                (_("Gapless"), "gapless"),
                (_("Default volume"), "volume"),
            ]
            
            self.session.openWithCallback(
                self.settingSelected,
                ChoiceBox,
                title=_("Select setting to edit"),
                list=[(name, key) for name, key in settings]
            )
        except Exception as e:
            debug_print(f"toggleSetting error: {e}")
            self.showMessage(_("Error editing setting"))
    
    def settingSelected(self, choice):
        """Handle setting selection"""
        try:
            if choice:
                setting_key = choice[1]
                
                if setting_key == "volume":
                    # Edit volume as number
                    from Screens.InputBox import InputBox
                    current_value = self.config.get(setting_key, 80)
                    self.session.openWithCallback(
                        lambda value: self.volumeSelected(value),
                        InputBox,
                        title=_("Enter default volume (0-100)"),
                        text=str(current_value)
                    )
                else:
                    # Toggle boolean setting
                    current = self.config.get(setting_key, True)
                    self.config[setting_key] = not current
                    self.updateDisplay()
                    debug_print(f"Toggled {setting_key}: {self.config[setting_key]}")
                    
        except Exception as e:
            debug_print(f"settingSelected error: {e}")
    
    def volumeSelected(self, value):
        """Handle volume input"""
        try:
            if value:
                try:
                    volume = int(value)
                    volume = max(0, min(100, volume))
                    self.config['volume'] = volume
                    self.updateDisplay()
                    debug_print(f"Set volume to {volume}%")
                except ValueError:
                    self.showMessage(_("Invalid number"))
        except Exception as e:
            debug_print(f"volumeSelected error: {e}")
    
    def save(self):
        """Save settings"""
        try:
            # Save to media config
            if MEDIA_UTILS_AVAILABLE:
                for key, value in self.config.items():
                    media_config.set_config('audioplayer', key, value)
                
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
                'auto_play': True,
                'crossfade': False,
                'replaygain': True,
                'visualization': True,
                'gapless': True,
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
    print(f"{PLUGIN_NAME} Audio Player Settings v{PLUGIN_VERSION}")
    print("=" * 60)
    
    print("Settings Configuration:")
    print("  • Auto-play next track")
    print("  • Crossfade between tracks")
    print("  • Replay Gain normalization")
    print("  • Visualization effects")
    print("  • Gapless playback")
    print("  • Default volume level")
    
    print("\n" + "=" * 60)
    print("AudioPlayerSettings module ready for v2.1.0 integration")