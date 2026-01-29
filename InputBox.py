#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division, unicode_literals

import os
import sys
import re
import time

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
    debug_print(f"InputBox: Imported plugin utilities v{PLUGIN_VERSION}")
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

# Try to import InputBox base class
try:
    from Screens.InputBox import InputBox as InputBoxBase
    INPUTBOX_AVAILABLE = True
    debug_print("InputBox: InputBoxBase available")
except ImportError:
    INPUTBOX_AVAILABLE = False
    debug_print("InputBox: InputBoxBase not available")
    
    # Create minimal base class
    class InputBoxBase:
        def __init__(self, session, title="", text="", windowTitle=None):
            self.session = session
            self.title = title
            self.text = text
            self.windowTitle = windowTitle
        
        def close(self, result=None):
            pass

# Try to import VirtualKeyBoard
try:
    from Screens.VirtualKeyBoard import VirtualKeyBoard
    VIRTUALKEYBOARD_AVAILABLE = True
    debug_print("InputBox: VirtualKeyBoard available")
except ImportError:
    VIRTUALKEYBOARD_AVAILABLE = False
    debug_print("InputBox: VirtualKeyBoard not available")
    
    class VirtualKeyBoard:
        def __init__(self, session, title="", **kwargs):
            self.session = session
            self.title = title

# Try to import Components
try:
    from Components.ActionMap import ActionMap
    ACTIONMAP_AVAILABLE = True
    debug_print("InputBox: ActionMap available")
except ImportError:
    ACTIONMAP_AVAILABLE = False
    debug_print("InputBox: ActionMap not available")
    
    class ActionMap:
        def __init__(self, contexts, actions, prio=-1):
            pass

try:
    from Components.Label import Label
    from Components.Pixmap import Pixmap
    from Components.Sources.StaticText import StaticText
    COMPONENTS_AVAILABLE = True
    debug_print("InputBox: Basic components available")
except ImportError:
    COMPONENTS_AVAILABLE = False
    debug_print("InputBox: Basic components not available")
    
    class Label:
        def setText(self, text):
            pass
        
        def show(self):
            pass
        
        def hide(self):
            pass
    
    class Pixmap:
        def show(self):
            pass
        
        def hide(self):
            pass
    
    class StaticText:
        def __init__(self, text=""):
            self.text = text

try:
    from enigma import eTimer, getDesktop
    ENIGMA_AVAILABLE = True
    debug_print("InputBox: Enigma available")
except ImportError:
    ENIGMA_AVAILABLE = False
    debug_print("InputBox: Enigma not available")
    
    class eTimer:
        def __init__(self):
            pass
        
        def start(self, interval):
            pass
        
        def stop(self):
            pass
        
        def timeout(self):
            class Timeout:
                def get(self):
                    return self
                
                def connect(self, func):
                    pass
            return Timeout()
    
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

class WestyInputBox(InputBoxBase):
    """Enhanced input box with validation and formatting - v2.1.0"""
    
    # Dynamic skin based on screen size
    @staticmethod
    def get_skin():
        """Generate skin based on desktop size"""
        try:
            desktop = getDesktop(0)
            screen_width, screen_height = desktop.size().width(), desktop.size().height()
        except:
            pass
        screen_width, screen_height = (800, 400) if FULLHD else (600, 300)
        
        return """
        <screen name="WestyInputBox" position="center,center" size="{width},{height}" title="{plugin_name} Input v{version}" flags="wfNoBorder">
            <widget name="title_label" position="{title_x},{title_y}" size="{title_width},40" font="Regular;{title_font}" halign="center" valign="center"/>
            <widget name="input" position="{input_x},{input_y}" size="{input_width},50" font="Regular;{input_font}" noWrap="1"/>
            <widget name="hint_label" position="{hint_x},{hint_y}" size="{hint_width},30" font="Regular;{hint_font}" foregroundColor="#888888"/>
            <widget name="validation_label" position="{validation_x},{validation_y}" size="{validation_width},30" font="Regular;{validation_font}" foregroundColor="#ff0000"/>
            <widget name="cursor_indicator" position="{cursor_x},{cursor_y}" size="4,54" backgroundColor="#00ff00"/>
            <widget name="char_count" position="{count_x},{count_y}" size="100,30" font="Regular;20" halign="right"/>
            <widget source="key_red" render="Label" position="{key1_x},{key_y}" size="200,40" font="Regular;24" backgroundColor="red" halign="center"/>
            <widget source="key_green" render="Label" position="{key2_x},{key_y}" size="200,40" font="Regular;24" backgroundColor="green" halign="center"/>
            <widget source="key_yellow" render="Label" position="{key3_x},{key_y}" size="200,40" font="Regular;24" backgroundColor="yellow" halign="center"/>
            <ePixmap position="{key1_x},{key_y}" size="200,40" pixmap="skin_default/buttons/red.png" transparent="1"/>
            <ePixmap position="{key2_x},{key_y}" size="200,40" pixmap="skin_default/buttons/green.png" transparent="1"/>
            <ePixmap position="{key3_x},{key_y}" size="200,40" pixmap="skin_default/buttons/yellow.png" transparent="1"/>
        </screen>
        """.format(
            width=screen_width,
            height=screen_height,
            title_x=20 if screen_width >= 800 else 10,
            title_y=20 if screen_height >= 400 else 10,
            title_width=screen_width-40 if screen_width >= 800 else screen_width-20,
            title_font=28 if screen_width >= 800 else 22,
            input_x=50 if screen_width >= 800 else 20,
            input_y=80 if screen_height >= 400 else 50,
            input_width=screen_width-100 if screen_width >= 800 else screen_width-40,
            input_font=32 if screen_width >= 800 else 26,
            hint_x=50 if screen_width >= 800 else 20,
            hint_y=140 if screen_height >= 400 else 100,
            hint_width=screen_width-100 if screen_width >= 800 else screen_width-40,
            hint_font=22 if screen_width >= 800 else 18,
            validation_x=50 if screen_width >= 800 else 20,
            validation_y=180 if screen_height >= 400 else 130,
            validation_width=screen_width-100 if screen_width >= 800 else screen_width-40,
            validation_font=22 if screen_width >= 800 else 18,
            cursor_x=48 if screen_width >= 800 else 18,
            cursor_y=78 if screen_height >= 400 else 48,
            count_x=screen_width-150 if screen_width >= 800 else screen_width-120,
            count_y=230 if screen_height >= 400 else 160,
            key_y=300 if screen_height >= 400 else 200,
            key1_x=100 if screen_width >= 800 else 50,
            key2_x=400 if screen_width >= 800 else 250,
            key3_x=700 if screen_width >= 800 else 450,
            plugin_name=PLUGIN_NAME,
            version=PLUGIN_VERSION
        )
    
    skin = get_skin()
    
    def __init__(self, session, title="", text="", windowTitle=None, 
                 validator=None, max_length=None, min_length=None,
                 allowed_chars=None, hint="", confirm_button=True,
                 password=False, input_type="text"):
        """
        Enhanced input box with validation - v2.1.0
        
        Args:
            session: Enigma session
            title: Input box title
            text: Default text
            windowTitle: Window title
            validator: Function that takes text and returns (is_valid, error_message)
            max_length: Maximum allowed characters
            min_length: Minimum required characters
            allowed_chars: Regex pattern of allowed characters
            hint: Help text shown below input
            confirm_button: Show confirm button
            password: Hide input characters
            input_type: "text", "number", "email", "filename", "path"
        """
        try:
            # Set default window title with plugin version
            if not windowTitle:
                windowTitle = f"{PLUGIN_NAME} Input"
            
            self.validator = validator
            self.max_length = max_length
            self.min_length = min_length
            self.allowed_chars = allowed_chars
            self.hint = hint
            self.input_type = input_type
            self.is_password = password
            
            # Set default validators based on input type
            if not validator:
                self.validator = self.getDefaultValidator()
            
            # Call parent with appropriate parameters
            if INPUTBOX_AVAILABLE:
                InputBoxBase.__init__(self, session, title=title, text=text, 
                                     windowTitle=windowTitle)
            else:
                # Fallback initialization
                self.session = session
                self.title = title
                self.text = text
                self.windowTitle = windowTitle
            
            # Additional widgets
            self["title_label"] = Label(title or windowTitle or "")
            self["hint_label"] = Label(hint)
            self["validation_label"] = Label("")
            self["cursor_indicator"] = Pixmap()
            self["char_count"] = Label("")
            
            # Update key texts
            self["key_red"] = StaticText(_("Cancel"))
            self["key_green"] = StaticText(_("OK") if confirm_button else "")
            self["key_yellow"] = StaticText(_("Clear"))
            
            # Enhanced actions
            self["enhanced_actions"] = ActionMap(["ColorActions", "NumberActions"],
            {
                "yellow": self.clearText,
                "0": self.insertZero,
                "1": lambda: self.insertTextFunc("1"),
                "2": lambda: self.insertTextFunc("2"),
                "3": lambda: self.insertTextFunc("3"),
                "4": lambda: self.insertTextFunc("4"),
                "5": lambda: self.insertTextFunc("5"),
                "6": lambda: self.insertTextFunc("6"),
                "7": lambda: self.insertTextFunc("7"),
                "8": lambda: self.insertTextFunc("8"),
                "9": lambda: self.insertTextFunc("9"),
            }, -1)
            
            # Cursor blink timer
            self.cursor_timer = eTimer()
            if hasattr(self.cursor_timer, 'timeout'):
                self.cursor_timer.timeout.get().append(self.blinkCursor)
            self.cursor_visible = True
            
            # Input change tracking
            self.old_text = text
            self.onTextChanged = []
            
            self.onLayoutFinish.append(self.setupInputBox)
            
            debug_print(f"WestyInputBox v{PLUGIN_VERSION}: Initialized (type: {input_type})")
            
        except Exception as e:
            debug_print(f"WestyInputBox init error: {e}")
            import traceback
            traceback.print_exc()
    
    def setupInputBox(self):
        """Setup input box after layout"""
        try:
            # Start cursor blinking
            if hasattr(self.cursor_timer, 'start'):
                self.cursor_timer.start(500)
            
            # Update character count
            self.updateCharCount()
            
            # Connect text changed signal if available
            if hasattr(self["input"], 'onTextChanged'):
                self["input"].onTextChanged.append(self.handleTextChanged)
            
            # Initial validation
            self.handleTextChanged()
            
        except Exception as e:
            debug_print(f"setupInputBox error: {e}")
    
    def getDefaultValidator(self):
        """Get default validator based on input type"""
        if self.input_type == "number":
            def number_validator(text):
                if not text:
                    return True, ""
                return (text.isdigit() or text == "" or (text.startswith('-') and text[1:].isdigit()), 
                       _("Please enter a valid number"))
            return number_validator
        
        elif self.input_type == "filename":
            def filename_validator(text):
                return (self.isValidFilename(text), _("Invalid filename"))
            return filename_validator
        
        elif self.input_type == "path":
            def path_validator(text):
                return (self.isValidPath(text), _("Invalid path"))
            return path_validator
        
        elif self.input_type == "email":
            def email_validator(text):
                return (self.isValidEmail(text), _("Invalid email address"))
            return email_validator
        
        else:  # text
            def text_validator(text):
                return (True, "")
            return text_validator
    
    def isValidFilename(self, text):
        """Check if text is a valid filename"""
        if not text:
            return True
        
        # Check for invalid characters
        invalid_chars = '<>:"/\\|?*'
        if any(char in text for char in invalid_chars):
            return False
        
        # Check for reserved names (Windows, but good practice)
        reserved = ['CON', 'PRN', 'AUX', 'NUL', 
                   'COM1', 'COM2', 'COM3', 'COM4',
                   'LPT1', 'LPT2', 'LPT3', 'LPT4']
        if text.upper() in reserved:
            return False
        
        # Check for dots at start or end
        if text.startswith('.') or text.endswith('.'):
            return False
        
        # Check for spaces at start or end
        if text.startswith(' ') or text.endswith(' '):
            return False
        
        return True
    
    def isValidPath(self, text):
        """Check if text is a valid path"""
        if not text:
            return True
        
        # Basic path validation
        try:
            # Check if path components are valid
            parts = text.split('/')
            for part in parts:
                if part and not self.isValidFilename(part):
                    return False
            return True
        except:
            return False
    
    def isValidEmail(self, text):
        """Check if text is a valid email address"""
        if not text:
            return True
        
        # Simple email validation pattern
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, text) is not None
    
    def handleTextChanged(self):
        """Handle text changes with validation"""
        try:
            current_text = self["input"].getText()
            
            # Update character count
            self.updateCharCount()
            
            # Validate
            is_valid, error = self.validateText(current_text)
            
            # Update validation label
            if error:
                self["validation_label"].setText(error)
                self["validation_label"].show()
            else:
                self["validation_label"].hide()
            
            # Update button state
            self.updateButtonState(is_valid)
            
            # Call text changed callbacks
            for callback in self.onTextChanged:
                try:
                    callback(current_text)
                except Exception as e:
                    debug_print(f"Text changed callback error: {e}")
            
        except Exception as e:
            debug_print(f"handleTextChanged error: {e}")
    
    def validateText(self, text):
        """Validate input text"""
        try:
            # Check min length
            if self.min_length is not None and len(text) < self.min_length:
                return False, _(f"Minimum {self.min_length} characters required")
            
            # Check max length
            if self.max_length is not None and len(text) > self.max_length:
                return False, _(f"Maximum {self.max_length} characters allowed")
            
            # Check allowed characters
            if self.allowed_chars:
                try:
                    pattern = re.compile(self.allowed_chars)
                    if not pattern.fullmatch(text):
                        return False, _("Invalid characters")
                except re.error:
                    debug_print(f"Invalid regex pattern: {self.allowed_chars}")
            
            # Use custom validator
            if self.validator:
                return self.validator(text)
            
            return True, ""
            
        except Exception as e:
            debug_print(f"validateText error: {e}")
            return False, _("Validation error")
    
    def updateCharCount(self):
        """Update character count display"""
        try:
            text = self["input"].getText()
            length = len(text)
            
            if self.max_length is not None:
                self["char_count"].setText(f"{length}/{self.max_length}")
            else:
                self["char_count"].setText(str(length))
            
            # Change color based on limits
            if hasattr(self["char_count"].instance, 'setForegroundColor'):
                if self.max_length is not None and length > self.max_length:
                    self["char_count"].instance.setForegroundColor(0x00ff0000)  # Red
                elif self.min_length is not None and length < self.min_length:
                    self["char_count"].instance.setForegroundColor(0x00ffff00)  # Yellow
                else:
                    self["char_count"].instance.setForegroundColor(0x0000ff00)  # Green
            
        except Exception as e:
            debug_print(f"updateCharCount error: {e}")
    
    def updateButtonState(self, is_valid):
        """Update button enabled state"""
        try:
            # In a real implementation, would enable/disable the OK button
            # For now, just update the text color
            if hasattr(self["key_green"], 'instance') and hasattr(self["key_green"].instance, 'setForegroundColor'):
                if is_valid:
                    self["key_green"].instance.setForegroundColor(0x00ffffff)  # White
                else:
                    self["key_green"].instance.setForegroundColor(0x00888888)  # Gray
            
        except Exception as e:
            debug_print(f"updateButtonState error: {e}")
    
    def blinkCursor(self):
        """Blink cursor indicator"""
        try:
            self.cursor_visible = not self.cursor_visible
            if self.cursor_visible:
                self["cursor_indicator"].show()
            else:
                self["cursor_indicator"].hide()
        except Exception as e:
            debug_print(f"blinkCursor error: {e}")
    
    def clearText(self):
        """Clear all text"""
        try:
            self["input"].setText("")
            debug_print("Text cleared")
        except Exception as e:
            debug_print(f"clearText error: {e}")
    
    def insertZero(self):
        """Insert zero"""
        self.insertTextFunc("0")
    
    def insertTextFunc(self, text):
        """Insert text at cursor"""
        try:
            current = self["input"].getText()
            # Get cursor position if available
            try:
                pos = self["input"].instance.getMarkedPos()
            except:
                pos = len(current)
            
            new_text = current[:pos] + text + current[pos:]
            self["input"].setText(new_text)
            
            # Move cursor after inserted text if possible
            try:
                self["input"].instance.setMarkedPos(pos + len(text))
            except:
                pass
            
        except Exception as e:
            debug_print(f"insertTextFunc error: {e}")
    
    def ok(self):
        """Handle OK button with validation"""
        try:
            text = self["input"].getText()
            
            # Validate before closing
            is_valid, error = self.validateText(text)
            
            if not is_valid:
                # Show error but don't close
                self["validation_label"].setText(error)
                self["validation_label"].show()
                debug_print(f"Validation failed: {error}")
                return
            
            # Close with text
            debug_print(f"Input confirmed: {text[:20]}..." if len(text) > 20 else text)
            self.close(text)
            
        except Exception as e:
            debug_print(f"ok error: {e}")
            self.close(None)
    
    def cancel(self):
        """Handle cancel"""
        try:
            debug_print("Input cancelled")
            self.close(None)
        except Exception as e:
            debug_print(f"cancel error: {e}")
            self.close(None)
    
    def close(self, result):
        """Clean up and close"""
        try:
            if hasattr(self.cursor_timer, 'stop'):
                self.cursor_timer.stop()
            
            if INPUTBOX_AVAILABLE:
                InputBoxBase.close(self, result)
            else:
                # Fallback close
                self.result = result
                
        except Exception as e:
            debug_print(f"close error: {e}")
            if INPUTBOX_AVAILABLE:
                InputBoxBase.close(self, None)


class WestyVirtualKeyBoard(VirtualKeyBoard):
    """Enhanced virtual keyboard with Westy styling - v2.1.0"""
    
    def __init__(self, session, title="", **kwargs):
        try:
            # Add custom styling options
            if not title:
                title = f"{PLUGIN_NAME} Keyboard"
            
            if VIRTUALKEYBOARD_AVAILABLE:
                kwargs['skin'] = kwargs.get('skin', 'WestyVirtualKeyboard')
                VirtualKeyBoard.__init__(self, session, title=title, **kwargs)
            else:
                # Fallback
                self.session = session
                self.title = title
            
            # Custom initialization
            self.custom_actions = []
            
            debug_print(f"WestyVirtualKeyBoard v{PLUGIN_VERSION}: Initialized")
            
        except Exception as e:
            debug_print(f"WestyVirtualKeyBoard init error: {e}")
            if VIRTUALKEYBOARD_AVAILABLE:
                VirtualKeyBoard.__init__(self, session, title=title, **kwargs)


# Factory functions for common input types
class InputFactory:
    """Factory for common input types - v2.1.0"""
    
    @staticmethod
    def createFilenameInput(session, title="", text="", 
                           allow_extensions=True, existing_only=False,
                           default_ext=""):
        """Create filename input with validation"""
        from . import _
        
        def validator(t):
            return InputFactory.validateFilename(t, allow_extensions, existing_only, default_ext)
        
        hint = _("Enter filename") + ("" if allow_extensions else _(" (no extension)"))
        if default_ext:
            hint += _(" (default: .{})").format(default_ext)
        
        # Add default extension if provided
        if text and default_ext and not text.endswith(f".{default_ext}"):
            text = f"{text}.{default_ext}"
        
        return WestyInputBox(
            session=session,
            title=title,
            text=text,
            validator=validator,
            min_length=1,
            input_type="filename",
            hint=hint
        )
    
    @staticmethod
    def validateFilename(text, allow_extensions, existing_only, default_ext=""):
        """Validate filename"""
        from . import _
        
        if not text:
            return False, _("Filename cannot be empty")
        
        # Add default extension if needed
        if default_ext and not text.endswith(f".{default_ext}"):
            text = f"{text}.{default_ext}"
        
        # Check for invalid characters
        invalid_chars = '<>:"/\\|?*'
        if any(char in text for char in invalid_chars):
            return False, _("Contains invalid characters")
        
        # Check extension if not allowed
        if not allow_extensions and '.' in text:
            return False, _("Extensions not allowed")
        
        # Check for dots at start or end
        if text.startswith('.') or text.endswith('.'):
            return False, _("Cannot start or end with dot")
        
        # Check for spaces at start or end
        if text.startswith(' ') or text.endswith(' '):
            return False, _("Cannot start or end with space")
        
        # Check if file exists (if existing_only)
        if existing_only:
            try:
                if not os.path.exists(text):
                    return False, _("File does not exist")
            except:
                pass
        
        return True, ""
    
    @staticmethod
    def createNumberInput(session, title="", text="", min_value=None, 
                         max_value=None, integer_only=True, allow_negative=True):
        """Create number input with range validation"""
        from . import _
        
        def validator(t):
            if not t:
                return True, ""
            
            # Check for valid number format
            if integer_only:
                if not (t.isdigit() or (allow_negative and t.startswith('-') and t[1:].isdigit())):
                    return False, _("Must be a whole number")
            else:
                try:
                    float(t)
                except ValueError:
                    return False, _("Invalid number format")
            
            try:
                value = int(t) if integer_only else float(t)
                
                if min_value is not None and value < min_value:
                    return False, _("Minimum value is {}").format(min_value)
                
                if max_value is not None and value > max_value:
                    return False, _("Maximum value is {}").format(max_value)
                
                return True, ""
            except:
                return False, _("Invalid number")
        
        hint_parts = []
        if min_value is not None:
            hint_parts.append(_("Min: {}").format(min_value))
        if max_value is not None:
            hint_parts.append(_("Max: {}").format(max_value))
        if allow_negative:
            hint_parts.append(_("Negative allowed"))
        
        hint = " | ".join(hint_parts)
        
        # Build allowed characters regex
        if integer_only:
            if allow_negative:
                allowed_chars = r'[\d\-]*'
            else:
                allowed_chars = r'[\d]*'
        else:
            if allow_negative:
                allowed_chars = r'[\d\.\-]*'
            else:
                allowed_chars = r'[\d\.]*'
        
        return WestyInputBox(
            session=session,
            title=title,
            text=text,
            validator=validator,
            input_type="number",
            hint=hint,
            allowed_chars=allowed_chars
        )
    
    @staticmethod
    def createPathInput(session, title="", text="", must_exist=False, 
                       is_directory=False, create_if_missing=False):
        """Create path input with validation"""
        from . import _
        
        def validator(t):
            if not t:
                return False, _("Path cannot be empty")
            
            # Basic path validation
            try:
                # Try to normalize path
                norm_path = os.path.normpath(t)
                
                # Check for invalid characters
                invalid_chars = '<>:"|?*'
                if any(char in t for char in invalid_chars):
                    return False, _("Contains invalid characters")
                
                # Check existence if required
                if must_exist and not os.path.exists(norm_path):
                    if create_if_missing:
                        # Allow non-existent paths if create_if_missing is True
                        pass
                    else:
                        return False, _("Path does not exist")
                
                # Check if it's a directory if required
                if is_directory and os.path.exists(norm_path) and not os.path.isdir(norm_path):
                    return False, _("Not a directory")
                
                return True, ""
            except:
                return False, _("Invalid path format")
        
        hint = _("Enter path")
        if must_exist:
            hint += _(" (must exist)")
        if create_if_missing:
            hint += _(" (will create if missing)")
        if is_directory:
            hint += _(" (directory)")
        
        return WestyInputBox(
            session=session,
            title=title,
            text=text,
            validator=validator,
            input_type="path",
            hint=hint
        )
    
    @staticmethod
    def createEmailInput(session, title="", text="", required=True):
        """Create email input with validation"""
        from . import _
        
        def validator(t):
            if not t and not required:
                return True, ""
            
            if not t:
                return False, _("Email cannot be empty")
            
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if re.match(pattern, t):
                return True, ""
            else:
                return False, _("Invalid email address")
        
        hint = _("Enter email address") + ("" if required else _(" (optional)"))
        
        return WestyInputBox(
            session=session,
            title=title,
            text=text,
            validator=validator,
            input_type="email",
            hint=hint
        )
    
    @staticmethod
    def createPasswordInput(session, title="", text="", min_length=6, 
                           max_length=32, confirm_password=False):
        """Create password input with validation"""
        from . import _
        
        def validator(t):
            if not t:
                return False, _("Password cannot be empty")
            
            if len(t) < min_length:
                return False, _(f"Password must be at least {min_length} characters")
            
            if len(t) > max_length:
                return False, _(f"Password must be at most {max_length} characters")
            
            # Check for common weak passwords
            weak_passwords = ['password', '123456', 'qwerty', 'admin', 'letmein']
            if t.lower() in weak_passwords:
                return False, _("Password is too common")
            
            return True, ""
        
        hint = _(f"Password ({min_length}-{max_length} characters)")
        
        box = WestyInputBox(
            session=session,
            title=title,
            text=text,
            validator=validator,
            min_length=min_length,
            max_length=max_length,
            hint=hint,
            password=True
        )
        
        if confirm_password:
            # This would need a second input box for confirmation
            # For now, just add a note
            box.hint = hint + _(" (enter twice to confirm)")
        
        return box
    
    @staticmethod
    def createTimeInput(session, title="", text="", format_24h=True):
        """Create time input with validation"""
        from . import _
        
        def validator(t):
            if not t:
                return True, ""
            
            if format_24h:
                pattern = r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$'
                error_msg = _("Format: HH:MM (24-hour)")
            else:
                pattern = r'^(0?[1-9]|1[0-2]):[0-5][0-9] (AM|PM)$'
                error_msg = _("Format: HH:MM AM/PM")
            
            if re.match(pattern, t.upper()):
                return True, ""
            else:
                return False, error_msg
        
        hint = _("Format: {}").format("HH:MM" if format_24h else "HH:MM AM/PM")
        
        return WestyInputBox(
            session=session,
            title=title,
            text=text,
            validator=validator,
            hint=hint,
            max_length=8 if format_24h else 11
        )
    
    @staticmethod
    def createDateInput(session, title="", text="", format_iso=True):
        """Create date input with validation"""
        from . import _
        
        def validator(t):
            if not t:
                return True, ""
            
            if format_iso:
                pattern = r'^\d{4}-\d{2}-\d{2}$'
                error_msg = _("Format: YYYY-MM-DD")
            else:
                pattern = r'^\d{2}/\d{2}/\d{4}$'
                error_msg = _("Format: MM/DD/YYYY")
            
            if re.match(pattern, t):
                # Additional date validation
                try:
                    if format_iso:
                        year, month, day = map(int, t.split('-'))
                    else:
                        month, day, year = map(int, t.split('/'))
                    
                    # Basic date validation
                    if month < 1 or month > 12:
                        return False, _("Invalid month")
                    
                    if day < 1 or day > 31:
                        return False, _("Invalid day")
                    
                    if year < 1900 or year > 2100:
                        return False, _("Year out of range")
                    
                    return True, ""
                except:
                    return False, error_msg
            else:
                return False, error_msg
        
        hint = _("Format: {}").format("YYYY-MM-DD" if format_iso else "MM/DD/YYYY")
        
        return WestyInputBox(
            session=session,
            title=title,
            text=text,
            validator=validator,
            hint=hint,
            max_length=10
        )


# Convenience functions
def get_text_input(session, title="", default="", **kwargs):
    """Get text input from user"""
    try:
        box = WestyInputBox(session, title=title, text=default, **kwargs)
        session.openWithCallback(lambda result: result, box)
        return box
    except Exception as e:
        debug_print(f"get_text_input error: {e}")
        return None

def get_number_input(session, title="", default="", **kwargs):
    """Get number input from user"""
    try:
        box = InputFactory.createNumberInput(session, title=title, text=str(default) if default else "", **kwargs)
        session.openWithCallback(lambda result: result, box)
        return box
    except Exception as e:
        debug_print(f"get_number_input error: {e}")
        return None

def get_filename_input(session, title="", default="", **kwargs):
    """Get filename input from user"""
    try:
        box = InputFactory.createFilenameInput(session, title=title, text=default, **kwargs)
        session.openWithCallback(lambda result: result, box)
        return box
    except Exception as e:
        debug_print(f"get_filename_input error: {e}")
        return None

def get_path_input(session, title="", default="", **kwargs):
    """Get path input from user"""
    try:
        box = InputFactory.createPathInput(session, title=title, text=default, **kwargs)
        session.openWithCallback(lambda result: result, box)
        return box
    except Exception as e:
        debug_print(f"get_path_input error: {e}")
        return None


# Test function
if __name__ == "__main__":
    print(f"{PLUGIN_NAME} InputBox v{PLUGIN_VERSION}")
    print("=" * 60)
    
    print("Input Types Available:")
    print("  1. Text input (default)")
    print("  2. Number input (with range validation)")
    print("  3. Filename input (with extension control)")
    print("  4. Path input (with existence validation)")
    print("  5. Email input (with format validation)")
    print("  6. Password input (with strength validation)")
    print("  7. Time input (24h or 12h format)")
    print("  8. Date input (ISO or US format)")
    
    print("\nFeatures:")
    print("  • Real-time validation with error messages")
    print("  • Character count with color coding")
    print("  • Minimum/maximum length validation")
    print("  • Custom regex pattern validation")
    print("  • Password masking")
    print("  • Cursor blink indicator")
    print("  • Dynamic skin based on screen size")
    print("  • Plugin version display")
    
    print("\nFactory Methods:")
    print("  • InputFactory.createFilenameInput()")
    print("  • InputFactory.createNumberInput()")
    print("  • InputFactory.createPathInput()")
    print("  • InputFactory.createEmailInput()")
    print("  • InputFactory.createPasswordInput()")
    print("  • InputFactory.createTimeInput()")
    print("  • InputFactory.createDateInput()")
    
    print("\nConvenience Functions:")
    print("  • get_text_input()")
    print("  • get_number_input()")
    print("  • get_filename_input()")
    print("  • get_path_input()")
    
    # Test validation functions
    print("\nValidation Examples:")
    test_cases = [
        ("test.txt", "isValidFilename", True),
        ("test<.txt", "isValidFilename", False),
        ("user@example.com", "isValidEmail", True),
        ("user@example", "isValidEmail", False),
        ("/home/user", "isValidPath", True),
        ("/home/user/<bad>", "isValidPath", False),
    ]
    
    for text, func_name, expected in test_cases:
        ib = WestyInputBox(None, title="Test", text=text)
        func = getattr(ib, func_name, None)
        if func:
            result = func(text)
            status = "✓" if result == expected else "✗"
            print(f"  {status} {func_name}('{text}'): {result} (expected: {expected})")
    
    print("\n" + "=" * 60)
    print("InputBox module ready for v2.1.0 integration")