#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division, unicode_literals

import os
import sys

# Import our plugin's compatibility functions
try:
    from . import (
        _,
        debug_print,
        ensure_str,
        ensure_unicode,
        PLUGIN_NAME,
        PLUGIN_VERSION
    )
    debug_print(f"Console: Imported plugin utilities v{PLUGIN_VERSION}")
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

# OpenATV/Enigma2 imports with try/except fallback
try:
    from Screens.Screen import Screen
    from Components.ActionMap import ActionMap
    from Components.ScrollLabel import ScrollLabel
    from Components.Sources.StaticText import StaticText
    from Components.Label import Label
    from Components.Pixmap import Pixmap
    from enigma import eConsoleAppContainer, eTimer, getDesktop
    
    ENIGMA2_AVAILABLE = True
    debug_print("Console: Enigma2 imports successful")
except ImportError as e:
    debug_print(f"Console: Could not import Enigma2 modules: {e}")
    ENIGMA2_AVAILABLE = False
    
    # Create mock classes for testing
    class Screen:
        def __init__(self, session):
            self.session = session
            self.onLayoutFinish = []
            self.onClose = []
        
        def close(self):
            pass
        
        def execBegin(self):
            pass
        
        def execEnd(self):
            pass
    
    class ActionMap:
        def __init__(self, context, actions, prio):
            self.context = context
            self.actions = actions
    
    class ScrollLabel:
        def __init__(self, text=""):
            self.text = text
        
        def setText(self, text):
            self.text = text
        
        def appendText(self, text):
            self.text += text
        
        def pageUp(self):
            pass
        
        def pageDown(self):
            pass
        
        def lastPage(self):
            pass
        
        def isAtLastPage(self):
            return True
    
    class StaticText:
        def __init__(self, text=""):
            self.text = text
    
    class Label:
        def __init__(self, text=""):
            self.text = text
        
        def setText(self, text):
            self.text = text
    
    class Pixmap:
        def __init__(self):
            self.instance = None
        
        def hide(self):
            pass
        
        def show(self):
            pass
    
    class eConsoleAppContainer:
        def __init__(self):
            self.appClosed = []
            self.dataAvail = []
        
        def execute(self, *args):
            print(f"Would execute: {args}")
            return 0
        
        def kill(self):
            pass
        
        def sendCtrlC(self):
            pass
    
    class eTimer:
        def __init__(self):
            self.callbacks = []
        
        def start(self, interval):
            print(f"Timer started: {interval}ms")
        
        def stop(self):
            print("Timer stopped")
        
        def timeout(self):
            class Timeout:
                def get(self):
                    return self
                def append(self, func):
                    pass
            return Timeout()
    
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

# TRY IMPORTING v2.1.0 MODULES FOR INTEGRATION
try:
    from .SelectionManager import SelectionManager
    SELECTION_MANAGER_AVAILABLE = True
    debug_print("Console: SelectionManager imported successfully")
except ImportError:
    SELECTION_MANAGER_AVAILABLE = False
    debug_print("Console: SelectionManager not available")
    
    class SelectionManager:
        def __init__(self):
            pass
        
        def get_selected_paths(self, pane_id=None):
            return []

try:
    from .BatchOperations import BatchOperations
    BATCH_OPS_AVAILABLE = True
    debug_print("Console: BatchOperations imported successfully")
except ImportError:
    BATCH_OPS_AVAILABLE = False
    debug_print("Console: BatchOperations not available")
    
    class BatchOperations:
        def __init__(self):
            pass
        
        def batch_copy(self, source_paths, dest_dir, overwrite=False):
            return {'success': [], 'failed': []}

# Check screen size for skin
FULLHD = getDesktop(0).size().width() >= 1920

class WestyConsole(Screen):
    if FULLHD:
        skin = """
        <screen position="center,center" size="1200,700" title="{title} Console" flags="wfNoBorder">
            <widget name="console_output" position="50,50" size="1100,550" font="Console;18" transparent="0"/>
            <widget name="progress_bar_bg" position="50,610" size="1100,20" backgroundColor="#333333"/>
            <widget name="progress_bar" position="50,610" size="0,20" backgroundColor="#00ff00"/>
            <widget name="progress_text" position="50,635" size="1100,20" font="Regular;16" halign="center"/>
            <widget source="key_red" render="Label" position="200,670" size="200,30" font="Regular;22" foregroundColor="#ffffff" backgroundColor="red" halign="center" valign="center"/>
            <widget source="key_green" render="Label" position="450,670" size="200,30" font="Regular;22" foregroundColor="#ffffff" backgroundColor="green" halign="center" valign="center"/>
            <widget source="key_yellow" render="Label" position="700,670" size="200,30" font="Regular;22" foregroundColor="#ffffff" backgroundColor="yellow" halign="center" valign="center"/>
        </screen>
        """.format(title=PLUGIN_NAME)
    else:
        skin = """
        <screen position="center,center" size="800,500" title="{title} Console">
            <widget name="console_output" position="30,30" size="740,400" font="Console;14" transparent="0"/>
            <widget name="progress_bar_bg" position="30,440" size="740,15" backgroundColor="#333333"/>
            <widget name="progress_bar" position="30,440" size="0,15" backgroundColor="#00ff00"/>
            <widget name="progress_text" position="30,460" size="740,15" font="Regular;14" halign="center"/>
            <widget source="key_red" render="Label" position="50,480" size="200,25" font="Regular;18" foregroundColor="#ffffff" backgroundColor="red" halign="center"/>
            <widget source="key_green" render="Label" position="300,480" size="200,25" font="Regular;18" foregroundColor="#ffffff" backgroundColor="green" halign="center"/>
            <widget source="key_yellow" render="Label" position="550,480" size="200,25" font="Regular;18" foregroundColor="#ffffff" backgroundColor="yellow" halign="center"/>
        </screen>
        """.format(title=PLUGIN_NAME)
    
    def __init__(self, session, title=None, cmdlist=None, finishedCallback=None, 
                 showProgress=False, progressUpdateCallback=None):
        Screen.__init__(self, session)
        
        self.title = title or f"{PLUGIN_NAME} Console"
        self.cmdlist = cmdlist or []
        self.finishedCallback = finishedCallback
        self.showProgress = showProgress
        self.progressUpdateCallback = progressUpdateCallback
        
        debug_print(f"Console: Initializing console screen v{PLUGIN_VERSION}")
        debug_print(f"Console: Command list: {len(self.cmdlist)} commands")
        
        self["console_output"] = ScrollLabel("")
        self["progress_bar_bg"] = Pixmap()
        self["progress_bar"] = Pixmap()
        self["progress_text"] = Label("")
        
        self["key_red"] = StaticText(_("Cancel"))
        self["key_green"] = StaticText(_("Pause"))
        self["key_yellow"] = StaticText(_("Save Log"))
        
        self.container = eConsoleAppContainer()
        if hasattr(self.container, 'appClosed'):
            self.container.appClosed.append(self.runFinished)
        if hasattr(self.container, 'dataAvail'):
            self.container.dataAvail.append(self.dataAvail)
        
        self.progress_timer = eTimer()
        if hasattr(self.progress_timer, 'timeout'):
            self.progress_timer.timeout.get().append(self.updateProgress)
        else:
            # Fallback for mock timer
            self.progress_timer.callback = self.updateProgress
        
        self.is_paused = False
        self.current_progress = 0
        self.output_lines = []
        self.run = 0
        
        self["actions"] = ActionMap(["ColorActions", "DirectionActions", "OkCancelActions"],
        {
            "cancel": self.close,
            "red": self.close,
            "green": self.togglePause,
            "yellow": self.saveLog,
            "up": self.pageUp,
            "down": self.pageDown,
            "left": self.pageLeft,
            "right": self.pageRight,
            "ok": self.pageDown,
        }, -1)
        
        self.onLayoutFinish.append(self.startExecution)
    
    def startExecution(self):
        """Start command execution"""
        self.setTitle(self.title)
        self["console_output"].setText(_("Starting execution...\n"))
        self["console_output"].appendText(f"Westy FileMaster PRO v{PLUGIN_VERSION}\n")
        self["console_output"].appendText("=" * 50 + "\n")
        
        self.executeNext()
    
    def executeNext(self):
        """Execute next command in list"""
        if self.run < len(self.cmdlist):
            cmd = self.cmdlist[self.run]
            
            if isinstance(cmd, (list, tuple)):
                # Python 3 compatibility: ensure all arguments are strings
                cmd_args = [ensure_str(arg) for arg in cmd]
                debug_print(f"Console: Executing command: {cmd_args}")
                
                if ENIGMA2_AVAILABLE and hasattr(self.container, 'execute'):
                    retval = self.container.execute(cmd_args[0], *cmd_args[1:])
                else:
                    # Fallback for testing
                    import subprocess
                    try:
                        result = subprocess.run(cmd_args, capture_output=True, text=True)
                        self.dataAvail(result.stdout.encode() if result.stdout else b"")
                        self.dataAvail(result.stderr.encode() if result.stderr else b"")
                        retval = result.returncode
                    except Exception as e:
                        self.dataAvail(str(e).encode())
                        retval = 1
            else:
                cmd_str = ensure_str(cmd)
                debug_print(f"Console: Executing command: {cmd_str}")
                
                if ENIGMA2_AVAILABLE and hasattr(self.container, 'execute'):
                    retval = self.container.execute(cmd_str)
                else:
                    # Fallback for testing
                    import subprocess
                    try:
                        result = subprocess.run(cmd_str, shell=True, capture_output=True, text=True)
                        self.dataAvail(result.stdout.encode() if result.stdout else b"")
                        self.dataAvail(result.stderr.encode() if result.stderr else b"")
                        retval = result.returncode
                    except Exception as e:
                        self.dataAvail(str(e).encode())
                        retval = 1
            
            if retval and retval != 0:
                self.runFinished(retval)
            else:
                self.run += 1
                if self.run < len(self.cmdlist):
                    # Execute next command after short delay
                    self.executeNext()
                else:
                    self.runFinished(0)
                
                if self.showProgress:
                    if hasattr(self.progress_timer, 'start'):
                        self.progress_timer.start(500)  # Update progress every 500ms
        else:
            self.runFinished(0)
    
    def updateProgress(self):
        """Update progress bar if callback provided"""
        if self.progressUpdateCallback and not self.is_paused:
            try:
                progress = self.progressUpdateCallback()
                if progress is not None:
                    self.current_progress = max(0, min(100, progress))
                    self.updateProgressDisplay()
            except Exception as e:
                debug_print(f"Console: Error in progress update: {e}")
    
    def updateProgressDisplay(self):
        """Update progress bar visualization"""
        try:
            # Calculate bar width based on screen size
            bar_max_width = 1100 if FULLHD else 740
            bar_width = int(bar_max_width * (self.current_progress / 100))
            
            # Update progress bar
            if hasattr(self["progress_bar"], 'instance') and self["progress_bar"].instance:
                self["progress_bar"].instance.resize(bar_width, 20 if FULLHD else 15)
            
            # Update progress text
            self["progress_text"].setText(_(f"Progress: {self.current_progress}%"))
        except Exception as e:
            debug_print(f"Console: Error updating progress display: {e}")
    
    def dataAvail(self, data):
        """Handle console output"""
        if not self.is_paused:
            # Convert data to string if it's bytes (Python 3)
            if isinstance(data, bytes):
                try:
                    data = data.decode('utf-8', 'ignore')
                except:
                    try:
                        data = data.decode('latin-1', 'ignore')
                    except:
                        data = str(data)
            
            # Clean up control characters
            import re
            data = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', data)  # Remove ANSI escape codes
            
            self.output_lines.append(data)
            if len(self.output_lines) > 1000:  # Keep last 1000 lines
                self.output_lines.pop(0)
            
            if hasattr(self["console_output"], 'appendText'):
                self["console_output"].appendText(data)
            else:
                current = self["console_output"].text
                self["console_output"].setText(current + data)
    
    def togglePause(self):
        """Pause/resume execution"""
        self.is_paused = not self.is_paused
        
        if self.is_paused:
            if hasattr(self.container, 'sendCtrlC'):
                self.container.sendCtrlC()  # Send SIGINT
            self["key_green"].setText(_("Resume"))
            self["console_output"].appendText("\n" + _("=== PAUSED ===\n"))
            debug_print("Console: Paused")
        else:
            self["key_green"].setText(_("Pause"))
            self["console_output"].appendText("\n" + _("=== RESUMED ===\n"))
            debug_print("Console: Resumed")
            
            # Continue execution
            if self.run < len(self.cmdlist):
                self.executeNext()
    
    def saveLog(self):
        """Save console output to file"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"/tmp/westy_console_{timestamp}.log"
        
        # Try to import VirtualKeyBoard, fallback to InputBox
        try:
            from Screens.VirtualKeyBoard import VirtualKeyBoard
            self.session.openWithCallback(
                lambda name: self.doSaveLog(name if name else default_name),
                VirtualKeyBoard,
                title=_("Enter log filename"),
                text=default_name
            )
        except ImportError:
            try:
                from Screens.InputBox import InputBox
                self.session.openWithCallback(
                    lambda name: self.doSaveLog(name if name else default_name),
                    InputBox,
                    title=_("Enter log filename"),
                    windowTitle=_("Save Log"),
                    text=default_name
                )
            except ImportError:
                # Direct save
                self.doSaveLog(default_name)
    
    def doSaveLog(self, filename):
        """Save log to file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(''.join(self.output_lines))
            
            message = f'{_("Log saved to:")} {filename}'
            self["console_output"].appendText(f"\n{message}\n")
            debug_print(f"Console: {message}")
        except Exception as e:
            error_msg = f'{_("Error saving log:")} {str(e)}'
            self["console_output"].appendText(f"\n{error_msg}\n")
            debug_print(f"Console: {error_msg}")
    
    def runFinished(self, retval):
        """Handle command completion"""
        debug_print(f"Console: Command finished with retval: {retval}")
        
        if hasattr(self.progress_timer, 'stop'):
            self.progress_timer.stop()
        
        if retval == 0:
            status = _("Execution completed successfully")
            debug_print("Console: Execution successful")
        else:
            status = _(f"Execution failed with code: {retval}")
            debug_print(f"Console: Execution failed: {retval}")
        
        self["console_output"].appendText(f"\n\n=== {status} ===\n")
        self["progress_text"].setText(status)
        self.current_progress = 100
        self.updateProgressDisplay()
        
        if self.finishedCallback:
            try:
                self.finishedCallback(retval)
            except Exception as e:
                debug_print(f"Console: Error in finishedCallback: {e}")
    
    def pageUp(self):
        if hasattr(self["console_output"], 'pageUp'):
            self["console_output"].pageUp()
    
    def pageDown(self):
        if hasattr(self["console_output"], 'pageDown'):
            self["console_output"].pageDown()
    
    def pageLeft(self):
        if hasattr(self["console_output"], 'lastPage'):
            self["console_output"].lastPage()
    
    def pageRight(self):
        if hasattr(self["console_output"], 'isAtLastPage'):
            self["console_output"].isAtLastPage()
    
    def close(self):
        """Clean up and close"""
        debug_print("Console: Closing console")
        
        if hasattr(self, 'container') and self.container:
            if hasattr(self.container, 'kill'):
                self.container.kill()
        
        if hasattr(self.progress_timer, 'stop'):
            self.progress_timer.stop()
        
        Screen.close(self)


# Convenience functions for UI integration
class WestyConsoleManager:
    """Manager for console operations with v2.1.0 integration"""
    
    def __init__(self):
        self.console_history = []
        self.max_history = 100
        debug_print(f"ConsoleManager: Initialized v{PLUGIN_VERSION}")
    
    def open_console(self, session, command=None, title=None):
        """Open console with optional command"""
        cmdlist = []
        if command:
            cmdlist = [command] if isinstance(command, str) else command
        
        console = session.open(
            WestyConsole,
            title=title or f"{PLUGIN_NAME} Terminal",
            cmdlist=cmdlist,
            finishedCallback=self.on_console_finished
        )
        
        self.console_history.append({
            'timestamp': time.time() if 'time' in globals() else 0,
            'command': command or 'interactive',
            'title': title
        })
        
        # Keep history manageable
        if len(self.console_history) > self.max_history:
            self.console_history.pop(0)
        
        return console
    
    def on_console_finished(self, retval):
        """Handle console completion"""
        debug_print(f"ConsoleManager: Console finished with code: {retval}")
    
    def execute_batch_command(self, session, command_template, file_paths):
        """Execute command on multiple files (for batch operations)"""
        if not file_paths:
            return None
        
        commands = []
        for file_path in file_paths:
            # Replace {file} placeholder with actual file path
            cmd = command_template.replace('{file}', ensure_str(file_path))
            commands.append(cmd)
        
        title = f"Batch Command: {command_template[:50]}..."
        return self.open_console(session, commands, title)
    
    def get_command_history(self, limit=20):
        """Get recent command history"""
        return self.console_history[-limit:] if self.console_history else []
    
    def clear_history(self):
        """Clear command history"""
        self.console_history.clear()
        debug_print("ConsoleManager: History cleared")


# Create a global instance for easy access
console_manager = WestyConsoleManager()

# Convenience function for UI
def open_console(session, command=None, title=None):
    """Open console (convenience wrapper)"""
    return console_manager.open_console(session, command, title)


# Test function
if __name__ == "__main__":
    print(f"{PLUGIN_NAME} Console Test")
    print("=" * 60)
    print(f"Version: {PLUGIN_VERSION}")
    print(f"Enigma2 Available: {ENIGMA2_AVAILABLE}")
    print(f"FullHD: {FULLHD}")
    print("=" * 60)
    
    # Test console manager
    mgr = WestyConsoleManager()
    print("Console manager initialized")
    
    # Test command execution
    test_cmd = ["echo", "Hello from Westy Console!"]
    print(f"Test command: {test_cmd}")
    
    print("\nConsole module ready for integration")