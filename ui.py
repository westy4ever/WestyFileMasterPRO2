#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ============================================================================
# UI DEBUG PATCH - v2.1.0 CRITICAL FIX
# ============================================================================
from __future__ import print_function, absolute_import, division, unicode_literals
import sys
import os

# UI Debug logging
UI_DEBUG_LOG = "/tmp/westy_ui_debug.log"

def gRGB(x): return x
def ui_debug_log(message):
    try:
        with open(UI_DEBUG_LOG, 'a') as f:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {message}\n")
            f.flush()
    except:
        pass

ui_debug_log("="*60)
ui_debug_log("UI Module Loading")
ui_debug_log("="*60)

PLUGIN_PATH = os.path.dirname(os.path.abspath(__file__))
if PLUGIN_PATH not in sys.path:
    sys.path.insert(0, PLUGIN_PATH)
    ui_debug_log(f"Added to path: {PLUGIN_PATH}")

# CRITICAL FIX: Direct imports instead of "import __init__ as plugin_init"
try:
    ui_debug_log("Importing from __init__...")
    from __init__ import (
        _,
        debug_print,
        ensure_str,
        ensure_unicode,
        PLUGIN_NAME,
        PLUGIN_VERSION
    )
    ui_debug_log(f"Successfully imported plugin utilities v{PLUGIN_VERSION}")
    
    try:
        from __init__ import is_full_hd, get_icon_path, _
        ui_debug_log("Imported optional functions")
    except:
        def is_full_hd(): return True
        def get_icon_path(icon): return None
        ui_debug_log("Using fallback functions")
        
except Exception as e:
    ui_debug_log(f"Import error: {e}")
    def _(text): return text
    def debug_print(*args, **kwargs):
        if args: 
            msg = " ".join(str(a) for a in args)
            ui_debug_log(msg)
    def ensure_str(s, encoding='utf-8'): return str(s)
    ensure_unicode = ensure_str
    PLUGIN_NAME = "Westy FileMaster PRO"
    PLUGIN_VERSION = "2.1.0"
    def is_full_hd(): return True
    def get_icon_path(icon): return None

ui_debug_log("UI patch initialization complete")

# ============================================================================
# CACHE IMPORT WITH FALLBACK
# ============================================================================
# Try to import performance cache - IMPROVED VERSION
try:
    # Add current directory to Python path
    PLUGIN_PATH = os.path.dirname(os.path.abspath(__file__))
    if PLUGIN_PATH not in sys.path:
        sys.path.insert(0, PLUGIN_PATH)
    
    # Try to import CacheManager
    try:
        from CacheManager import file_info_cache, image_cache, CACHE_AVAILABLE
        debug_print("ui.py: CacheManager imported successfully")
    except ImportError:
        # Try relative import
        from .CacheManager import file_info_cache, image_cache, CACHE_AVAILABLE
        debug_print("ui.py: CacheManager imported via relative import")
    
except ImportError as e:
    CACHE_AVAILABLE = False
    debug_print("ui.py: CacheManager not available: %s" % str(e))
    # Create dummy cache objects for compatibility
    class DummyCache:
        def invalidate_directory(self, path): pass
        def invalidate_file(self, path): pass
        def get(self, key): return None
        def set(self, key, value): pass
    
    file_info_cache = DummyCache()
    image_cache = DummyCache()
# ============================================================================
# ENIGMA2 SCREEN IMPORTS
# ============================================================================
ENIGMA2_SCREENS_AVAILABLE = False

# Debug BEFORE import attempt
try:
    with open("/tmp/westy_imports.log", "a") as f:
        from datetime import datetime
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ENIGMA2_SCREENS_AVAILABLE = {ENIGMA2_SCREENS_AVAILABLE} (before import attempt)\n")
        f.write("  Screen class: NOT IMPORTED YET\n")
except Exception as e:
    pass

try:
    from Screens.Screen import Screen
    from Components.ActionMap import ActionMap, HelpableActionMap
    from Components.Label import Label
    from Components.MenuList import MenuList
    from Components.Sources.StaticText import StaticText
    from Components.Pixmap import Pixmap
    from Components.config import config
    from enigma import getDesktop, eTimer, RT_HALIGN_CENTER, RT_VALIGN_CENTER, gRGB
    ENIGMA2_SCREENS_AVAILABLE = True
    
    # Debug AFTER successful import
    try:
        with open("/tmp/westy_imports.log", "a") as f:
            from datetime import datetime
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ENIGMA2_SCREENS_AVAILABLE = {ENIGMA2_SCREENS_AVAILABLE} (imports successful!)\n")
            f.write(f"  Screen class: {Screen}\n")
            f.write(f"  Screen module: {Screen.__module__}\n")
            f.write(f"  Screen has __setitem__: {hasattr(Screen, '__setitem__')}\n")
    except Exception as e:
        pass
    
    debug_print("ui.py: Enigma2 screen imports successful")
except ImportError as e:
    debug_print(f"ui.py: Enigma2 screen imports failed: {e}")
    
    # Debug for import failure
    try:
        with open("/tmp/westy_imports.log", "a") as f:
            from datetime import datetime
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ENIGMA2_SCREENS_AVAILABLE = False (imports failed: {e})\n")
            f.write("  Using mock classes instead\n")
    except Exception as e2:
        pass
    
    # Mock classes for testing
    class Screen:
        def __init__(self, session):
            self.session = session
            self.onLayoutFinish = []
            self.onClose = []
            self._widgets = {}  # Dictionary to store widgets
        
        # Dictionary-like access for widgets
        def __setitem__(self, key, value):
            self._widgets[key] = value
        
        def __getitem__(self, key):
            return self._widgets.get(key)
        
        def get(self, key, default=None):
            return self._widgets.get(key, default)
        
        def close(self): pass
        def execBegin(self): pass
        def execEnd(self): pass
    
    class ActionMap:
        def __init__(self, context, actions, prio):
            self.context = context
            self.actions = actions
    
    HelpableActionMap = ActionMap
    
    class Label:
        def __init__(self, text=""): 
            self.text = text
        def setText(self, text): 
            self.text = text
        def setForegroundColor(self, color): pass
        def hide(self): pass
        def show(self): pass
    
    class StaticText:
        def __init__(self, text=""): 
            self.text = text
    
    class Pixmap:
        def __init__(self): pass
        def hide(self): pass
        def show(self): pass
    
    class MockConfig:
        class plugins:
            class westyfilemaster:
                default_left_path = "/tmp/"
                default_right_path = "/tmp/"
                show_hidden_files = False
                confirm_deletions = True
    
    config = MockConfig()
    
    def getDesktop(screen=0):
        class Desktop:
            def size(self):
                class Size:
                    def width(self): 
                        return 1920
                    def height(self): 
                        return 1080
                return Size()
        return Desktop()
    
    class eTimer:
        def __init__(self):
            self.callbacks = []
            self.timeout = self._create_timeout()
        
        def _create_timeout(self):
            class Timeout:
                def __init__(self, parent):
                    self.parent = parent
                def get(self):
                    return self
                def append(self, func):
                    self.parent.callbacks.append(func)
            return Timeout(self)
        
        def start(self, interval): 
            pass
        def stop(self): 
            pass
    
    RT_HALIGN_CENTER = 1
    RT_VALIGN_CENTER = 1
    gRGB = lambda x: x

# ============================================================================
# ENIGMA2 DIALOG IMPORTS
# ============================================================================
ENIGMA2_DIALOGS_AVAILABLE = False
try:
    from Screens.ChoiceBox import ChoiceBox
    from Screens.MessageBox import MessageBox
    from Screens.VirtualKeyBoard import VirtualKeyBoard
    from Screens.InputBox import InputBox
    ENIGMA2_DIALOGS_AVAILABLE = True
    debug_print("ui.py: Enigma2 dialog imports successful")
except ImportError:
    debug_print("ui.py: Enigma2 dialog imports failed")
    class ChoiceBox: pass
    class MessageBox: pass
    class VirtualKeyBoard: pass
    class InputBox: pass

# ============================================================================
# MULTIMEDIA COMPONENTS IMPORT
# ============================================================================
# Try to import multimedia components
try:
    # Check if multimedia modules exist
    multimedia_imported = False
    try:
        # Try relative import
        from .ImageViewer import WestyImageViewer, viewImage
        from .MediaPlayer import WestyMediaPlayer, playMedia
        from .AudioPlayer import WestyAudioPlayer, playAudio
        multimedia_imported = True
        debug_print("ui.py: Multimedia components imported successfully")
    except ImportError:
        # Try direct import
        try:
            import ImageViewer
            import MediaPlayer
            import AudioPlayer
            WestyImageViewer = ImageViewer.WestyImageViewer
            WestyMediaPlayer = MediaPlayer.WestyMediaPlayer
            WestyAudioPlayer = AudioPlayer.WestyAudioPlayer
            viewImage = ImageViewer.viewImage
            playMedia = MediaPlayer.playMedia
            playAudio = AudioPlayer.playAudio
            multimedia_imported = True
            debug_print("ui.py: Multimedia components imported directly")
        except ImportError as e:
            debug_print(f"ui.py: Multimedia import failed: {e}")
    
    if not multimedia_imported:
        raise ImportError("Could not import multimedia components")
        
except Exception as e:
    debug_print(f"ui.py: Multimedia components not available: {e}")
    # Create minimal mock classes
    class WestyImageViewer:
        def __init__(self, session, image_file): pass
    class WestyMediaPlayer:
        def __init__(self, session, media_file): pass
    class WestyAudioPlayer:
        def __init__(self, session, audio_file): pass
    
    def viewImage(session, image_file):
        try:
           from ImageViewer import viewImage as _viewImage
           return _viewImage(session, image_file)
        except ImportError:
            debug_print(f"Mock viewImage called: {image_file}")
    
    def playMedia(session, media_file):
        debug_print(f"Mock playMedia called: {media_file}")
    
    def playAudio(session, audio_file):
        debug_print(f"Mock playAudio called: {audio_file}")

# ============================================================================
# PLUGIN MODULE IMPORTS WITH FALLBACKS - FIXED VERSION
# ============================================================================
# Try to import enhanced modules
module_imports = {
    'Console': ('WestyConsole', None),
    'FileTransfer': ('WestyFileTransferJob', None),
    'Directories': ('SmartDirectoryManager', None),
    'TaskList': ('WestyTaskListScreen', None),
    'InputBox': ('WestyInputBox', InputBox),  # Fallback to Enigma2 InputBox
    'UnitConversions': ('EnhancedUnitScaler', None),
    'FileList': ('WestyFileList', None),
    'BatchOperations': ('BatchOperations', None),
    'SelectionManager': ('SelectionManager', None),
    'Setup': ('WestyFileMasterSetup', None)
}

# Import modules dynamically with BETTER ERROR HANDLING
for module_name, (primary_class, fallback_class) in module_imports.items():
    try:
        ui_debug_log(f"Trying to import {module_name}.{primary_class}")
        module = __import__(f'.{module_name}', fromlist=[primary_class])
        
        # Check if the class exists in the module
        if hasattr(module, primary_class):
            globals()[primary_class] = getattr(module, primary_class)
            ui_debug_log(f"INFO: Imported {primary_class} from {module_name}")
            debug_print(f"ui.py: Imported {primary_class} from {module_name}")
        else:
            raise ImportError(f"Class {primary_class} not found in {module_name}")
            
    except ImportError as e:
        ui_debug_log(f"ERROR: Failed to import {module_name}.{primary_class}: {e}")
        debug_print(f"ui.py: Failed to import {module_name}: {e}")
        
        if fallback_class:
            globals()[primary_class] = fallback_class
            ui_debug_log(f"WARNING: Using fallback class for {primary_class}")
        else:
            # Create ENHANCED mock class that has required methods
            if primary_class == 'SmartDirectoryManager':
                ui_debug_log(f"WARNING: Creating enhanced mock for {primary_class}")
                class EnhancedMockDirManager:
                    def __init__(self, *args, **kwargs): 
                        ui_debug_log("EnhancedMockDirManager initialized")
                    
                    def get_recommended_directory(self, typ):
                        # Always return a valid directory
                        ui_debug_log(f"Mock get_recommended_directory({typ}) called")
                        for path in ['/media/hdd/', '/home/root/', '/tmp/']:
                            if os.path.isdir(path):
                                return path
                        return '/tmp/'
                    
                    def shorten_path(self, path, max_len):
                        if len(path) > max_len:
                            keep = (max_len - 3) // 2
                            return path[:keep] + "..." + path[-keep:]
                        return path
                        
                    def __getattr__(self, name):
                        # Handle any other missing methods
                        ui_debug_log(f"Mock method called: {name}")
                        def dummy_method(*args, **kwargs):
                            ui_debug_log(f"Dummy {name} called with args: {args}")
                            return None
                        return dummy_method
                
                globals()[primary_class] = EnhancedMockDirManager
            else:
                # For other modules, create simple mock
                class MockClass:
                    def __init__(self, *args, **kwargs): 
                        ui_debug_log(f"MockClass {primary_class} initialized")
                    def __call__(self, *args, **kwargs): 
                        ui_debug_log(f"MockClass {primary_class} called")
                globals()[primary_class] = MockClass
# ============================================================================
# TOOLS.DIRECTORIES IMPORTS
# ============================================================================
try:
    from Tools.Directories import fileExists, pathExists, isMount
    TOOLS_AVAILABLE = True
except ImportError:
    debug_print("ui.py: Tools.Directories not available")
    TOOLS_AVAILABLE = False
    
    def fileExists(path):
        return os.path.exists(ensure_str(path))
    
    def pathExists(path):
        return os.path.exists(ensure_str(path))
    
    def isMount(path):
        return False

# ============================================================================
# SCREEN DEFINITION
# ============================================================================
class WestyFileMasterScreen(Screen):
    """Main file manager screen with dual panes"""
    
    # Debug line should be inside __init__ or as a class variable, not here
    # debug_print(f"ui.py: Inheriting from Screen class: {Screen}")  # REMOVED
    
    # ========================================================================
    # SKIN TEMPLATES - STATIC DEFINITIONS
    # ========================================================================
    
    # Full HD skin template (1920x1080)
    SKIN_FULLHD = """
<screen position="center,center" size="1920,1080" title="{} v{}" flags="wfNoBorder">
    <!-- Left Pane Background (Active/Inactive) -->
    <widget name="left_pane_bg" position="40,40" size="900,920" backgroundColor="#1a1a1a" transparent="0" zPosition="-1"/>
    <widget name="left_pane_active" position="40,40" size="6,920" backgroundColor="#00ff00" transparent="0" zPosition="0"/>
    
    <!-- Right Pane Background (Active/Inactive) -->
    <widget name="right_pane_bg" position="980,40" size="900,920" backgroundColor="#1a1a1a" transparent="0" zPosition="-1"/>
    <widget name="right_pane_active" position="1874,40" size="6,920" backgroundColor="#00ff00" transparent="0" zPosition="0"/>
    
    <!-- Left Pane Header -->
    <widget name="left_header" position="50,50" size="880,35" font="Regular;28" foregroundColor="#ffffff" backgroundColor="#333333" halign="center" valign="center" transparent="0"/>
    <widget name="left_path" position="50,90" size="880,25" font="Regular;20" foregroundColor="#cccccc" noWrap="1"/>
    
    <!-- Right Pane Header -->
    <widget name="right_header" position="990,50" size="880,35" font="Regular;28" foregroundColor="#ffffff" backgroundColor="#333333" halign="center" valign="center" transparent="0"/>
    <widget name="right_path" position="990,90" size="880,25" font="Regular;20" foregroundColor="#cccccc" noWrap="1"/>
    
    <!-- File Lists -->
    <widget name="list_left" position="50,120" size="880,780" itemHeight="40" scrollbarMode="showOnDemand"/>
    <widget name="list_right" position="990,120" size="880,780" itemHeight="40" scrollbarMode="showOnDemand"/>
    
    <!-- Status Bar -->
    <widget name="status_bar" position="50,910" size="1820,40" font="Regular;22" foregroundColor="#00ff00" backgroundColor="#222222" halign="center" valign="center"/>
    
    <!-- Selection Status -->
    <widget name="selection_status" position="50,960" size="500,30" font="Regular;22" foregroundColor="#ffff00" backgroundColor="#222222" halign="left" valign="center"/>
    
    <!-- Key Help -->
    <widget source="key_red" render="Label" position="600,970" size="280,40" font="Regular;26" foregroundColor="#ffffff" backgroundColor="#ff0000" halign="center" valign="center"/>
    <widget source="key_green" render="Label" position="900,970" size="280,40" font="Regular;26" foregroundColor="#ffffff" backgroundColor="#00ff00" halign="center" valign="center"/>
    <widget source="key_yellow" render="Label" position="1200,970" size="280,40" font="Regular;26" foregroundColor="#ffffff" backgroundColor="#ffff00" halign="center" valign="center"/>
    <widget source="key_blue" render="Label" position="1500,970" size="280,40" font="Regular;26" foregroundColor="#ffffff" backgroundColor="#0000ff" halign="center" valign="center"/>
    
    <!-- Info Labels -->
    <widget name="left_info" position="50,950" size="880,20" font="Regular;18" foregroundColor="#888888"/>
    <widget name="right_info" position="990,950" size="880,20" font="Regular;18" foregroundColor="#888888"/>
</screen>
"""
    
    # HD skin template (1280x720)
    SKIN_HD = """
<screen position="center,center" size="1280,720" title="{} v{}">
    <!-- Left Pane -->
    <widget name="left_pane_bg" position="20,20" size="600,580" backgroundColor="#1a1a1a"/>
    <widget name="left_pane_active" position="20,20" size="4,580" backgroundColor="#00ff00"/>
    
    <!-- Right Pane -->
    <widget name="right_pane_bg" position="660,20" size="600,580" backgroundColor="#1a1a1a"/>
    <widget name="right_pane_active" position="1256,20" size="4,580" backgroundColor="#00ff00"/>
    
    <!-- Headers -->
    <widget name="left_header" position="30,30" size="580,30" font="Regular;22" foregroundColor="#ffffff" backgroundColor="#333333" halign="center"/>
    <widget name="left_path" position="30,65" size="580,20" font="Regular;16" foregroundColor="#cccccc"/>
    
    <widget name="right_header" position="670,30" size="580,30" font="Regular;22" foregroundColor="#ffffff" backgroundColor="#333333" halign="center"/>
    <widget name="right_path" position="670,65" size="580,20" font="Regular;16" foregroundColor="#cccccc"/>
    
    <!-- File Lists -->
    <widget name="list_left" position="30,90" size="580,500" itemHeight="30" scrollbarMode="showOnDemand"/>
    <widget name="list_right" position="670,90" size="580,500" itemHeight="30" scrollbarMode="showOnDemand"/>
    
    <!-- Status Bar -->
    <widget name="status_bar" position="20,610" size="1240,30" font="Regular;18" foregroundColor="#00ff00" backgroundColor="#222222" halign="center"/>
    
    <!-- Selection Status -->
    <widget name="selection_status" position="20,640" size="400,20" font="Regular;16" foregroundColor="#ffff00" backgroundColor="#222222" halign="left"/>
    
    <!-- Key Help -->
    <widget source="key_red" render="Label" position="40,670" size="280,30" font="Regular;20" foregroundColor="#ffffff" backgroundColor="#ff0000" halign="center"/>
    <widget source="key_green" render="Label" position="360,670" size="280,30" font="Regular;20" foregroundColor="#ffffff" backgroundColor="#00ff00" halign="center"/>
    <widget source="key_yellow" render="Label" position="680,670" size="280,30" font="Regular;20" foregroundColor="#ffffff" backgroundColor="#ffff00" halign="center"/>
    <widget source="key_blue" render="Label" position="1000,670" size="280,30" font="Regular;20" foregroundColor="#ffffff" backgroundColor="#0000ff" halign="center"/>
</screen>
"""
    
    # ========================================================================
    # INITIALIZATION
    # ========================================================================
    def __init__(self, session, path_left=None):
        # Direct debug
        try:
            with open("/tmp/westy_screen_init.log", "a") as f:
                from datetime import datetime
                f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] WestyFileMasterScreen.__init__ called\n")
                f.write(f"  session: {session}\n")
                f.write(f"  path_left: {path_left}\n")
        except:
            pass
        
        try:
            import sys
            
            # DEBUG 0.1 - Start
            try:
                with open("/tmp/westy_screen_debug.log", "a") as f:
                    from datetime import datetime
                    f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [0.1] __init__ started\n")
            except:
                pass
            
            # DETERMINE SCREEN RESOLUTION HERE (when instance is created, not at import time)
            try:
                from enigma import getDesktop
                desktop = getDesktop(0)
                width = desktop.size().width()
                is_fullhd = width >= 1920
                debug_print(f"[UI] Screen resolution detected: {width}px ({'FullHD' if is_fullhd else 'HD'})")
                
                # DEBUG 0.2 - Resolution detected
                try:
                    with open("/tmp/westy_screen_debug.log", "a") as f:
                        from datetime import datetime
                        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [0.2] Resolution detected\n")
                        f.write(f"  width: {width}\n")
                        f.write(f"  is_fullhd: {is_fullhd}\n")
                except:
                    pass
                    
            except Exception as e:
                debug_print(f"ui.py: Could not detect screen resolution: {e}, defaulting to HD")
                is_fullhd = False
                
                # DEBUG 0.3 - Resolution error
                try:
                    with open("/tmp/westy_screen_debug.log", "a") as f:
                        from datetime import datetime
                        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [0.3] Resolution error: {e}\n")
                except:
                    pass
            
            # DEBUG - Skin selection
            try:
                with open("/tmp/westy_screen_init.log", "a") as f:
                    from datetime import datetime
                    f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Before skin selection\n")
                    if 'width' in locals():
                        f.write(f"  Desktop width: {width}\n")
            except Exception as e:
                try:
                    with open("/tmp/westy_screen_init.log", "a") as f:
                        f.write(f"  Error checking desktop: {e}\n")
                except:
                    pass
            
            # DEBUG 0.5 - Before skin assignment
            try:
                with open("/tmp/westy_screen_debug.log", "a") as f:
                    from datetime import datetime
                    f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [0.5] Before skin assignment\n")
                    f.write(f"  is_fullhd: {is_fullhd}\n")
            except:
                pass
            
            # SET SKIN BASED ON DETECTED RESOLUTION
            if is_fullhd:
                self.skin = self.SKIN_FULLHD.format("Westy FileMaster PRO", PLUGIN_VERSION)
                debug_print("[UI] Using FullHD skin")
            else:
                self.skin = self.SKIN_HD.format("Westy FileMaster PRO", PLUGIN_VERSION)
                debug_print("[UI] Using HD skin")
            
            # DEBUG 0.6 - After skin assignment
            try:
                with open("/tmp/westy_screen_debug.log", "a") as f:
                    from datetime import datetime
                    f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [0.6] After skin assignment\n")
                    f.write(f"  has skin attr: {hasattr(self, 'skin')}\n")
                    if hasattr(self, 'skin'):
                        f.write(f"  skin length: {len(self.skin)}\n")
            except:
                pass
            
            # DEBUG 1 - Before parent init
            try:
                with open("/tmp/westy_screen_debug.log", "a") as f:
                    from datetime import datetime
                    f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [1] About to call Screen.__init__()\n")
                    f.write(f"  self type: {type(self)}\n")
                    f.write(f"  has skin: {hasattr(self, 'skin')}\n")
                    if hasattr(self, 'skin'):
                        f.write(f"  skin length: {len(self.skin)}\n")
                        f.write(f"  skin preview: {repr(self.skin[:100])}\n")
            except Exception as e:
                try:
                    with open("/tmp/westy_screen_debug.log", "a") as f:
                        f.write(f"  Error in debug 1: {e}\n")
                except:
                    pass
            
            # Now call parent constructor
            Screen.__init__(self, session)
            
            # DEBUG 2 - After parent init
            try:
                with open("/tmp/westy_screen_debug.log", "a") as f:
                    from datetime import datetime
                    f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [2] Screen.__init__() completed\n")
            except:
                pass
            
            debug_print(f"ui.py: Parent Screen.__init__ completed")
            debug_print("Initializing {} v{}".format(PLUGIN_NAME, PLUGIN_VERSION))
            
            # Continue with the rest of your initialization...
            self._initialize_modules()
            
            # Initialize multi-selection manager
            self.selection_manager = SelectionManager()
            self.batch_ops = BatchOperations()
            
            # Initialize panes
            self.active_pane = "left"
            self.left_pane_active = True
            
            # Selection state
            self.multi_select_mode = False
            self.last_selected_index = None
            
            # Initialize UI widgets
            self._setup_widgets()
            
            # Initialize file lists
            self.initializeFileLists(path_left)
            
            # Setup actions
            self.setupActions()
            
            # Connect callbacks
            self.onLayoutFinish.append(self.updatePaneHighlight)
            
            # Initialize timers
            self._setup_timers()
            
            debug_print("FileMaster screen initialized successfully")
            debug_print(f"ui.py: Screen initialization COMPLETE")
            
        except Exception as e:
            debug_print(f"ui.py: CRITICAL ERROR in screen __init__: {e}")
            sys.stderr.write(f"ERROR in screen __init__: {e}\n")
            import traceback
            traceback.print_exc(file=sys.stderr)
            raise
    def _initialize_modules(self):
        """Initialize all plugin modules with error handling"""
        print("DEBUG: _initialize_modules called")
        import sys
        
        try:
            self.console = WestyConsole()
        except:
            class MockConsole:
                def log(self, msg): debug_print(f"Console: {msg}")
                def open_console(self, session): debug_print("Console would open")
                def cleanup(self): pass
            self.console = MockConsole()
        
        try:
            self.file_transfer = WestyFileTransferJob()
        except:
            class MockFileTransfer:
                def __init__(self): pass
                def cleanup(self): pass
            self.file_transfer = MockFileTransfer()
        
        try:
            self.dir_manager = SmartDirectoryManager()
        except:
            class MockDirManager:
                def get_recommended_directory(self, typ): return "/tmp/"
                def shorten_path(self, path, max_len): 
                    return path if len(path) <= max_len else path[:max_len-3] + "..."
            self.dir_manager = MockDirManager()
        
        try:
            self.task_list = WestyTaskListScreen(self.session)
        except:
            class MockTaskList:
                def __init__(self, session): self.session = session
            self.task_list = MockTaskList(self.session)
        
        try:
            self.unit_scaler = EnhancedUnitScaler()
        except:
            class MockUnitScaler:
                def format(self, value, unit_type='bytes'):
                    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                        if value < 1024.0:
                            return f"{value:.1f} {unit}"
                        value /= 1024.0
                    return f"{value:.1f} PB"
            self.unit_scaler = MockUnitScaler()
    
    def _setup_widgets(self):
        """Setup all UI widgets"""
        # Pane background widgets
        self["left_pane_bg"] = Pixmap()
        self["left_pane_active"] = Pixmap()
        self["right_pane_bg"] = Pixmap()
        self["right_pane_active"] = Pixmap()
        
        # Headers and paths
        self["left_header"] = Label(_("LEFT PANE"))
        self["left_path"] = Label("")
        self["right_header"] = Label(_("RIGHT PANE"))
        self["right_path"] = Label("")
        
        # Status bar and selection status
        self["status_bar"] = Label(_("Ready"))
        self["selection_status"] = Label("")
        
        # Key labels
        self["key_red"] = StaticText(_("Exit"))
        self["key_green"] = StaticText(_("Copy/Move"))
        self["key_yellow"] = StaticText(_("Menu"))
        self["key_blue"] = StaticText(_("Delete/Rename"))
        
        # Info labels
        self["left_info"] = Label("")
        self["right_info"] = Label("")
        # File list widgets
        self["list_left"] = MenuList([])
        self["list_right"] = MenuList([])
    
    def _setup_timers(self):
        debug_print(f"ui.py: _setup_timers called")
        debug_print(f"  refresh_timer type: {type(self.refresh_timer)}")
        debug_print(f"  has timeout: {hasattr(self.refresh_timer, 'timeout')}")
        """Setup refresh timer"""
        self.refresh_timer = eTimer()
        try:
            self.refresh_timer.timeout.get().append(self.updateStatus)
        except:
            # Fallback for mock timer
            self.refresh_timer.callback.append(self.updateStatus)
        self.refresh_timer.start(1000)
    
    # ========================================================================
    # FILE LIST INITIALIZATION
    # ========================================================================
    def initializeFileLists(self, path_left):
        """Initialize left and right file lists"""
        debug_print("Initializing file lists with path_left={}".format(path_left))
        
        # Get default paths from config
        try:
            default_left = config.plugins.westyfilemaster.default_left_path.value
            default_right = config.plugins.westyfilemaster.default_right_path.value
            show_hidden = config.plugins.westyfilemaster.show_hidden_files.value
        except:
            default_left = "/media/hdd/"
            default_right = "/home/root/"
            show_hidden = False
        
        # Determine left path
        if path_left and os.path.isdir(ensure_str(path_left)):
            left_path = path_left
        else:
            left_path = self.dir_manager.get_recommended_directory("source")
            if not left_path or not os.path.isdir(ensure_str(left_path)):
                left_path = default_left
        
        # Determine right path
        right_path = self.dir_manager.get_recommended_directory("target")
        if not right_path or not os.path.isdir(ensure_str(right_path)):
            right_path = default_right
        
        # Ensure paths end with /
        left_path = ensure_str(left_path).rstrip("/") + "/"
        right_path = ensure_str(right_path).rstrip("/") + "/"
        
        debug_print("Left path: {}".format(left_path))
        debug_print("Right path: {}".format(right_path))
        
        # Create file lists
        try:
            self["list_left"] = WestyFileList(
                left_path, 
                active=self.left_pane_active,
                show_hidden=show_hidden
            )
            self["list_left"].setSelectionManager(self.selection_manager, "left")
            
            self["list_right"] = WestyFileList(
                right_path, 
                active=not self.left_pane_active,
                show_hidden=show_hidden
            )
            self["list_right"].setSelectionManager(self.selection_manager, "right")
        except Exception as e:
            debug_print(f"ui.py: CRITICAL ERROR in screen __init__: {e}")
            debug_print(f"Error creating file lists: {e}")
            # Create simple mock file lists
            class MockFileList:
                def __init__(self, path, **kwargs):
                    self.current_directory = path
                    self.active = kwargs.get('active', False)
                    self.show_hidden = kwargs.get('show_hidden', False)
                def getCurrentDirectory(self): return self.current_directory
                def refresh(self): pass
                def setActive(self, active): self.active = active
                def getFilename(self): return None
                def up(self): pass
                def down(self): pass
                def pageUp(self): pass
                def pageDown(self): pass
                def canDescent(self): return False
                def descent(self): pass
            
            self["list_left"] = MockFileList(left_path, active=True, show_hidden=show_hidden)
            self["list_right"] = MockFileList(right_path, active=False, show_hidden=show_hidden)
        
        # Set current active list
        self.active_list = self["list_left"]
        self.inactive_list = self["list_right"]
        
        # Update selection manager
        self.selection_manager.set_current_pane(self.active_pane)
        
        # Update path labels
        self["left_path"].setText(self.shortenPath(left_path))
        self["right_path"].setText(self.shortenPath(right_path))
        
        # Log initialization
        self.console.log("FileMaster initialized: Left={}, Right={}".format(left_path, right_path))
    
    # ========================================================================
    # ACTION MAP SETUP
    # ========================================================================
    def setupActions(self):
        """Setup action map with arrow key navigation"""
        self["actions"] = ActionMap(["WizardActions", "DirectionActions", "ColorActions", "EPGSelectActions"],
        {
            # Arrow key navigation
            "left": self.navigateToLeftPane,
            "right": self.navigateToRightPane,
            "up": self.navigateUp,
            "down": self.navigateDown,
            
            # OK and Cancel
            "ok": self.enterDirectory,
            "cancel": self.exit,
            
            # Color buttons
            "red": self.exit,
            "green": self.copyOrMove,
            "yellow": self.openMenu,
            "blue": self.deleteOrRename,
            
            # Additional navigation
            "pageUp": self.pageUp,
            "pageDown": self.pageDown,
            "nextBouquet": self.switchPane,
            "prevBouquet": self.switchPane,
            
            # Info
            "info": self.showEnhancedFileInfo,
            
            # Multi-selection shortcuts
            "0": self.refreshView,
            "1": self.selectAll,
            "2": self.deselectAll,
            "3": self.toggleMultiSelectMode,
            "4": self.showBatchMenu,
            "5": self.showSelectionSummary,
            
            # Media playback
            "playpause": self.playSelectedMedia,
        }, -1)
    
    # ========================================================================
    # PANE NAVIGATION METHODS
    # ========================================================================
    def navigateToLeftPane(self):
        """Move focus to left pane using LEFT arrow key"""
        if self.active_pane == "right":
            self.switchToPane("left")
            self["status_bar"].setText(_("Left pane active"))
    
    def navigateToRightPane(self):
        """Move focus to right pane using RIGHT arrow key"""
        if self.active_pane == "left":
            self.switchToPane("right")
            self["status_bar"].setText(_("Right pane active"))
    
    def navigateUp(self):
        """Move up in current active list"""
        if hasattr(self.active_list, 'up'):
            self.active_list.up()
        self.updateFileInfo()
        self.updateSelectionDisplay()
    
    def navigateDown(self):
        """Move down in current active list"""
        if hasattr(self.active_list, 'down'):
            self.active_list.down()
        self.updateFileInfo()
        self.updateSelectionDisplay()
    
    def switchToPane(self, pane):
        """Switch active pane with visual feedback"""
        old_pane = self.active_pane
        self.active_pane = pane
        
        if pane == "left":
            self.active_list = self["list_left"]
            self.inactive_list = self["list_right"]
            # Update active state
            if hasattr(self["list_left"], 'setActive'):
                self["list_left"].setActive(True)
            if hasattr(self["list_right"], 'setActive'):
                self["list_right"].setActive(False)
        else:
            self.active_list = self["list_right"]
            self.inactive_list = self["list_left"]
            # Update active state
            if hasattr(self["list_left"], 'setActive'):
                self["list_left"].setActive(False)
            if hasattr(self["list_right"], 'setActive'):
                self["list_right"].setActive(True)
        
        # Update selection manager
        self.selection_manager.set_current_pane(self.active_pane)
        
        # Update visual highlighting
        self.updatePaneHighlight()
        
        # Update displays
        self.updateFileInfo()
        self.updateSelectionDisplay()
        
        # Log pane switch
        self.console.log("Switched from {} to {} pane".format(old_pane, pane))
    
    def updatePaneHighlight(self):
        """Update visual highlighting of active pane"""
        if self.active_pane == "left":
            # Highlight left pane
            self["left_header"].setText(_("← ACTIVE PANE"))
            self["right_header"].setText(_("RIGHT PANE"))
            
            # Show/hide active indicators
            if hasattr(self["left_pane_active"], 'show'):
                self["left_pane_active"].show()
            if hasattr(self["right_pane_active"], 'hide'):
                self["right_pane_active"].hide()
        else:
            # Highlight right pane
            self["left_header"].setText(_("LEFT PANE"))
            self["right_header"].setText(_("ACTIVE PANE →"))
            
            # Show/hide active indicators
            if hasattr(self["left_pane_active"], 'hide'):
                self["left_pane_active"].hide()
            if hasattr(self["right_pane_active"], 'show'):
                self["right_pane_active"].show()
    
    # ========================================================================
    # CONTEXT-SENSITIVE COLOR BUTTON METHODS
    # ========================================================================
    def copyOrMove(self):
        """🟢 GREEN button: Copy OR Move based on context"""
        if not ENIGMA2_DIALOGS_AVAILABLE:
            self["status_bar"].setText(_("Dialog not available"))
            return
        
        # Check if we have selections
        has_selections = self.selection_manager.get_selection_count() > 0
        
        if has_selections:
            # With selections: Show copy/move options
            count = self.selection_manager.get_selection_count()
            menu = [
                (_("Copy {} files").format(count), self.copySelectedFiles),
                (_("Move {} files").format(count), self.moveSelectedFiles),
                (_("Copy to..."), self.copyToLocation),
                (_("Move to..."), self.moveToLocation),
                (_("Cancel"), None)
            ]
            
            self.session.openWithCallback(
                lambda choice: choice[1]() if choice and choice[1] else None,
                ChoiceBox,
                title=_("Copy or Move?"),
                list=menu
            )
        else:
            # No selections: Just copy current file
            self.copyFile()
    
    def deleteOrRename(self):
        """🔵 BLUE button: Delete OR Rename based on context"""
        if not ENIGMA2_DIALOGS_AVAILABLE:
            self["status_bar"].setText(_("Dialog not available"))
            return
        
        # Check if we have selections
        has_selections = self.selection_manager.get_selection_count() > 0
        
        if has_selections:
            # With selections: Show delete/rename options
            count = self.selection_manager.get_selection_count()
            menu = [
                (_("Delete {} files").format(count), self.deleteSelectedFiles),
                (_("Rename {} files").format(count), self.renameSelectedFiles),
                (_("Secure Delete {} files").format(count), self.secureDeleteSelected),
                (_("Cancel"), None)
            ]
            
            self.session.openWithCallback(
                lambda choice: choice[1]() if choice and choice[1] else None,
                ChoiceBox,
                title=_("Delete or Rename?"),
                list=menu
            )
        else:
            # No selections: Single file operations
            filename = self.getCurrentFilename()
            if filename:
                menu = [
                    (_("Delete '{}'").format(filename), self.deleteFile),
                    (_("Rename '{}'").format(filename), self.renameFile),
                    (_("Properties"), self.showEnhancedFileInfo),
                    (_("Cancel"), None)
                ]
                
                self.session.openWithCallback(
                    lambda choice: choice[1]() if choice and choice[1] else None,
                    ChoiceBox,
                    title=_("File Operations"),
                    list=menu
                )
            else:
                self["status_bar"].setText(_("No file selected"))
    
    def getCurrentFilename(self):
        """Get filename from active list"""
        if hasattr(self.active_list, 'getFilename'):
            return self.active_list.getFilename()
        return None
    
    # ========================================================================
    # SELECTION AND BATCH OPERATIONS
    # ========================================================================
    def toggleMultiSelectMode(self):
        """Toggle multi-selection mode on/off"""
        self.multi_select_mode = not self.multi_select_mode
        mode_text = "MULTI-SELECT: ON" if self.multi_select_mode else "MULTI-SELECT: OFF"
        self["status_bar"].setText(mode_text)
        
        if not self.multi_select_mode:
            # Clear all selections when turning off multi-select
            self.clearSelections()
        
        self.updateSelectionDisplay()
        self.console.log("Multi-select mode: {}".format(self.multi_select_mode))
        return True
    
    def clearSelections(self):
        """Clear all selections"""
        self.selection_manager.clear_selection()
        self.last_selected_index = None
        self.updateSelectionDisplay()
        self.refreshFileLists()
        self["status_bar"].setText(_("Selection cleared"))
    
    def updateSelectionDisplay(self):
        """Update the selection status display"""
        count = self.selection_manager.get_selection_count()
        if count > 0:
            total_size = self.selection_manager.get_total_size()
            size_text = self.unit_scaler.format(total_size, 'bytes')
            status_text = _("Selected: {} items ({})").format(count, size_text)
            if self.multi_select_mode:
                status_text = "Ⓜ " + status_text
        else:
            status_text = _("No selection")
            if self.multi_select_mode:
                status_text = "Ⓜ " + status_text
        
        self["selection_status"].setText(status_text)
    
    def selectAll(self):
        """Select all items in active pane"""
        if not self.multi_select_mode:
            self.toggleMultiSelectMode()
        
        # Get file list
        file_list = self.getCurrentFileList()
        count = self.selection_manager.select_all_in_pane(file_list, self.active_pane)
        
        self.updateSelectionDisplay()
        self.refreshFileLists()
        self["status_bar"].setText(_("Selected all {} items").format(count))
    
    def deselectAll(self):
        """Deselect all items in active pane"""
        self.selection_manager.clear_selection(self.active_pane)
        self.updateSelectionDisplay()
        self.refreshFileLists()
        self["status_bar"].setText(_("Selection cleared"))
    
    def refreshFileLists(self):
        """Refresh both file lists to update selection highlighting"""
        if hasattr(self["list_left"], 'refresh'):
            self["list_left"].refresh()
        if hasattr(self["list_right"], 'refresh'):
            self["list_right"].refresh()
    
    def getCurrentFileList(self):
        """Get current list of files in active pane"""
        try:
            current_dir = self.active_list.getCurrentDirectory()
            items = []
            
            # Try to get items from the current directory
            if current_dir and os.path.exists(current_dir):
                for filename in os.listdir(current_dir):
                    # Skip hidden files if not showing them
                    if filename.startswith('.') and not getattr(self.active_list, 'show_hidden', False):
                        continue
                    
                    full_path = os.path.join(current_dir, filename)
                    
                    file_info = {
                        'name': filename,
                        'full_path': full_path,
                        'isdir': os.path.isdir(full_path),
                        'size': 0
                    }
                    
                    if not file_info['isdir']:
                        try:
                            file_info['size'] = os.path.getsize(full_path)
                        except:
                            pass
                    
                    items.append(file_info)
            
            return items
        except Exception as e:
            debug_print(f"ui.py: CRITICAL ERROR in screen __init__: {e}")
            debug_print("Error getting file list: {}".format(e))
            return []
    
    # ========================================================================
    # FILE OPERATIONS WITH MULTI-SELECT SUPPORT
    # ========================================================================
    def enterDirectory(self):
        """Enter selected directory or open file/play media"""
        if self.multi_select_mode:
            # In multi-select mode, handle selection
            self.handleFileSelection()
            return
        
        if hasattr(self.active_list, 'canDescent') and self.active_list.canDescent():
            # It's a directory - enter it
            if hasattr(self.active_list, 'descent'):
                # Clear cache for old directory before entering new one
                old_dir = self.active_list.getCurrentDirectory()
                self._clear_directory_cache(old_dir)
                
                self.active_list.descent()
                self.updatePathDisplay()
                self.updateFileInfo()
                self.updateSelectionDisplay()
                self.console.log("Entered directory: {}".format(self.active_list.getCurrentDirectory()))
        else:
            # It's a file - check if it's media and play it
            filename = self.getCurrentFilename()
            if filename:
                ext = os.path.splitext(filename)[1].lower()
                media_extensions = ('.mp4', '.avi', '.mkv', '.ts', '.mov', '.flv', '.m2ts', '.vob',
                                  '.mp3', '.flac', '.ogg', '.wav', '.aac', '.m4a',
                                  '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff')
                
                if ext in media_extensions:
                    # It's a media file - play it
                    self.playSelectedMedia()
                else:
                    # Regular file - use default file opening logic
                    self.openFile()
    def _clear_directory_cache(self, directory):
        """Clear cache for a directory when leaving it"""
        try:
            if CACHE_AVAILABLE:
                file_info_cache.invalidate_directory(directory)
                debug_print("Cleared cache for directory: %s" % directory)
        except Exception as e:
            debug_print(f"ui.py: CRITICAL ERROR in screen __init__: {e}")
            debug_print("Error clearing cache: %s" % str(e))

    def handleFileSelection(self):
        """Handle file selection with multi-select support"""
        filename = self.getCurrentFilename()
        if not filename:
            return
        
        current_dir = self.active_list.getCurrentDirectory()
        full_path = os.path.join(current_dir, filename)
        
        # Create file info
        file_info = {
            'name': filename,
            'full_path': full_path,
            'isdir': os.path.isdir(full_path),
            'size': 0
        }
        
        if not file_info['isdir']:
            try:
                file_info['size'] = os.path.getsize(full_path)
            except:
                pass
        
        # Toggle selection
        was_selected = self.selection_manager.is_selected(full_path, self.active_pane)
        if was_selected:
            self.selection_manager.deselect_item(full_path, self.active_pane)
        else:
            self.selection_manager.select_item(full_path, file_info, self.active_pane)
        
        self.updateSelectionDisplay()
        self.refreshFileLists()
        
        action = "Deselected" if was_selected else "Selected"
        self["status_bar"].setText("{} {}".format(action, filename))
    
    # ========================================================================
    # COPY OPERATIONS
    # ========================================================================
    def copyFile(self):
        """Copy single file to opposite pane"""
        filename = self.getCurrentFilename()
        if not filename:
            self["status_bar"].setText(_("No file selected"))
            return
        
        src_path = os.path.join(self.active_list.getCurrentDirectory(), filename)
        dest_dir = self.inactive_list.getCurrentDirectory()
        
        # Perform copy using batch_ops
        results = self.batch_ops.batch_copy([src_path], dest_dir, overwrite=False)
        
        if results.get('success'):
            self["status_bar"].setText(_("Copied: {}").format(filename))
            self.refreshView()
        else:
            self["status_bar"].setText(_("Copy failed"))
    
    def copySelectedFiles(self):
        """Copy selected files to opposite pane"""
        selected_paths = self.selection_manager.get_selected_paths(self.active_pane)
        if not selected_paths:
            self.showMessage(_("No files selected"), "error")
            return
        
        dest_dir = self.inactive_list.getCurrentDirectory()
        
        # Perform batch copy
        results = self.batch_ops.batch_copy(selected_paths, dest_dir, overwrite=False)
        
        self.showBatchResults(_("Copy"), results)
        
        # Clear selection after copy
        if self.multi_select_mode:
            self.clearSelections()
    
    def copyToLocation(self):
        """Copy selected files to chosen location"""
        selected_paths = self.selection_manager.get_selected_paths(self.active_pane)
        if not selected_paths:
            self.showMessage(_("No files selected"), "error")
            return
        
        # Show destination selection
        self.selectDestinationForBatch(_("Copy files to:"), 
                                      lambda dest: self.performBatchCopyTo(dest, selected_paths))
    
    def performBatchCopyTo(self, dest_dir, paths):
        """Perform batch copy to selected destination"""
        results = self.batch_ops.batch_copy(paths, dest_dir, overwrite=False)
        self.showBatchResults(_("Copy"), results)
        
        # Clear selection after copy
        if self.multi_select_mode:
            self.clearSelections()
    
    # ========================================================================
    # MOVE OPERATIONS
    # ========================================================================
    def moveFile(self):
        """Move single file to opposite pane"""
        filename = self.getCurrentFilename()
        if not filename:
            self["status_bar"].setText(_("No file selected"))
            return
        
        src_path = os.path.join(self.active_list.getCurrentDirectory(), filename)
        dest_dir = self.inactive_list.getCurrentDirectory()
        
        # Show confirmation
        if ENIGMA2_DIALOGS_AVAILABLE:
            self.session.openWithCallback(
                lambda result: self.confirmSingleMove(result, src_path, dest_dir),
                MessageBox,
                _("Move '{}' to {}?").format(filename, self.shortenPath(dest_dir)),
                MessageBox.TYPE_YESNO
            )
    
    def confirmSingleMove(self, result, src_path, dest_dir):
        """Confirm single file move"""
        if result:
            results = self.batch_ops.batch_move([src_path], dest_dir, overwrite=False)
            if results.get('success'):
                self["status_bar"].setText(_("Moved: {}").format(os.path.basename(src_path)))
                self.refreshView()
            else:
                self["status_bar"].setText(_("Move failed"))
    
    def moveSelectedFiles(self):
        """Move selected files to opposite pane"""
        selected_paths = self.selection_manager.get_selected_paths(self.active_pane)
        if not selected_paths:
            self.showMessage(_("No files selected"), "error")
            return
        
        dest_dir = self.inactive_list.getCurrentDirectory()
        
        # Show confirmation
        if ENIGMA2_DIALOGS_AVAILABLE:
            self.session.openWithCallback(
                lambda result: self.confirmBatchMove(result, selected_paths, dest_dir),
                MessageBox,
                _("Move {} files to {}?").format(len(selected_paths), self.shortenPath(dest_dir)),
                MessageBox.TYPE_YESNO
            )
    
    def confirmBatchMove(self, result, paths, dest_dir):
        """Confirm batch move"""
        if result:
            results = self.batch_ops.batch_move(paths, dest_dir, overwrite=False)
            self.showBatchResults(_("Move"), results)
            
            # Clear selection after move
            if self.multi_select_mode:
                self.clearSelections()
    
    def moveToLocation(self):
        """Move selected files to chosen location"""
        selected_paths = self.selection_manager.get_selected_paths(self.active_pane)
        if not selected_paths:
            self.showMessage(_("No files selected"), "error")
            return
        
        # Show destination selection
        self.selectDestinationForBatch(_("Move files to:"), 
                                      lambda dest: self.performBatchMoveTo(dest, selected_paths))
    
    def performBatchMoveTo(self, dest_dir, paths):
        """Perform batch move to selected destination"""
        results = self.batch_ops.batch_move(paths, dest_dir, overwrite=False)
        self.showBatchResults(_("Move"), results)
        
        # Clear selection after move
        if self.multi_select_mode:
            self.clearSelections()
    
    # ========================================================================
    # DELETE OPERATIONS
    # ========================================================================
    def deleteFile(self):
        """Delete single file"""
        filename = self.getCurrentFilename()
        if not filename:
            self["status_bar"].setText(_("No file selected"))
            return
        
        filepath = os.path.join(self.active_list.getCurrentDirectory(), filename)
        
        # Show confirmation
        if ENIGMA2_DIALOGS_AVAILABLE:
            self.session.openWithCallback(
                lambda result: self.confirmSingleDelete(result, filepath),
                MessageBox,
                _("Are you sure you want to delete '{}'?").format(filename),
                MessageBox.TYPE_YESNO
            )
    
    def confirmSingleDelete(self, result, filepath):
        """Confirm single file delete"""
        if result:
            results = self.batch_ops.batch_delete([filepath], secure=False)
            if results.get('success'):
                self["status_bar"].setText(_("Deleted: {}").format(os.path.basename(filepath)))
                self.refreshView()
            else:
                self["status_bar"].setText(_("Delete failed"))
    
    def deleteSelectedFiles(self):
        """Delete selected files"""
        selected_paths = self.selection_manager.get_selected_paths(self.active_pane)
        if not selected_paths:
            self.showMessage(_("No files selected"), "error")
            return
        
        # Show confirmation
        if ENIGMA2_DIALOGS_AVAILABLE:
            self.session.openWithCallback(
                lambda result: self.confirmBatchDelete(result, selected_paths, False),
                MessageBox,
                _("Are you sure you want to delete {} files?").format(len(selected_paths)),
                MessageBox.TYPE_YESNO
            )
    
    def secureDeleteSelected(self):
        """Securely delete selected files"""
        selected_paths = self.selection_manager.get_selected_paths(self.active_pane)
        if not selected_paths:
            self.showMessage(_("No files selected"), "error")
            return
        
        # Show confirmation
        if ENIGMA2_DIALOGS_AVAILABLE:
            self.session.openWithCallback(
                lambda result: self.confirmBatchDelete(result, selected_paths, True),
                MessageBox,
                _("Securely delete {} files? (Overwrites before deleting)").format(len(selected_paths)),
                MessageBox.TYPE_YESNO
            )
    
    def confirmBatchDelete(self, result, paths, secure):
        """Confirm batch delete"""
        if result:
            results = self.batch_ops.batch_delete(paths, secure=secure)
            self.showBatchResults(_("Delete"), results)
            
            # Clear selection after delete
            if self.multi_select_mode:
                self.clearSelections()
    
    # ========================================================================
    # RENAME OPERATIONS
    # ========================================================================
    def renameFile(self):
        """Rename single file"""
        filename = self.getCurrentFilename()
        if not filename:
            self["status_bar"].setText(_("No file selected"))
            return
        
        if ENIGMA2_DIALOGS_AVAILABLE:
            self.session.openWithCallback(
                lambda newname: self.performSingleRename(newname, filename),
                VirtualKeyBoard,
                title=_("Enter new name"),
                text=filename
            )
    
    def performSingleRename(self, newname, oldname):
        """Perform single file rename"""
        if newname and newname != oldname:
            old_path = os.path.join(self.active_list.getCurrentDirectory(), oldname)
            rename_list = [{'old_path': old_path, 'new_name': newname}]
            
            results = self.batch_ops.batch_rename(rename_list)
            if results.get('success'):
                self["status_bar"].setText(_("Renamed to: {}").format(newname))
                self.refreshView()
            else:
                self["status_bar"].setText(_("Rename failed"))
    
    def renameSelectedFiles(self):
        """Rename multiple selected files"""
        selected_paths = self.selection_manager.get_selected_paths(self.active_pane)
        if not selected_paths:
            self.showMessage(_("No files selected"), "error")
            return
        
        if len(selected_paths) == 1:
            # Single file: Use normal rename
            self.renameFile()
        else:
            # Multiple files: Show batch rename
            if ENIGMA2_DIALOGS_AVAILABLE:
                self.session.openWithCallback(
                    lambda pattern: self.performBatchRename(pattern, selected_paths),
                    VirtualKeyBoard,
                    title=_("Enter rename pattern (use {name}, {ext}, {n}, {date})"),
                    text="renamed_{name}_{n:03d}{ext}"
                )
    
    def performBatchRename(self, pattern, paths):
        """Perform batch rename with pattern"""
        if not pattern:
            return
        
        # Prepare rename list
        rename_list = []
        for path in paths:
            old_name = os.path.basename(path)
            rename_list.append({
                'old_path': path,
                'new_name': old_name  # Will be replaced by pattern in batch_rename
            })
        
        # Perform batch rename
        results = self.batch_ops.batch_rename(rename_list, pattern)
        
        self.showBatchResults(_("Rename"), results)
        
        # Clear selection after rename
        if self.multi_select_mode:
            self.clearSelections()
    
    # ========================================================================
    # BATCH OPERATIONS MENU
    # ========================================================================
    def showBatchMenu(self):
        """Show batch operations menu"""
        if not ENIGMA2_DIALOGS_AVAILABLE:
            self["status_bar"].setText(_("Dialog not available"))
            return
        
        has_selections = self.selection_manager.get_selection_count() > 0
        
        menu = [
            (_("Batch Copy"), self.batchCopySelected),
            (_("Batch Move"), self.batchMoveSelected),
            (_("Batch Delete"), self.batchDeleteSelected),
            (_("Batch Rename"), self.batchRenameSelected),
            (_("Batch Change Permissions"), self.batchChangePermissions),
            (_("Batch Compress"), self.batchCompressSelected),
            (_("Selection Summary"), self.showSelectionSummary),
        ]
        
        if has_selections:
            menu.append((_("Clear Selection"), self.clearSelections))
        
        menu.append((_("Toggle Multi-Select"), self.toggleMultiSelectMode))
        menu.append((_("Cancel"), None))
        
        self.session.openWithCallback(self.batchMenuCallback, ChoiceBox, 
                                    title=_("Batch Operations"), list=menu)
    
    def batchMenuCallback(self, choice):
        """Handle batch menu selection"""
        if choice and choice[1]:
            choice[1]()
    
    def batchCopySelected(self):
        """Copy selected files to destination"""
        selected_paths = self.selection_manager.get_selected_paths(self.active_pane)
        if not selected_paths:
            self.showMessage(_("No files selected"), "error")
            return
        
        # Show destination selection
        self.selectDestinationForBatch(_("Copy files to:"), 
                                      lambda dest: self.performBatchCopy(dest, selected_paths))
    
    def performBatchCopy(self, dest_dir, paths):
        """Perform batch copy to selected destination"""
        results = self.batch_ops.batch_copy(paths, dest_dir, overwrite=False)
        self.showBatchResults(_("Copy"), results)
        
        # Clear selection after copy
        if self.multi_select_mode:
            self.clearSelections()
    
    def batchMoveSelected(self):
        """Move selected files to destination"""
        selected_paths = self.selection_manager.get_selected_paths(self.active_pane)
        if not selected_paths:
            self.showMessage(_("No files selected"), "error")
            return
        
        # Show destination selection
        self.selectDestinationForBatch(_("Move files to:"), 
                                      lambda dest: self.performBatchMove(dest, selected_paths))
    
    def performBatchMove(self, dest_dir, paths):
        """Perform batch move to selected destination"""
        results = self.batch_ops.batch_move(paths, dest_dir, overwrite=False)
        self.showBatchResults(_("Move"), results)
        
        # Clear selection after move
        if self.multi_select_mode:
            self.clearSelections()
    
    def batchDeleteSelected(self):
        """Delete selected files"""
        self.deleteSelectedFiles()  # Reuse existing method
    
    def batchRenameSelected(self):
        """Rename selected files"""
        self.renameSelectedFiles()  # Reuse existing method
    
    def batchChangePermissions(self):
        """Change permissions for selected files"""
        selected_paths = self.selection_manager.get_selected_paths(self.active_pane)
        if not selected_paths:
            self.showMessage(_("No files selected"), "error")
            return
        
        # Show permissions dialog
        if ENIGMA2_DIALOGS_AVAILABLE:
            self.session.openWithCallback(
                lambda mode: self.performBatchChmod(mode, selected_paths),
                InputBox,
                title=_("Enter permissions (e.g., 755 for rwxr-xr-x)"),
                windowTitle=_("Change Permissions"),
                text="755"
            )
    
    def performBatchChmod(self, mode_str, paths):
        """Perform batch permissions change"""
        if not mode_str:
            return
        
        try:
            # Convert string to octal integer
            mode = int(mode_str, 8)
            results = self.batch_ops.batch_chmod(paths, mode, recursive=False)
            self.showBatchResults(_("Change Permissions"), results)
        except ValueError:
            self.showMessage(_("Invalid permissions format"), "error")
    
    def batchCompressSelected(self):
        """Compress selected files"""
        selected_paths = self.selection_manager.get_selected_paths(self.active_pane)
        if not selected_paths:
            self.showMessage(_("No files selected"), "error")
            return
        
        # Show compression options
        if ENIGMA2_DIALOGS_AVAILABLE:
            formats = [
                (_("ZIP Archive (.zip)"), "zip"),
                (_("GZip Tarball (.tar.gz)"), "gztar"),
                (_("BZip2 Tarball (.tar.bz2)"), "bztar"),
                (_("XZ Tarball (.tar.xz)"), "xztar"),
                (_("Tar Archive (.tar)"), "tar"),
            ]
            
            self.session.openWithCallback(
                lambda choice: self.selectCompressionDestination(choice, selected_paths) if choice else None,
                ChoiceBox,
                title=_("Select Archive Format"),
                list=formats
            )
    
    def selectCompressionDestination(self, choice, paths):
        """Select destination for compressed archive"""
        if not choice:
            return
        
        format_name, format_ext = choice[0], choice[1]
        
        # Get default archive name
        if len(paths) == 1:
            default_name = os.path.basename(paths[0]) + "." + {
                'zip': 'zip',
                'gztar': 'tar.gz',
                'bztar': 'tar.bz2',
                'xztar': 'tar.xz',
                'tar': 'tar'
            }.get(format_ext, 'zip')
        else:
            default_name = "archive." + {
                'zip': 'zip',
                'gztar': 'tar.gz',
                'bztar': 'tar.bz2',
                'xztar': 'tar.xz',
                'tar': 'tar'
            }.get(format_ext, 'zip')
        
        # Show destination dialog
        if ENIGMA2_DIALOGS_AVAILABLE:
            self.session.openWithCallback(
                lambda name: self.performBatchCompress(name, format_ext, paths) if name else None,
                VirtualKeyBoard,
                title=_("Enter archive name"),
                text=default_name
            )
    
    def performBatchCompress(self, archive_name, format_ext, paths):
        """Perform batch compression"""
        # Build full archive path
        dest_dir = self.active_list.getCurrentDirectory()
        archive_path = os.path.join(dest_dir, archive_name)
        
        results = self.batch_ops.batch_compress(paths, archive_path, format_ext)
        
        if results.get('success'):
            self.showMessage(_("Created archive: {}").format(archive_name), "info")
            self.refreshView()
        else:
            self.showMessage(_("Compression failed: {}").format(results.get('error', 'Unknown error')), "error")
    
    def showSelectionSummary(self):
        """Show summary of selected files"""
        selected_paths = self.selection_manager.get_selected_paths(self.active_pane)
        
        if not selected_paths:
            self.showMessage(_("No files selected"), "error")
            return
        
        summary = self.batch_ops.get_batch_summary(selected_paths)
        
        # Format summary message
        if ENIGMA2_DIALOGS_AVAILABLE:
            msg_lines = [
                _("Selection Summary:"),
                _("Total items: {}").format(summary['total_count']),
                _("Files: {}").format(summary['file_count']),
                _("Directories: {}").format(summary['dir_count']),
                _("Total size: {}").format(summary.get('formatted_size', '0 B')),
            ]
            
            if summary.get('largest_file'):
                msg_lines.append(_("Largest file: {} ({})").format(
                    os.path.basename(summary['largest_file']),
                    summary.get('formatted_largest', '0 B')
                ))
            
            if summary.get('oldest_date'):
                msg_lines.append(_("Oldest: {}").format(summary['oldest_date']))
                msg_lines.append(_("Newest: {}").format(summary['newest_date']))
            
            if summary.get('extensions'):
                msg_lines.append(_("\nFile extensions:"))
                for ext, count in sorted(summary['extensions'].items()):
                    if ext:  # Skip empty extensions
                        msg_lines.append(f"  {ext}: {count}")
            
            self.session.open(MessageBox, "\n".join(msg_lines), MessageBox.TYPE_INFO)
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    def selectDestinationForBatch(self, title, callback):
        """Select destination directory for batch operation"""
        if not ENIGMA2_DIALOGS_AVAILABLE:
            self["status_bar"].setText(_("Dialog not available"))
            return
        
        menu = [
            (_("Opposite Pane ({})").format(self.shortenPath(self.inactive_list.getCurrentDirectory())), 
             lambda: callback(self.inactive_list.getCurrentDirectory())),
            (_("Same Directory"), 
             lambda: callback(self.active_list.getCurrentDirectory())),
            (_("Cancel"), None)
        ]
        
        self.session.openWithCallback(
            lambda choice: choice[1]() if choice and choice[1] else None,
            ChoiceBox,
            title=title,
            list=menu
        )
    
    def showBatchResults(self, operation, results):
        """Show results of batch operation"""
        success_count = len(results.get('success', []))
        failed_count = len(results.get('failed', []))
        skipped_count = len(results.get('skipped', []))
        
        if success_count == 0 and failed_count == 0:
            self["status_bar"].setText(_("No files processed"))
            return
        
        message = _("{}: {} successful").format(operation, success_count)
        if failed_count > 0:
            message += _(", {} failed").format(failed_count)
        if skipped_count > 0:
            message += _(", {} skipped").format(skipped_count)
        
        self["status_bar"].setText(message)
        self.refreshView()
    
    def showMessage(self, message, msg_type="info"):
        """Show a message to the user"""
        if not ENIGMA2_DIALOGS_AVAILABLE:
            self["status_bar"].setText(message)
            return
        
        if msg_type == "error":
            mbox_type = MessageBox.TYPE_ERROR
        elif msg_type == "warning":
            mbox_type = MessageBox.TYPE_WARNING
        else:
            mbox_type = MessageBox.TYPE_INFO
        
        self.session.open(MessageBox, message, mbox_type)
    
    def shortenPath(self, path, max_length=50):
        """Shorten long paths for display"""
        if len(path) > max_length:
            # Try to keep beginning and end
            keep = (max_length - 3) // 2
            return path[:keep] + "..." + path[-keep:]
        return path
    
    def updatePathDisplay(self):
        """Update path labels"""
        left_path = self["list_left"].getCurrentDirectory() if hasattr(self["list_left"], 'getCurrentDirectory') else ""
        right_path = self["list_right"].getCurrentDirectory() if hasattr(self["list_right"], 'getCurrentDirectory') else ""
        
        self["left_path"].setText(self.shortenPath(left_path))
        self["right_path"].setText(self.shortenPath(right_path))
    
    def updateFileInfo(self):
        """Update file information display"""
        filename = self.getCurrentFilename()
        if filename:
            current_dir = self.active_list.getCurrentDirectory()
            full_path = os.path.join(current_dir, filename) if current_dir else filename
            
            if os.path.isdir(full_path):
                file_type = _("Folder")
                try:
                    count = len([f for f in os.listdir(full_path) if not f.startswith('.') or getattr(self.active_list, 'show_hidden', False)])
                    info = _("Items: {}").format(count)
                except:
                    info = _("Inaccessible")
            else:
                file_type = _("File")
                # Check if it's a media file
                ext = os.path.splitext(filename)[1].lower()
                if ext in ('.mp4', '.avi', '.mkv', '.ts', '.mov', '.flv'):
                    file_type = _("Video")
                elif ext in ('.mp3', '.flac', '.ogg', '.wav', '.aac'):
                    file_type = _("Audio")
                elif ext in ('.jpg', '.jpeg', '.png', '.gif', '.bmp'):
                    file_type = _("Image")
                
                try:
                    size = os.path.getsize(full_path)
                    info = _("Size: {}").format(self.unit_scaler.format(size, 'bytes'))
                except:
                    info = _("Unknown size")
            
            if self.active_pane == "left":
                self["left_info"].setText("{} | {}".format(file_type, info))
                self["right_info"].setText("")
            else:
                self["right_info"].setText("{} | {}".format(file_type, info))
                self["left_info"].setText("")
        else:
            # Clear info if no file selected
            if self.active_pane == "left":
                self["left_info"].setText("")
            else:
                self["right_info"].setText("")
    
    def updateStatus(self):
        """Update status bar with system info"""
        import time
        current_time = time.strftime("%H:%M:%S")
        
        # Get free space for current directory
        try:
            if self.active_pane == "left":
                path = self["list_left"].getCurrentDirectory() if hasattr(self["list_left"], 'getCurrentDirectory') else ""
            else:
                path = self["list_right"].getCurrentDirectory() if hasattr(self["list_right"], 'getCurrentDirectory') else ""
            
            if path and os.path.exists(path):
                stat = os.statvfs(path)
                free_bytes = stat.f_bavail * stat.f_frsize
                free_str = self.unit_scaler.format(free_bytes, 'bytes')
                status = _("{} | Free: {}").format(current_time, free_str)
            else:
                status = _("{} | Ready").format(current_time)
        except Exception as e:
            debug_print(f"ui.py: CRITICAL ERROR in screen __init__: {e}")
            debug_print("Error getting disk space: {}".format(e))
            status = _("{} | System ready").format(current_time)
        
        self["status_bar"].setText(status)
    
    # ========================================================================
    # ENHANCED FEATURES
    # ========================================================================
    def openConsole(self):
        """Open enhanced console"""
        self.console.open_console(self.session)
    
    def openTaskList(self):
        """Open task list screen"""
        self.session.open(self.task_list)
    
    def showEnhancedFileInfo(self):
        """Show enhanced file information"""
        filename = self.getCurrentFilename()
        if filename:
            if ENIGMA2_DIALOGS_AVAILABLE:
                current_dir = self.active_list.getCurrentDirectory()
                fullpath = os.path.join(current_dir, filename) if current_dir else filename
                
                try:
                    stat = os.stat(fullpath)
                    import time
                    
                    # Get enhanced information
                    size_formatted = self.unit_scaler.format(stat.st_size, 'bytes')
                    
                    info = _("""
File: {}
Size: {} ({:,} bytes)
Type: {}
Created: {}
Modified: {}
Accessed: {}
Permissions: {:o}
Owner: {}:{}
                    """).format(
                        filename,
                        size_formatted,
                        stat.st_size,
                        self.get_file_type(fullpath),
                        time.ctime(stat.st_ctime),
                        time.ctime(stat.st_mtime),
                        time.ctime(stat.st_atime),
                        stat.st_mode & 0o777,
                        stat.st_uid,
                        stat.st_gid
                    )
                except Exception as e:
                    debug_print(f"ui.py: Error getting file info: {e}")
                    info = _("Could not read file information: {}").format(str(e))
                
                self.session.open(MessageBox, info, MessageBox.TYPE_INFO)
    
    def get_file_type(self, path):
        """Get detailed file type"""
        if os.path.isdir(path):
            return _("Directory")
        elif os.path.islink(path):
            return _("Symbolic Link")
        elif os.path.isfile(path):
            # Check extension
            ext = os.path.splitext(path)[1].lower()
            if ext in ('.py', '.pyc', '.pyo'):
                return _("Python Script")
            elif ext in ('.sh', '.bash'):
                return _("Shell Script")
            elif ext in ('.txt', '.log', '.cfg', '.conf'):
                return _("Text File")
            elif ext in ('.jpg', '.jpeg', '.png', '.gif', '.bmp'):
                return _("Image File")
            elif ext in ('.mp3', '.flac', '.wav', '.ogg'):
                return _("Audio File")
            elif ext in ('.mp4', '.avi', '.mkv', '.mov'):
                return _("Video File")
            else:
                return _("File")
        else:
            return _("Special File")
    
    def openMenu(self):
        """Open enhanced context menu"""
        if not ENIGMA2_DIALOGS_AVAILABLE:
            self["status_bar"].setText(_("Menu not available"))
            return
        
        menu = [
            (_("Refresh View"), self.refreshView),
            (_("New Folder"), self.createFolder),
            (_("New File"), self.createFile),
            (_("Rename"), self.renameFile),
            (_("Properties"), self.showEnhancedFileInfo),
            (_("Play Media"), self.playSelectedMedia),
            (_("Open Console"), self.openConsole),
            (_("Task List"), self.openTaskList),
            (_("Select All"), self.selectAll),
            (_("Settings"), self.openSettings),
        ]
        
        self.session.openWithCallback(self.menuCallback, ChoiceBox, 
                                    title=_("FileMaster PRO Menu"), list=menu)
    
    def menuCallback(self, choice):
        """Handle menu selection"""
        if choice and choice[1]:
            choice[1]()
    
    # ========================================================================
    # ADDITIONAL METHODS
    # ========================================================================
    def refreshView(self):
        """Refresh both panes"""
        if hasattr(self["list_left"], 'refresh'):
            self["list_left"].refresh()
        if hasattr(self["list_right"], 'refresh'):
            self["list_right"].refresh()
        self.updatePathDisplay()
        self.updateFileInfo()
        self.updateSelectionDisplay()
        self["status_bar"].setText(_("View refreshed"))
        self.console.log("View refreshed")
    
    def createFolder(self):
        """Create new folder"""
        if not ENIGMA2_DIALOGS_AVAILABLE:
            self["status_bar"].setText(_("Keyboard not available"))
            return
        
        self.session.openWithCallback(self.folderCreated, VirtualKeyBoard,
                                    title=_("Enter folder name"), text=_("NewFolder"))
    
    def folderCreated(self, name):
        if name:
            current_dir = self.active_list.getCurrentDirectory()
            path = os.path.join(current_dir, ensure_str(name))
            try:
                os.mkdir(path)
                self.refreshView()
                self["status_bar"].setText(_("Folder created: {}").format(name))
                self.console.log("Folder created: {}".format(path))
            except Exception as e:
                debug_print(f"ui.py: Error creating folder: {e}")
                self["status_bar"].setText(_("Error: {}").format(str(e)))
    
    def createFile(self):
        """Create new file"""
        if not ENIGMA2_DIALOGS_AVAILABLE:
            self["status_bar"].setText(_("Keyboard not available"))
            return
        
        self.session.openWithCallback(self.fileCreated, VirtualKeyBoard,
                                    title=_("Enter filename"), text=_("newfile.txt"))
    
    def fileCreated(self, name):
        if name:
            current_dir = self.active_list.getCurrentDirectory()
            path = os.path.join(current_dir, ensure_str(name))
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write('')
                self.refreshView()
                self["status_bar"].setText(_("File created: {}").format(name))
                self.console.log("File created: {}".format(path))
            except Exception as e:
                debug_print(f"ui.py: Error creating file: {e}")
                self["status_bar"].setText(_("Error: {}").format(str(e)))
    
    def openSettings(self):
        """Open settings screen"""
        if SETUP_AVAILABLE:
            self.session.open(WestyFileMasterSetup)
        else:
            if ENIGMA2_DIALOGS_AVAILABLE:
                self.session.open(MessageBox, 
                                _("Settings screen not available yet."),
                                MessageBox.TYPE_INFO)
    
    def pageUp(self):
        """Page up in current list"""
        if hasattr(self.active_list, 'pageUp'):
            self.active_list.pageUp()
    
    def pageDown(self):
        """Page down in current list"""
        if hasattr(self.active_list, 'pageDown'):
            self.active_list.pageDown()
    
    def switchPane(self):
        """Toggle between panes (alternative method)"""
        if self.active_pane == "left":
            self.switchToPane("right")
        else:
            self.switchToPane("left")
    
    def openFile(self):
        """Open selected file with appropriate viewer"""
        filename = self.getCurrentFilename()
        if filename:
            self["status_bar"].setText(_("Opening: {}").format(filename))
            self.showEnhancedFileInfo()
    
    def playSelectedMedia(self):
        """Play selected media file"""
        filename = self.getCurrentFilename()
        if filename:
            current_dir = self.active_list.getCurrentDirectory()
            filepath = os.path.join(current_dir, filename) if current_dir else filename
            ext = os.path.splitext(filename)[1].lower()
            
            # Video files
            if ext in ('.mp4', '.avi', '.mkv', '.ts', '.mov', '.flv', '.m2ts', '.vob'):
                try:
                    playMedia(self.session, filepath)
                    self["status_bar"].setText(_("Playing video: {}").format(filename))
                    self.console.log("Playing video: {}".format(filename))
                except:
                    self["status_bar"].setText(_("Cannot play video: {}").format(filename))
            
            # Audio files
            elif ext in ('.mp3', '.flac', '.ogg', '.wav', '.aac', '.m4a'):
                try:
                    playAudio(self.session, filepath)
                    self["status_bar"].setText(_("Playing audio: {}").format(filename))
                    self.console.log("Playing audio: {}".format(filename))
                except:
                    self["status_bar"].setText(_("Cannot play audio: {}").format(filename))
            
            # Image files
            elif ext in ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'):
                try:
                    viewImage(self.session, filepath)
                    self["status_bar"].setText(_("Viewing image: {}").format(filename))
                    self.console.log("Viewing image: {}".format(filename))
                except:
                    self["status_bar"].setText(_("Cannot view image: {}").format(filename))
            else:
                self["status_bar"].setText(_("Unsupported media format: {}").format(ext))
        else:
            self["status_bar"].setText(_("No file selected"))
    
    def exit(self):
        """Exit the file manager"""
        if hasattr(self, 'refresh_timer'):
            try:
                self.refresh_timer.stop()
            except:
                pass
        
        # Clean up modules
        for module in ['console', 'file_transfer']:
            if hasattr(self, module) and hasattr(getattr(self, module), 'cleanup'):
                try:
                    getattr(self, module).cleanup()
                except:
                    pass
        
        self.close()
        debug_print("FileMaster closed")

# ============================================================================
# TEST FUNCTION
# ============================================================================
if __name__ == "__main__":
    print("Westy FileMaster PRO UI Test")
    print("=" * 60)
    print("Plugin: {} v{}".format(PLUGIN_NAME, PLUGIN_VERSION))
    print("UI module requires Enigma2/OpenATV environment")
    print("=" * 60)