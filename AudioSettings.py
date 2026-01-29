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
    debug_print(f"AudioSettings: Imported plugin utilities v{PLUGIN_VERSION}")
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
    debug_print("AudioSettings: Media utilities available")
except ImportError:
    MEDIA_UTILS_AVAILABLE = False
    debug_print("AudioSettings: Media utilities not available")

# Try to import Screens with fallbacks
try:
    from Screens.Screen import Screen
    SCREEN_AVAILABLE = True
    debug_print("AudioSettings: Screen available")
except ImportError:
    SCREEN_AVAILABLE = False
    debug_print("AudioSettings: Screen not available")
    
    class Screen:
        def __init__(self, session):
            self.session = session
        
        def close(self):
            pass

try:
    from Components.ActionMap import ActionMap
    ACTIONMAP_AVAILABLE = True
    debug_print("AudioSettings: ActionMap available")
except ImportError:
    ACTIONMAP_AVAILABLE = False
    debug_print("AudioSettings: ActionMap not available")
    
    class ActionMap:
        def __init__(self, contexts, actions, prio=-1):
            pass

try:
    from Components.Label import Label
    from Components.Sources.StaticText import StaticText
    COMPONENTS_AVAILABLE = True
    debug_print("AudioSettings: Basic components available")
except ImportError:
    COMPONENTS_AVAILABLE = False
    debug_print("AudioSettings: Basic components not available")
    
    class Label:
        def setText(self, text):
            pass
    
    class StaticText:
        def __init__(self, text=""):
            self.text = text

try:
    from enigma import getDesktop
    ENIGMA_AVAILABLE = True
    debug_print("AudioSettings: Enigma available")
except ImportError:
    ENIGMA_AVAILABLE = False
    debug_print("AudioSettings: Enigma not available")
    
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

class WestyAudioSettings(Screen):
    """Audio settings screen - v2.1.0"""
    
    # Dynamic skin based on screen size
    @staticmethod
    def get_skin():
        """Generate skin based on desktop size"""
        try:
            desktop = getDesktop(0)
            screen_width, screen_height = desktop.size().width(), desktop.size().height()
        except:
            screen_width, screen_height = 900, 700
        
        return """
        <screen name="WestyAudioSettings" position="center,center" size="{width},{height}" title="{plugin_name} Audio Settings v{version}">
            <widget name="title" position="{title_x},{title_y}" size="{title_width},40" font="Regular;{title_font}" halign="center"/>
            
            <!-- Audio Output -->
            <widget name="output_label" position="{label_x},100" size="200,30" font="Regular;{font_size}" text="Audio Output"/>
            <widget name="output_mode" position="{value_x},100" size="{value_width},30" font="Regular;{font_size}"/>
            
            <!-- Volume Control -->
            <widget name="volume_label" position="{label_x},150" size="200,30" font="Regular;{font_size}" text="Volume"/>
            <widget name="volume_slider" position="{value_x},150" size="{value_width},30"/>
            
            <!-- Balance -->
            <widget name="balance_label" position="{label_x},200" size="200,30" font="Regular;{font_size}" text="Balance"/>
            <widget name="balance_slider" position="{value_x},200" size="{value_width},30"/>
            
            <!-- Bass Boost -->
            <widget name="bass_label" position="{label_x},250" size="200,30" font="Regular;{font_size}" text="Bass Boost"/>
            <widget name="bass_toggle" position="{value_x},250" size="{value_width},30"/>
            
            <!-- Surround Sound -->
            <widget name="surround_label" position="{label_x},300" size="200,30" font="Regular;{font_size}" text="Surround"/>
            <widget name="surround_toggle" position="{value_x},300" size="{value_width},30"/>
            
            <!-- Key Help -->
            <widget source="key_red" render="Label" position="{key1_x},{key_y}" size="{key_width},40" font="Regular;{key_font}" backgroundColor="red" halign="center"/>
            <widget source="key_green" render="Label" position="{key2_x},{key_y}" size="{key_width},40" font="Regular;{key_font}" backgroundColor="green" halign="center"/>
            <widget source="key_blue" render="Label" position="{key3_x},{key_y}" size="{key_width},40" font="Regular;{key_font}" backgroundColor="blue" halign="center"/>
        </screen>
        """.format(
            width=screen_width,
            height=screen_height,
            title_x=50 if screen_width >= 900 else 20,
            title_y=30 if screen_height >= 700 else 20,
            title_width=screen_width-100 if screen_width >= 900 else screen_width-40,
            title_font=28 if screen_width >= 900 else 22,
            label_x=50 if screen_width >= 900 else 30,
            value_x=300 if screen_width >= 900 else 200,
            value_width=500 if screen_width >= 900 else 450,
            font_size=24 if screen_width >= 900 else 18,
            key_y=screen_height-80 if screen_height >= 700 else screen_height-60,
            key1_x=100 if screen_width >= 900 else 50,
            key2_x=350 if screen_width >= 900 else 260,
            key3_x=600 if screen_width >= 900 else 470,
            key_width=200 if screen_width >= 900 else 180,
            key_font=24 if screen_width >= 900 else 20,
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
                self.config = media_config.get_config('audiosettings')
            else:
                # Default configuration
                self.config = {
                    'audio_output': 'stereo',
                    'volume': 80,
                    'balance': 50,
                    'bass_boost': False,
                    'surround': False,
                }
            
            self.setupWidgets()
            self.setupActions()
            self.updateDisplay()
            
            debug_print(f"AudioSettings v{PLUGIN_VERSION}: Initialized")
            
        except Exception as e:
            debug_print(f"AudioSettings init error: {e}")
            import traceback
            traceback.print_exc()
    
    def setupWidgets(self):
        """Setup screen widgets"""
        try:
            self["title"] = Label(_("Audio Settings"))
            
            self["output_label"] = Label(_("Audio Output:"))
            self["output_mode"] = Label(self.config.get('audio_output', 'stereo').title())
            
            self["volume_label"] = Label(_("Volume:"))
            self["volume_slider"] = Label(f"{self.config.get('volume', 80)}%")
            
            self["balance_label"] = Label(_("Balance:"))
            balance = self.config.get('balance', 50)
            balance_text = f"L {balance} R"
            self["balance_slider"] = Label(balance_text)
            
            self["bass_label"] = Label(_("Bass Boost:"))
            self["bass_toggle"] = Label(_("On") if self.config.get('bass_boost', False) else _("Off"))
            
            self["surround_label"] = Label(_("Surround Sound:"))
            self["surround_toggle"] = Label(_("On") if self.config.get('surround', False) else _("Off"))
            
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
                "left": self.left,
                "right": self.right,
                "up": self.up,
                "down": self.down,
            }, -1)
        except Exception as e:
            debug_print(f"setupActions error: {e}")
    
    def updateDisplay(self):
        """Update display with current values"""
        try:
            self["output_mode"].setText(self.config.get('audio_output', 'stereo').title())
            self["volume_slider"].setText(f"{self.config.get('volume', 80)}%")
            
            balance = self.config.get('balance', 50)
            self["balance_slider"].setText(f"L {balance} R")
            
            self["bass_toggle"].setText(_("On") if self.config.get('bass_boost', False) else _("Off"))
            self["surround_toggle"].setText(_("On") if self.config.get('surround', False) else _("Off"))
            
        except Exception as e:
            debug_print(f"updateDisplay error: {e}")
    
    def editSetting(self):
        """Edit current setting"""
        try:
            from Screens.ChoiceBox import ChoiceBox
            
            settings = [
                (_("Audio Output"), "audio_output", "choice"),
                (_("Volume"), "volume", "number"),
                (_("Balance"), "balance", "number"),
                (_("Bass Boost"), "bass_boost", "toggle"),
                (_("Surround Sound"), "surround", "toggle"),
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
                    current = self.config.get(setting_key, False)
                    self.config[setting_key] = not current
                    self.updateDisplay()
                    debug_print(f"Toggled {setting_key}: {self.config[setting_key]}")
                
                elif setting_type == "choice":
                    # Show choices for selection setting
                    if setting_key == "audio_output":
                        choices = [
                            ("stereo", _("Stereo")),
                            ("mono", _("Mono")),
                            ("surround", _("Surround")),
                        ]
                        
                        self.session.openWithCallback(
                            lambda value: self.choiceSelected(setting_key, value),
                            ChoiceBox,
                            title=_("Select audio output"),
                            list=choices
                        )
                
                elif setting_type == "number":
                    # Edit numeric value
                    from Screens.InputBox import InputBox
                    current_value = self.config.get(setting_key, 80 if setting_key == "volume" else 50)
                    min_val = 0
                    max_val = 100
                    
                    self.session.openWithCallback(
                        lambda value: self.numberSelected(setting_key, value, min_val, max_val),
                        InputBox,
                        title=_("Enter {} ({}-{})").format(setting_key.replace("_", " "), min_val, max_val),
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
    
    def numberSelected(self, setting_key, value, min_val, max_val):
        """Handle number input"""
        try:
            if value:
                try:
                    num_value = int(value)
                    if min_val <= num_value <= max_val:
                        self.config[setting_key] = num_value
                        self.updateDisplay()
                        debug_print(f"Set {setting_key} to {num_value}")
                    else:
                        self.showMessage(_("Value must be between {} and {}").format(min_val, max_val))
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
                    media_config.set_config('audiosettings', key, value)
                
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
                'audio_output': 'stereo',
                'volume': 80,
                'balance': 50,
                'bass_boost': False,
                'surround': False,
            }
            
            self.config.update(default_config)
            self.updateDisplay()
            self.showMessage(_("Defaults restored"))
            debug_print("Settings reset to defaults")
            
        except Exception as e:
            debug_print(f"defaults error: {e}")
    
    def left(self):
        """Handle left navigation"""
        try:
            # Would adjust selected value in real implementation
            pass
        except Exception as e:
            debug_print(f"left error: {e}")
    
    def right(self):
        """Handle right navigation"""
        try:
            # Would adjust selected value in real implementation
            pass
        except Exception as e:
            debug_print(f"right error: {e}")
    
    def up(self):
        """Handle up navigation"""
        try:
            # Would navigate to previous setting
            pass
        except Exception as e:
            debug_print(f"up error: {e}")
    
    def down(self):
        """Handle down navigation"""
        try:
            # Would navigate to next setting
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
    print(f"{PLUGIN_NAME} Audio Settings v{PLUGIN_VERSION}")
    print("=" * 60)
    
    print("Audio Settings Configuration:")
    print("  • Audio output mode (Stereo, Mono, Surround)")
    print("  • Volume level control")
    print("  • Left/Right balance")
    print("  • Bass boost enhancement")
    print("  • Surround sound simulation")
    
    print("\n" + "=" * 60)
    print("AudioSettings module ready for v2.1.0 integration")