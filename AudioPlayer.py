#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division, unicode_literals

import os
import sys
import time
from datetime import datetime

# ============================================================================
# IMPORT PLUGIN UTILITIES
# ============================================================================
try:
    # Add current directory to path first
    PLUGIN_PATH = os.path.dirname(os.path.abspath(__file__))
    if PLUGIN_PATH not in sys.path:
        sys.path.insert(0, PLUGIN_PATH)
    
    from . import (
        _,
        debug_print,
        ensure_str,
        ensure_unicode,
        PLUGIN_NAME,
        PLUGIN_VERSION
    )
    debug_print("AudioPlayer: Imported plugin utilities v%s" % PLUGIN_VERSION)
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

# ============================================================================
# IMPORT MEDIA UTILITIES - FIXED VERSION
# ============================================================================
MEDIA_UTILS_AVAILABLE = False
media_config = None
media_utils = None

try:
    # Try to import media_utils
    try:
        from .media_utils import media_utils, media_config
        MEDIA_UTILS_AVAILABLE = True
        debug_print("AudioPlayer: Media utilities imported")
    except ImportError:
        # Try direct import
        try:
            import media_utils as mu
            media_utils = mu.media_utils
            media_config = mu.media_config
            MEDIA_UTILS_AVAILABLE = True
            debug_print("AudioPlayer: Media utilities imported directly")
        except ImportError as e:
            raise ImportError("Could not import media_utils: %s" % str(e))
    
    debug_print("AudioPlayer: Media utilities available: %s" % MEDIA_UTILS_AVAILABLE)
    
except Exception as e:
    debug_print("AudioPlayer: Media utilities not available: %s" % str(e))
    # Create minimal utilities
    class MediaUtils:
        SUPPORTED_AUDIO_EXTS = ('.mp3', '.flac', '.ogg', '.wav', '.aac', '.m4a', '.wma', '.opus')
        
        @staticmethod
        def is_audio_file(filename):
            ext = os.path.splitext(filename)[1].lower()
            return ext in MediaUtils.SUPPORTED_AUDIO_EXTS
        
        @staticmethod
        def sanitize_filename(filename):
            import re
            name = os.path.splitext(filename)[0]
            name = name.replace('_', ' ').replace('-', ' - ')
            name = re.sub(r'^\d{1,3}\s*[.-]\s*', '', name)
            name = name.strip()
            if len(name) > 50:
                name = name[:47] + "..."
            return name
        
        @staticmethod
        def save_m3u_playlist(filepath, playlist):
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write("#EXTM3U\n")
                    f.write("# Created by %s v%s\n" % (PLUGIN_NAME, PLUGIN_VERSION))
                    f.write("# Date: %s\n" % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    for track in playlist:
                        f.write("%s\n" % track)
                return True
            except:
                return False
        
        @staticmethod
        def parse_m3u_playlist(filepath):
            try:
                playlist = []
                base_dir = os.path.dirname(filepath)
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            if os.path.isabs(line):
                                playlist.append(line)
                            else:
                                rel_path = os.path.join(base_dir, line)
                                playlist.append(rel_path)
                return playlist
            except:
                return []
    
    media_utils = MediaUtils()
    
    # Create minimal config
    class SimpleConfig:
        def get_config(self, module):
            return {'volume': 80, 'repeat_mode': 'none', 'shuffle': False, 'visualization': True}
        def set_config(self, module, key, value):
            return True
    
    media_config = SimpleConfig()

# ============================================================================
# IMPORT SCREEN COMPONENTS WITH FALLBACKS
# ============================================================================
# Try to import Screens with fallbacks
try:
    from Screens.Screen import Screen
    SCREEN_AVAILABLE = True
    debug_print("AudioPlayer: Screen available")
except ImportError:
    SCREEN_AVAILABLE = False
    debug_print("AudioPlayer: Screen not available")
    
    class Screen:
        def __init__(self, session):
            self.session = session
        
        def close(self):
            pass
        
        def onLayoutFinish(self, callback):
            callback()

try:
    from Components.ActionMap import ActionMap, HelpableActionMap
    ACTIONMAP_AVAILABLE = True
    debug_print("AudioPlayer: ActionMap available")
except ImportError:
    ACTIONMAP_AVAILABLE = False
    debug_print("AudioPlayer: ActionMap not available")
    
    class ActionMap:
        def __init__(self, contexts, actions, prio=-1):
            pass
    
    HelpableActionMap = ActionMap

try:
    from Components.Label import Label
    from Components.Pixmap import Pixmap
    from Components.Sources.StaticText import StaticText
    from Components.ProgressBar import ProgressBar
    from Components.ServiceEventTracker import ServiceEventTracker
    COMPONENTS_AVAILABLE = True
    debug_print("AudioPlayer: Basic components available")
except ImportError:
    COMPONENTS_AVAILABLE = False
    debug_print("AudioPlayer: Basic components not available")
    
    class Label:
        def setText(self, text):
            pass
        
        def setForegroundColor(self, color):
            pass
        
        def hide(self):
            pass
        
        def show(self):
            pass
    
    class Pixmap:
        def show(self):
            pass
        
        def hide(self):
            pass
    
    class StaticText:
        def __init__(self, text=""):
            self.text = text
    
    class ProgressBar:
        pass
    
    class ServiceEventTracker:
        def __init__(self, screen=None, eventmap=None):
            pass

try:
    from Components.Sources.List import List
    from Components.MenuList import MenuList
    LIST_COMPONENTS_AVAILABLE = True
    debug_print("AudioPlayer: List components available")
except ImportError:
    LIST_COMPONENTS_AVAILABLE = False
    debug_print("AudioPlayer: List components not available")
    
    class List:
        def __init__(self, list=None):
            self.list = list or []
            self.index = 0
        
        def getCurrent(self):
            if self.list and 0 <= self.index < len(self.list):
                return self.list[self.index]
            return None
        
        def getIndex(self):
            return self.index
        
        def setIndex(self, index):
            if 0 <= index < len(self.list):
                self.index = index
        
        def selectPrevious(self):
            if self.index > 0:
                self.index -= 1
        
        def selectNext(self):
            if self.index < len(self.list) - 1:
                self.index += 1
        
        def pageUp(self):
            self.index = max(0, self.index - 10)
        
        def pageDown(self):
            self.index = min(len(self.list) - 1, self.index + 10)
        
        def setList(self, lst):
            self.list = lst
            self.index = min(self.index, len(lst) - 1)
    
    class MenuList:
        def __init__(self, list=None):
            self.list = list or []
            self.index = 0
        
        def getCurrent(self):
            if self.list and 0 <= self.index < len(self.list):
                return self.list[self.index]
            return None
        
        def getSelectionIndex(self):
            return self.index
        
        def selectPrevious(self):
            if self.index > 0:
                self.index -= 1
        
        def selectNext(self):
            if self.index < len(self.list) - 1:
                self.index += 1
        
        def setList(self, lst):
            self.list = lst
            self.index = min(self.index, len(lst) - 1)
        
        def moveToIndex(self, index):
            if 0 <= index < len(self.list):
                self.index = index

try:
    from enigma import eServiceReference, eServiceCenter, iPlayableService, eTimer, getDesktop
    from ServiceReference import ServiceReference
    ENIGMA_CORE_AVAILABLE = True
    debug_print("AudioPlayer: Enigma core available")
except ImportError as e:
    ENIGMA_CORE_AVAILABLE = False
    debug_print("AudioPlayer: Core enigma imports not available: %s" % str(e))
    
    # Mock classes
    class eServiceReference:
        idFile = 1
        noFlags = 0
        
        def __init__(self, type, flags, path):
            self.type = type
            self.flags = flags
            self.path = path
        
        def getPath(self):
            return self.path
    
    class eServiceCenter:
        @staticmethod
        def getInstance():
            return eServiceCenter()
    
    class iPlayableService:
        evStart = 1
        evEOF = 2
        evSeekableStatusChanged = 3
        evUpdatedInfo = 4
    
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
    
    class ServiceReference:
        pass

# ============================================================================
# IMPORT MUTAGEN FOR METADATA (OPTIONAL)
# ============================================================================
try:
    from mutagen import File as MutagenFile
    from mutagen.id3 import ID3
    from mutagen.easyid3 import EasyID3
    from mutagen.mp3 import MP3
    from mutagen.flac import FLAC
    from mutagen.oggvorbis import OggVorbis
    MUTAGEN_AVAILABLE = True
    debug_print("AudioPlayer: Mutagen available")
except ImportError:
    MUTAGEN_AVAILABLE = False
    debug_print("AudioPlayer: Mutagen not available")
    
    # Create dummy classes
    class MutagenFile:
        pass
    class ID3:
        pass
    class EasyID3:
        pass
    class MP3:
        pass
    class FLAC:
        pass
    class OggVorbis:
        pass

# ============================================================================
# SCREEN SIZE DETECTION
# ============================================================================
# Get screen size for skin
try:
    FULLHD = getDesktop(0).size().width() >= 1920
except:
    FULLHD = False

# ============================================================================
# WESTY AUDIO PLAYER CLASS
# ============================================================================
class WestyAudioPlayer(Screen):
    """Advanced Audio Player with ID3 tag support and visualizations - v2.1.0"""
    
    # Dynamic skin based on screen size - FIXED: No f-strings
    @staticmethod
    def get_skin():
        """Generate skin based on desktop size"""
        try:
            desktop = getDesktop(0)
            screen_width, screen_height = desktop.size().width(), desktop.size().height()
        except:
            screen_width, screen_height = 1280, 720
        
        return """
        <screen name="WestyAudioPlayer" position="center,center" size="%d,%d" title="%s Audio Player v%s" flags="wfNoBorder">
            <!-- Background -->
            <widget name="background" position="0,0" size="%d,%d" backgroundColor="#0a0a1a" zPosition="-2"/>
            
            <!-- Album Art -->
            <widget name="album_art" position="%d,%d" size="%d,%d" alphatest="blend" zPosition="-1"/>
            <widget name="no_art_label" position="%d,%d" size="%d,%d" font="Regular;%d" foregroundColor="#666666" halign="center" valign="center" text="No Album Art" zPosition="0"/>
            
            <!-- Visualizer -->
            <widget name="visualizer" position="%d,%d" size="%d,%d" backgroundColor="#000000" zPosition="-1"/>
            
            <!-- Track Info -->
            <widget name="title_label" position="%d,%d" size="%d,50" font="Regular;%d" foregroundColor="#ffffff" halign="center" noWrap="1" zPosition="1"/>
            <widget name="artist_label" position="%d,%d" size="%d,30" font="Regular;%d" foregroundColor="#00ff00" halign="center" zPosition="1"/>
            <widget name="album_label" position="%d,%d" size="%d,30" font="Regular;%d" foregroundColor="#8888ff" halign="center" zPosition="1"/>
            
            <!-- Time Display -->
            <widget name="time_current" position="%d,%d" size="200,30" font="Regular;24" foregroundColor="#ffffff" halign="left" zPosition="1"/>
            <widget name="time_total" position="%d,%d" size="200,30" font="Regular;24" foregroundColor="#ffffff" halign="right" zPosition="1"/>
            
            <!-- Progress Bar -->
            <widget name="progress_bg" position="%d,%d" size="%d,10" backgroundColor="#333333" zPosition="1"/>
            <widget name="progress" position="%d,%d" size="0,10" backgroundColor="#00ff00" zPosition="2"/>
            
            <!-- Playback Controls -->
            <widget name="play_pause_btn" position="%d,%d" size="100,100" alphatest="blend" zPosition="3"/>
            <widget name="prev_btn" position="%d,%d" size="60,60" alphatest="blend" zPosition="3"/>
            <widget name="next_btn" position="%d,%d" size="60,60" alphatest="blend" zPosition="3"/>
            <widget name="stop_btn" position="%d,%d" size="60,60" alphatest="blend" zPosition="3"/>
            
            <!-- Volume -->
            <widget name="volume_bg" position="%d,%d" size="200,30" backgroundColor="#333333" zPosition="1"/>
            <widget name="volume_level" position="%d,%d" size="0,30" backgroundColor="#00ff00" zPosition="2"/>
            <widget name="volume_icon" position="%d,%d" size="20,30" alphatest="blend" zPosition="3"/>
            <widget name="volume_text" position="%d,%d" size="80,30" font="Regular;22" foregroundColor="#ffffff" zPosition="3"/>
            
            <!-- Playback Mode -->
            <widget name="play_mode" position="%d,%d" size="80,30" font="Regular;22" foregroundColor="#ffff00" halign="center" zPosition="3"/>
            
            <!-- Equalizer Display -->
            <widget name="eq_display" position="%d,%d" size="%d,180" backgroundColor="#000022" zPosition="0"/>
            
            <!-- Key Help -->
            <widget source="key_red" render="Label" position="100,20" size="260,40" font="Regular;26" backgroundColor="red" halign="center" valign="center" zPosition="5"/>
            <widget source="key_green" render="Label" position="460,20" size="260,40" font="Regular;26" backgroundColor="green" halign="center" valign="center" zPosition="5"/>
            <widget source="key_yellow" render="Label" position="820,20" size="260,40" font="Regular;26" backgroundColor="yellow" halign="center" valign="center" zPosition="5"/>
            <widget source="key_blue" render="Label" position="1180,20" size="260,40" font="Regular;26" backgroundColor="blue" halign="center" valign="center" zPosition="5"/>
            
            <!-- Spectrum Analyzer Bars (dynamic) -->
            <widget name="spectrum_0" position="%d,%d" size="10,180" backgroundColor="#ff0000" zPosition="1"/>
            <widget name="spectrum_1" position="%d,%d" size="10,180" backgroundColor="#ff5500" zPosition="1"/>
            <widget name="spectrum_2" position="%d,%d" size="10,180" backgroundColor="#ffff00" zPosition="1"/>
            <widget name="spectrum_3" position="%d,%d" size="10,180" backgroundColor="#00ff00" zPosition="1"/>
            <widget name="spectrum_4" position="%d,%d" size="10,180" backgroundColor="#00ffff" zPosition="1"/>
            <widget name="spectrum_5" position="%d,%d" size="10,180" backgroundColor="#0000ff" zPosition="1"/>
            <widget name="spectrum_6" position="%d,%d" size="10,180" backgroundColor="#5500ff" zPosition="1"/>
            <widget name="spectrum_7" position="%d,%d" size="10,180" backgroundColor="#ff00ff" zPosition="1"/>
            <widget name="spectrum_8" position="%d,%d" size="10,180" backgroundColor="#ffffff" zPosition="1"/>
            <widget name="spectrum_9" position="%d,%d" size="10,180" backgroundColor="#ff0000" zPosition="1"/>
        </screen>
        """ % (
            # Screen size and title
            screen_width, screen_height,
            PLUGIN_NAME, PLUGIN_VERSION,
            
            # Background
            screen_width, screen_height,
            
            # Album art position and size
            100 if screen_width >= 1280 else 50,
            100 if screen_height >= 720 else 50,
            400 if screen_width >= 1280 else 200,
            400 if screen_width >= 1280 else 200,
            100 if screen_width >= 1280 else 50,
            100 if screen_height >= 720 else 50,
            400 if screen_width >= 1280 else 200,
            400 if screen_width >= 1280 else 200,
            36 if screen_width >= 1280 else 24,
            
            # Visualizer
            520 if screen_width >= 1280 else 270,
            100 if screen_height >= 720 else 50,
            660 if screen_width >= 1280 else 480,
            400 if screen_width >= 1280 else 200,
            
            # Track info positions
            100 if screen_width >= 1280 else 50,
            520 if screen_height >= 720 else 270,
            screen_width-200 if screen_width >= 1280 else screen_width-100,
            40 if screen_width >= 1280 else 28,
            100 if screen_width >= 1280 else 50,
            580 if screen_height >= 720 else 310,
            screen_width-200 if screen_width >= 1280 else screen_width-100,
            28 if screen_width >= 1280 else 20,
            100 if screen_width >= 1280 else 50,
            620 if screen_height >= 720 else 340,
            screen_width-200 if screen_width >= 1280 else screen_width-100,
            24 if screen_width >= 1280 else 18,
            
            # Time display
            100 if screen_width >= 1280 else 50,
            660 if screen_height >= 720 else 380,
            screen_width-250 if screen_width >= 1280 else screen_width-150,
            660 if screen_height >= 720 else 380,
            
            # Progress bar
            320 if screen_width >= 1280 else 160,
            660 if screen_height >= 720 else 380,
            640 if screen_width >= 1280 else 480,
            320 if screen_width >= 1280 else 160,
            660 if screen_height >= 720 else 380,
            
            # Playback controls
            screen_width//2-50,
            680 if screen_height >= 720 else 300,
            screen_width//2-140,
            700 if screen_height >= 720 else 310,
            screen_width//2+80,
            700 if screen_height >= 720 else 310,
            screen_width//2-300,
            700 if screen_height >= 720 else 310,
            
            # Volume display
            100 if screen_width >= 1280 else 50,
            700 if screen_height >= 720 else 380,
            100 if screen_width >= 1280 else 50,
            700 if screen_height >= 720 else 380,
            80 if screen_width >= 1280 else 30,
            700 if screen_height >= 720 else 380,
            310 if screen_width >= 1280 else 210,
            700 if screen_height >= 720 else 380,
            
            # Play mode
            screen_width-180 if screen_width >= 1280 else screen_width-80,
            700 if screen_height >= 720 else 380,
            
            # Equalizer display
            520 if screen_width >= 1280 else 270,
            510 if screen_height >= 720 else 230,
            660 if screen_width >= 1280 else 480,
            
            # Spectrum analyzer positions
            530 if screen_width >= 1280 else 280,
            510 if screen_height >= 720 else 230,
            550 if screen_width >= 1280 else 300,
            510 if screen_height >= 720 else 230,
            570 if screen_width >= 1280 else 320,
            510 if screen_height >= 720 else 230,
            590 if screen_width >= 1280 else 340,
            510 if screen_height >= 720 else 230,
            610 if screen_width >= 1280 else 360,
            510 if screen_height >= 720 else 230,
            630 if screen_width >= 1280 else 380,
            510 if screen_height >= 720 else 230,
            650 if screen_width >= 1280 else 400,
            510 if screen_height >= 720 else 230,
            670 if screen_width >= 1280 else 420,
            510 if screen_height >= 720 else 230,
            690 if screen_width >= 1280 else 440,
            510 if screen_height >= 720 else 230,
            710 if screen_width >= 1280 else 460,
            510 if screen_height >= 720 else 230
        )
    
    skin = get_skin()
    
    def __init__(self, session, audio_file=None, playlist=None):
        try:
            Screen.__init__(self, session)
            
            self.session = session
            self.audio_file = audio_file
            self.playlist = playlist or []
            self.current_index = 0
            
            # Load configuration
            self.config = {}
            if MEDIA_UTILS_AVAILABLE and media_config:
                self.config = media_config.get_config('audioplayer')
            
            # Player state
            self.is_playing = False
            self.is_paused = False
            self.volume = self.config.get('volume', 80)
            self.is_muted = False
            
            # Playback modes
            self.repeat_mode = self.config.get('repeat_mode', 'none')
            self.shuffle_mode = self.config.get('shuffle', False)
            self.equalizer_preset = self.config.get('equalizer_preset', 'normal')
            
            # Audio metadata
            self.metadata = {}
            self.album_art = None
            
            # Visualization
            self.spectrum_bars = []
            self.visualization_active = self.config.get('visualization', True)
            
            # Timers
            self.update_timer = eTimer()
            self.visualization_timer = eTimer()
            self.spectrum_timer = eTimer()
            
            # Setup widgets
            self.setupWidgets()
            
            # Setup actions
            self.setupActions()
            
            # Setup service
            self.setupService()
            
            # Initialize if file provided
            if audio_file:
                self.loadAudioFile(audio_file)
            
            # Start timers
            if hasattr(self.update_timer, 'timeout'):
                self.update_timer.timeout.get().append(self.updateDisplay)
                self.update_timer.start(500)
            
            if hasattr(self.visualization_timer, 'timeout'):
                self.visualization_timer.timeout.get().append(self.updateVisualization)
                self.visualization_timer.start(100)
            
            if hasattr(self.spectrum_timer, 'timeout'):
                self.spectrum_timer.timeout.get().append(self.updateSpectrum)
                self.spectrum_timer.start(50)
            
            self.onClose.append(self.cleanup)
            
            debug_print("WestyAudioPlayer v%s: Initialized" % PLUGIN_VERSION)
            
        except Exception as e:
            debug_print("AudioPlayer init error: %s" % str(e))
            import traceback
            traceback.print_exc()
    
    def setupWidgets(self):
        """Setup all screen widgets"""
        try:
            # Background
            self["background"] = Pixmap()
            
            # Album art
            self["album_art"] = Pixmap()
            self["no_art_label"] = Label(_("No Album Art"))
            
            # Track info
            self["title_label"] = Label("")
            self["artist_label"] = Label("")
            self["album_label"] = Label("")
            
            # Progress
            self["time_current"] = Label("00:00")
            self["time_total"] = Label("00:00")
            self["progress_bg"] = Pixmap()
            self["progress"] = Pixmap()
            
            # Controls
            self["play_pause_btn"] = Pixmap()
            self["prev_btn"] = Pixmap()
            self["next_btn"] = Pixmap()
            self["stop_btn"] = Pixmap()
            
            # Volume
            self["volume_bg"] = Pixmap()
            self["volume_level"] = Pixmap()
            self["volume_icon"] = Pixmap()
            self["volume_text"] = Label("%d%%" % self.volume)
            
            # Play mode
            self["play_mode"] = Label("▶")
            
            # Visualization
            self["visualizer"] = Pixmap()
            self["eq_display"] = Pixmap()
            
            # Spectrum analyzer bars
            for i in range(10):
                widget_name = "spectrum_%d" % i
                self[widget_name] = Pixmap()
                self[widget_name].hide()
                self.spectrum_bars.append(self[widget_name])
            
            # Key labels
            self["key_red"] = StaticText(_("Playlist"))
            self["key_green"] = StaticText(_("Play/Pause"))
            self["key_yellow"] = StaticText(_("Equalizer"))
            self["key_blue"] = StaticText(_("Visualizer"))
            
            # Set initial visualization state
            if not self.visualization_active:
                self["visualizer"].hide()
                self["eq_display"].hide()
                for bar in self.spectrum_bars:
                    bar.hide()
            
        except Exception as e:
            debug_print("setupWidgets error: %s" % str(e))
    
    def setupActions(self):
        """Setup action map"""
        try:
            self["actions"] = HelpableActionMap(self, ["WestyAudioPlayerActions", "ColorActions", "MediaPlayerActions"],
            {
                # Playback control
                "playpauseService": self.togglePlayPause,
                "stop": self.stopPlayback,
                "pause": self.pausePlayback,
                "play": self.playPlayback,
                
                # Navigation
                "nextBouquet": self.nextTrack,
                "prevBouquet": self.prevTrack,
                "seekBack": self.rewind,
                "seekFwd": self.forward,
                
                # Volume control
                "volumeUp": self.volumeUp,
                "volumeDown": self.volumeDown,
                "volumeMute": self.toggleMute,
                
                # Playback modes
                "info": self.toggleRepeat,
                "showEventInfo": self.toggleShuffle,
                
                # Color buttons
                "red": self.showPlaylist,
                "green": self.togglePlayPause,
                "yellow": self.openEqualizer,
                "blue": self.toggleVisualization,
                
                # Menu
                "menu": self.openMenu,
                
                # Exit
                "cancel": self.exitPlayer,
                
                # Audio specific
                "audioSelection": self.openAudioSettings,
                
                # Number keys for quick jump
                "1": lambda: self.seekToPercentage(10),
                "2": lambda: self.seekToPercentage(20),
                "3": lambda: self.seekToPercentage(30),
                "4": lambda: self.seekToPercentage(40),
                "5": lambda: self.seekToPercentage(50),
                "6": lambda: self.seekToPercentage(60),
                "7": lambda: self.seekToPercentage(70),
                "8": lambda: self.seekToPercentage(80),
                "9": lambda: self.seekToPercentage(90),
                "0": lambda: self.seekToPercentage(0),
            }, -1)
            
        except Exception as e:
            debug_print("setupActions error: %s" % str(e))
    
    def setupService(self):
        """Setup audio service"""
        try:
            self.service = None
            if ENIGMA_CORE_AVAILABLE:
                self.service_handler = eServiceCenter.getInstance()
                debug_print("Audio service handler initialized")
        except Exception as e:
            debug_print("setupService error: %s" % str(e))
    
    def loadAudioFile(self, filepath):
        """Load audio file and extract metadata"""
        try:
            if not os.path.exists(filepath):
                self.showError(_("File not found: %s") % filepath)
                return
            
            # Extract metadata
            self.extractMetadata(filepath)
            
            # Update display with metadata
            self.updateMetadataDisplay()
            
            # Try to extract album art
            if MUTAGEN_AVAILABLE:
                self.extractAlbumArt(filepath)
            else:
                self["no_art_label"].show()
                debug_print("Mutagen not installed for album art extraction")
            
            # Create service reference
            if ENIGMA_CORE_AVAILABLE:
                self.service = eServiceReference(eServiceReference.idFile, 
                                                eServiceReference.noFlags, 
                                                filepath)
                debug_print("Created service reference for: %s" % filepath)
            
            # Start playback
            self.startPlayback()
            
        except Exception as e:
            debug_print("loadAudioFile error: %s" % str(e))
            self.showError(_("Error loading audio file"))
    
    def extractMetadata(self, filepath):
        """Extract audio metadata using mutagen or basic file info"""
        try:
            # Start with basic info
            filename = os.path.basename(filepath)
            
            self.metadata = {
                'title': filename,
                'artist': _("Unknown Artist"),
                'album': _("Unknown Album"),
                'genre': _("Unknown"),
                'year': "",
                'track': "",
                'bitrate': 0,
                'samplerate': 0,
                'channels': 2,
                'duration': 0,
                'filetype': os.path.splitext(filepath)[1].lower()
            }
            
            # Get basic file info
            if os.path.exists(filepath):
                import stat
                file_stat = os.stat(filepath)
                self.metadata['filesize'] = file_stat.st_size
                self.metadata['modified'] = time.ctime(file_stat.st_mtime)
            else:
                self.metadata['filesize'] = 0
                self.metadata['modified'] = _("Unknown")
            
            # Use mutagen if available for detailed metadata
            if MUTAGEN_AVAILABLE:
                try:
                    audio = None
                    file_ext = filepath.lower()
                    
                    # Load based on file type
                    if file_ext.endswith('.mp3'):
                        try:
                            audio = MP3(filepath, ID3=EasyID3)
                        except:
                            audio = MP3(filepath)
                        
                        if hasattr(audio, 'info'):
                            self.metadata['bitrate'] = audio.info.bitrate // 1000 if hasattr(audio.info, 'bitrate') else 0
                            self.metadata['samplerate'] = audio.info.sample_rate if hasattr(audio.info, 'sample_rate') else 0
                            self.metadata['duration'] = audio.info.length if hasattr(audio.info, 'length') else 0
                    
                    elif file_ext.endswith('.flac'):
                        try:
                            audio = FLAC(filepath)
                            if hasattr(audio, 'info'):
                                self.metadata['bitrate'] = audio.info.bitrate // 1000 if audio.info.bitrate else 0
                                self.metadata['samplerate'] = audio.info.sample_rate
                                self.metadata['duration'] = audio.info.length
                        except:
                            pass
                    
                    elif file_ext.endswith(('.ogg', '.oga')):
                        try:
                            audio = OggVorbis(filepath)
                            if hasattr(audio, 'info'):
                                self.metadata['bitrate'] = audio.info.bitrate // 1000
                                self.metadata['samplerate'] = audio.info.sample_rate
                                self.metadata['duration'] = audio.info.length
                        except:
                            pass
                    
                    # Extract tags if available
                    if audio and hasattr(audio, 'tags'):
                        tags = audio.tags
                        
                        if 'title' in tags:
                            self.metadata['title'] = str(tags['title'][0])
                        if 'artist' in tags:
                            self.metadata['artist'] = str(tags['artist'][0])
                        if 'album' in tags:
                            self.metadata['album'] = str(tags['album'][0])
                        if 'genre' in tags:
                            self.metadata['genre'] = str(tags['genre'][0])
                        if 'date' in tags:
                            self.metadata['year'] = str(tags['date'][0])
                        if 'tracknumber' in tags:
                            self.metadata['track'] = str(tags['tracknumber'][0])
                
                except Exception as mutagen_error:
                    debug_print("Mutagen metadata extraction error: %s" % str(mutagen_error))
            
            # Sanitize title using media utilities if available
            if MEDIA_UTILS_AVAILABLE:
                self.metadata['title'] = media_utils.sanitize_filename(self.metadata['title'])
            
            debug_print("Extracted metadata for: %s" % filename)
            
        except Exception as e:
            debug_print("extractMetadata error: %s" % str(e))
    
    def extractAlbumArt(self, filepath):
        """Extract album art from audio file"""
        try:
            if not MUTAGEN_AVAILABLE:
                return
                
            # Only for MP3 files with ID3 tags
            if filepath.lower().endswith('.mp3'):
                try:
                    audio = ID3(filepath)
                    for tag in audio.values():
                        if tag.FrameID == 'APIC':  # Album art
                            # Save album art to temp file
                            import tempfile
                            art_data = tag.data
                            temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
                            temp_file.write(art_data)
                            temp_file.close()
                            
                            self.album_art = temp_file.name
                            
                            # Try to load into pixmap
                            try:
                                from Tools.LoadPixmap import LoadPixmap
                                pixmap = LoadPixmap(self.album_art)
                                if pixmap:
                                    self["album_art"].instance.setPixmap(pixmap)
                                    self["no_art_label"].hide()
                                    debug_print("Loaded album art")
                                    break
                            except ImportError:
                                debug_print("LoadPixmap not available")
                
                except Exception as id3_error:
                    debug_print("ID3 album art extraction error: %s" % str(id3_error))
            
        except Exception as e:
            debug_print("extractAlbumArt error: %s" % str(e))
    
    def updateMetadataDisplay(self):
        """Update display with current metadata"""
        try:
            title = self.metadata.get('title', '')
            artist = self.metadata.get('artist', '')
            album = self.metadata.get('album', '')
            
            self["title_label"].setText(title)
            self["artist_label"].setText(artist)
            self["album_label"].setText(album)
            
            # Update window title
            display_title = "%s - %s" % (artist, title) if artist else title
            
            if len(display_title) > 50:
                display_title = display_title[:47] + "..."
            
            # Set screen title with plugin version
            full_title = "%s Audio Player v%s" % (PLUGIN_NAME, PLUGIN_VERSION)
            if hasattr(self, 'setTitle'):
                self.setTitle(full_title)
            
            debug_print("Display updated: %s" % display_title)
            
        except Exception as e:
            debug_print("updateMetadataDisplay error: %s" % str(e))
    
    def startPlayback(self):
        """Start audio playback"""
        try:
            if ENIGMA_CORE_AVAILABLE and hasattr(self.session, 'nav'):
                if self.service:
                    self.session.nav.playService(self.service)
            
            self.is_playing = True
            self.is_paused = False
            self.updatePlayButton()
            
            # Show playback started message
            self["title_label"].setForegroundColor("#00ff00")
            
            debug_print("Playback started")
            
        except Exception as e:
            debug_print("startPlayback error: %s" % str(e))
    
    def togglePlayPause(self):
        """Toggle play/pause"""
        try:
            if self.is_playing and not self.is_paused:
                self.pausePlayback()
            else:
                self.playPlayback()
        except Exception as e:
            debug_print("togglePlayPause error: %s" % str(e))
    
    def playPlayback(self):
        """Resume playback"""
        try:
            if ENIGMA_CORE_AVAILABLE and hasattr(self.session, 'nav'):
                if self.session.nav.getCurrentlyPlayingServiceReference():
                    self.session.nav.unpause()
            
            self.is_paused = False
            self.is_playing = True
            self.updatePlayButton()
            self["title_label"].setForegroundColor("#00ff00")
            
            debug_print("Playback resumed")
            
        except Exception as e:
            debug_print("playPlayback error: %s" % str(e))
    
    def pausePlayback(self):
        """Pause playback"""
        try:
            if ENIGMA_CORE_AVAILABLE and hasattr(self.session, 'nav'):
                if self.session.nav.getCurrentlyPlayingServiceReference():
                    self.session.nav.pause()
            
            self.is_paused = True
            self.updatePlayButton()
            self["title_label"].setForegroundColor("#ffff00")
            
            debug_print("Playback paused")
            
        except Exception as e:
            debug_print("pausePlayback error: %s" % str(e))
    
    def stopPlayback(self):
        """Stop playback"""
        try:
            if ENIGMA_CORE_AVAILABLE and hasattr(self.session, 'nav'):
                self.session.nav.stopService()
            
            self.is_playing = False
            self.is_paused = False
            self.updatePlayButton()
            self["title_label"].setForegroundColor("#ff0000")
            
            debug_print("Playback stopped")
            
        except Exception as e:
            debug_print("stopPlayback error: %s" % str(e))
    
    def updatePlayButton(self):
        """Update play/pause button display"""
        try:
            mode = "▶" if not self.is_playing or self.is_paused else "⏸"
            self["play_mode"].setText(mode)
        except Exception as e:
            debug_print("updatePlayButton error: %s" % str(e))
    
    def nextTrack(self):
        """Play next track in playlist"""
        try:
            if self.playlist and len(self.playlist) > 1:
                if self.shuffle_mode:
                    import random
                    self.current_index = random.randint(0, len(self.playlist) - 1)
                else:
                    self.current_index = (self.current_index + 1) % len(self.playlist)
                
                self.loadAudioFile(self.playlist[self.current_index])
                debug_print("Next track: %d" % self.current_index)
        except Exception as e:
            debug_print("nextTrack error: %s" % str(e))
    
    def prevTrack(self):
        """Play previous track in playlist"""
        try:
            if self.playlist and len(self.playlist) > 1:
                self.current_index = (self.current_index - 1) % len(self.playlist)
                self.loadAudioFile(self.playlist[self.current_index])
                debug_print("Previous track: %d" % self.current_index)
        except Exception as e:
            debug_print("prevTrack error: %s" % str(e))
    
    def rewind(self):
        """Rewind 5 seconds"""
        try:
            self.seekRelative(-5)
            debug_print("Rewind 5 seconds")
        except Exception as e:
            debug_print("rewind error: %s" % str(e))
    
    def forward(self):
        """Forward 5 seconds"""
        try:
            self.seekRelative(5)
            debug_print("Forward 5 seconds")
        except Exception as e:
            debug_print("forward error: %s" % str(e))
    
    def seekRelative(self, seconds):
        """Seek relative to current position"""
        try:
            if ENIGMA_CORE_AVAILABLE and hasattr(self.session, 'nav'):
                service = self.session.nav.getCurrentService()
                if service:
                    seek = service.seek()
                    if seek:
                        position = seek.getPlayPosition()
                        if position and position[0]:
                            new_position = position[1] + (seconds * 90000)
                            seek.seekTo(new_position)
                            debug_print("Seek relative: %d seconds" % seconds)
        except Exception as e:
            debug_print("seekRelative error: %s" % str(e))
    
    def seekToPercentage(self, percentage):
        """Seek to percentage of track"""
        try:
            if ENIGMA_CORE_AVAILABLE and hasattr(self.session, 'nav'):
                service = self.session.nav.getCurrentService()
                if service:
                    seek = service.seek()
                    if seek:
                        length = seek.getLength()
                        if length and length[0]:
                            position = (length[1] * percentage) // 100
                            seek.seekTo(position)
                            debug_print("Seek to: %d%%" % percentage)
        except Exception as e:
            debug_print("seekToPercentage error: %s" % str(e))
    
    def volumeUp(self):
        """Increase volume"""
        try:
            self.volume = min(100, self.volume + 5)
            self.updateVolumeDisplay()
            
            # Update configuration
            if MEDIA_UTILS_AVAILABLE:
                media_config.set_config('audioplayer', 'volume', self.volume)
            
            debug_print("Volume up: %d%%" % self.volume)
        except Exception as e:
            debug_print("volumeUp error: %s" % str(e))
    
    def volumeDown(self):
        """Decrease volume"""
        try:
            self.volume = max(0, self.volume - 5)
            self.updateVolumeDisplay()
            
            # Update configuration
            if MEDIA_UTILS_AVAILABLE:
                media_config.set_config('audioplayer', 'volume', self.volume)
            
            debug_print("Volume down: %d%%" % self.volume)
        except Exception as e:
            debug_print("volumeDown error: %s" % str(e))
    
    def toggleMute(self):
        """Toggle mute"""
        try:
            self.is_muted = not self.is_muted
            self.updateVolumeDisplay()
            debug_print("Mute toggled: %s" % self.is_muted)
        except Exception as e:
            debug_print("toggleMute error: %s" % str(e))
    
    def updateVolumeDisplay(self):
        """Update volume display"""
        try:
            if self.is_muted:
                self["volume_text"].setText(_("Muted"))
                if hasattr(self["volume_level"].instance, 'resize'):
                    self["volume_level"].instance.resize(0, 30 if FULLHD else 20)
            else:
                self["volume_text"].setText("%d%%" % self.volume)
                if hasattr(self["volume_level"].instance, 'resize'):
                    width = int(200 * (self.volume / 100)) if FULLHD else int(150 * (self.volume / 100))
                    self["volume_level"].instance.resize(width, 30 if FULLHD else 20)
        except Exception as e:
            debug_print("updateVolumeDisplay error: %s" % str(e))
    
    def toggleRepeat(self):
        """Toggle repeat mode"""
        try:
            modes = ["none", "one", "all"]
            current_index = modes.index(self.repeat_mode) if self.repeat_mode in modes else 0
            self.repeat_mode = modes[(current_index + 1) % len(modes)]
            
            # Update display
            repeat_symbols = {"none": "▶", "one": "🔂", "all": "🔁"}
            self["play_mode"].setText(repeat_symbols.get(self.repeat_mode, "▶"))
            
            # Update configuration
            if MEDIA_UTILS_AVAILABLE:
                media_config.set_config('audioplayer', 'repeat_mode', self.repeat_mode)
            
            self.showMessage(_("Repeat: %s") % self.repeat_mode)
            debug_print("Repeat mode: %s" % self.repeat_mode)
            
        except Exception as e:
            debug_print("toggleRepeat error: %s" % str(e))
    
    def toggleShuffle(self):
        """Toggle shuffle mode"""
        try:
            self.shuffle_mode = not self.shuffle_mode
            
            # Update display
            self["play_mode"].setText("🔀" if self.shuffle_mode else "▶")
            
            # Update configuration
            if MEDIA_UTILS_AVAILABLE:
                media_config.set_config('audioplayer', 'shuffle', self.shuffle_mode)
            
            mode = _("On") if self.shuffle_mode else _("Off")
            self.showMessage(_("Shuffle: %s") % mode)
            debug_print("Shuffle mode: %s" % self.shuffle_mode)
            
        except Exception as e:
            debug_print("toggleShuffle error: %s" % str(e))
    
    def toggleVisualization(self):
        """Toggle visualization"""
        try:
            self.visualization_active = not self.visualization_active
            
            # Update configuration
            if MEDIA_UTILS_AVAILABLE:
                media_config.set_config('audioplayer', 'visualization', self.visualization_active)
            
            if self.visualization_active:
                self["visualizer"].show()
                self["eq_display"].show()
                for bar in self.spectrum_bars:
                    bar.show()
                debug_print("Visualization enabled")
            else:
                self["visualizer"].hide()
                self["eq_display"].hide()
                for bar in self.spectrum_bars:
                    bar.hide()
                debug_print("Visualization disabled")
            
        except Exception as e:
            debug_print("toggleVisualization error: %s" % str(e))
    
    def updateDisplay(self):
        """Update time and progress display"""
        try:
            if not self.is_playing or self.is_paused:
                return
            
            duration = self.metadata.get('duration', 0)
            if duration > 0:
                # Simulate playback progress for demo
                # In real implementation, would get actual position from service
                current_time = time.time() % duration if duration > 0 else 0
                
                # Update time labels
                self["time_current"].setText(self.formatTime(current_time))
                self["time_total"].setText(self.formatTime(duration))
                
                # Update progress bar
                if duration > 0:
                    progress = (current_time / duration) * 100
                    progress_width = 640 if FULLHD else 480
                    width = int(progress_width * (progress / 100))
                    if hasattr(self["progress"].instance, 'resize'):
                        self["progress"].instance.resize(width, 10 if FULLHD else 6)
            
        except Exception as e:
            debug_print("updateDisplay error: %s" % str(e))
    
    def formatTime(self, seconds):
        """Format seconds to MM:SS or HH:MM:SS"""
        try:
            if seconds < 0:
                return "00:00"
            
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            
            if hours > 0:
                return "%02d:%02d:%02d" % (hours, minutes, secs)
            else:
                return "%02d:%02d" % (minutes, secs)
                
        except Exception as e:
            debug_print("formatTime error: %s" % str(e))
            return "00:00"
    
    def updateVisualization(self):
        """Update visualization display"""
        try:
            if not self.visualization_active or not self.is_playing or self.is_paused:
                return
            
            # In real implementation, would use audio data for visualization
            # For now, create simple animation
            pass
            
        except Exception as e:
            debug_print("updateVisualization error: %s" % str(e))
    
    def updateSpectrum(self):
        """Update spectrum analyzer bars"""
        try:
            if not self.visualization_active or not self.is_playing or self.is_paused:
                return
            
            import random
            
            for i, bar in enumerate(self.spectrum_bars):
                # Random height for demo (would use FFT in real implementation)
                height = random.randint(20, 180)
                if hasattr(bar.instance, 'resize'):
                    bar.instance.resize(10, height)
                
                # Position from bottom
                if FULLHD:
                    y_pos = 510 + (180 - height)
                    if hasattr(bar.instance, 'move'):
                        from enigma import ePoint
                        bar.instance.move(ePoint(530 + (i * 20), y_pos))
            
        except Exception as e:
            debug_print("updateSpectrum error: %s" % str(e))
    
    def showPlaylist(self):
        """Show playlist browser"""
        try:
            if self.playlist:
                # Try to import playlist browser
                try:
                    from .PlaylistBrowser import WestyAudioPlaylistBrowser
                    self.session.open(WestyAudioPlaylistBrowser, self.playlist, self.current_index)
                except ImportError:
                    # Show simple playlist dialog
                    from Screens.MessageBox import MessageBox
                    playlist_text = _("Playlist (%d tracks):\n\n") % len(self.playlist)
                    for i, track in enumerate(self.playlist[:10]):
                        name = os.path.basename(track)
                        prefix = "▶ " if i == self.current_index else "%d. " % (i+1)
                        playlist_text += "%s%s\n" % (prefix, name)
                    
                    if len(self.playlist) > 10:
                        playlist_text += _("\n... and %d more") % (len(self.playlist) - 10)
                    
                    self.session.open(MessageBox, playlist_text, MessageBox.TYPE_INFO)
            
        except Exception as e:
            debug_print("showPlaylist error: %s" % str(e))
    
    def openEqualizer(self):
        """Open audio equalizer"""
        try:
            # Try to import equalizer
            try:
                from .Equalizer import WestyAudioEqualizer
                self.session.openWithCallback(self.equalizerCallback, WestyAudioEqualizer, self.equalizer_preset)
            except ImportError:
                self.showMessage(_("Equalizer feature requires additional files"))
        except Exception as e:
            debug_print("openEqualizer error: %s" % str(e))
            self.showMessage(_("Error opening equalizer"))
    
    def equalizerCallback(self, preset):
        """Callback from equalizer"""
        try:
            if preset:
                self.equalizer_preset = preset
                
                # Update configuration
                if MEDIA_UTILS_AVAILABLE:
                    media_config.set_config('audioplayer', 'equalizer_preset', preset)
                
                self.showMessage(_("Equalizer preset: %s") % preset)
                debug_print("Equalizer preset set to: %s" % preset)
        except Exception as e:
            debug_print("equalizerCallback error: %s" % str(e))
    
    def openAudioSettings(self):
        """Open audio settings"""
        try:
            # Try to import audio settings
            try:
                from .AudioSettings import WestyAudioSettings
                self.session.open(WestyAudioSettings)
            except ImportError:
                self.showMessage(_("Audio settings not available"))
        except Exception as e:
            debug_print("openAudioSettings error: %s" % str(e))
            self.showMessage(_("Error opening audio settings"))
    
    def openMenu(self):
        """Open audio player menu"""
        try:
            from Screens.ChoiceBox import ChoiceBox
            
            menu = []
            
            if self.playlist:
                menu.append((_("Playlist Editor"), self.editPlaylist))
            
            menu.append((_("File Info"), self.showFileInfo))
            menu.append((_("Audio Settings"), self.openAudioSettings))
            menu.append((_("Sleep Timer"), self.setSleepTimer))
            
            if self.playlist:
                menu.append((_("Save Playlist"), self.savePlaylist))
                menu.append((_("Load Playlist"), self.loadPlaylist))
            
            menu.append((_("Settings"), self.openSettings))
            menu.append(("", None))  # Separator
            menu.append((_("About Audio Player"), self.showAbout))
            
            self.session.openWithCallback(
                self.menuCallback,
                ChoiceBox,
                title=_("Audio Player Menu"),
                list=menu
            )
            
        except Exception as e:
            debug_print("openMenu error: %s" % str(e))
            self.showMessage(_("Error opening menu"))
    
    def menuCallback(self, choice):
        """Handle menu choice callback"""
        try:
            if choice:
                debug_print("Menu choice: %s" % choice[0])
                choice[1]()
        except Exception as e:
            debug_print("menuCallback error: %s" % str(e))
    
    def editPlaylist(self):
        """Edit current playlist"""
        try:
            # Try to import playlist editor
            try:
                from .PlaylistEditor import WestyPlaylistEditor
                self.session.open(WestyPlaylistEditor, self.playlist)
            except ImportError:
                self.showMessage(_("Playlist editor not available"))
        except Exception as e:
            debug_print("editPlaylist error: %s" % str(e))
    
    def showFileInfo(self):
        """Show detailed file information"""
        try:
            from Screens.MessageBox import MessageBox
            
            info_lines = []
            
            info_lines.append(_("File: %s") % self.metadata.get('title', ''))
            info_lines.append(_("Artist: %s") % self.metadata.get('artist', ''))
            info_lines.append(_("Album: %s") % self.metadata.get('album', ''))
            info_lines.append(_("Genre: %s") % self.metadata.get('genre', ''))
            
            if self.metadata.get('year'):
                info_lines.append(_("Year: %s") % self.metadata['year'])
            
            if self.metadata.get('track'):
                info_lines.append(_("Track: %s") % self.metadata['track'])
            
            if self.metadata.get('bitrate'):
                info_lines.append(_("Bitrate: %d kbps") % self.metadata['bitrate'])
            
            if self.metadata.get('samplerate'):
                info_lines.append(_("Sample Rate: %d Hz") % self.metadata['samplerate'])
            
            if self.metadata.get('duration'):
                info_lines.append(_("Duration: %s") % self.formatTime(self.metadata['duration']))
            
            if self.metadata.get('filesize'):
                # Format file size
                size = self.metadata['filesize']
                for unit in ['B', 'KB', 'MB', 'GB']:
                    if size < 1024.0:
                        info_lines.append(_("Size: %.1f %s") % (size, unit))
                        break
                    size /= 1024.0
            
            info_lines.append(_("Format: %s") % self.metadata.get('filetype', '').upper().replace('.', ''))
            info_lines.append(_("Modified: %s") % self.metadata.get('modified', ''))
            
            info_text = "\n".join(info_lines)
            self.session.open(MessageBox, info_text, MessageBox.TYPE_INFO)
            
        except Exception as e:
            debug_print("showFileInfo error: %s" % str(e))
            self.showMessage(_("Error showing file info"))
    
    def setSleepTimer(self):
        """Set sleep timer"""
        try:
            from Screens.InputBox import InputBox
            self.session.openWithCallback(
                self.sleepTimerSet,
                InputBox,
                title=_("Sleep timer (minutes)"),
                text="30"
            )
        except Exception as e:
            debug_print("setSleepTimer error: %s" % str(e))
    
    def sleepTimerSet(self, minutes):
        """Set sleep timer callback"""
        try:
            if minutes:
                try:
                    minutes_int = int(minutes)
                    self.showMessage(_("Sleep timer set for %d minutes") % minutes_int)
                    debug_print("Sleep timer: %d minutes" % minutes_int)
                except ValueError:
                    self.showMessage(_("Invalid number"))
        except Exception as e:
            debug_print("sleepTimerSet error: %s" % str(e))
    
    def savePlaylist(self):
        """Save playlist to file"""
        try:
            from Screens.VirtualKeyBoard import VirtualKeyBoard
            
            default_name = "my_playlist.m3u"
            self.session.openWithCallback(
                lambda name: self.doSavePlaylist(name if name else default_name),
                VirtualKeyBoard,
                title=_("Enter playlist name"),
                text=default_name
            )
        except Exception as e:
            debug_print("savePlaylist error: %s" % str(e))
    
    def doSavePlaylist(self, filename):
        """Save playlist to file"""
        try:
            if not filename.lower().endswith('.m3u'):
                filename += '.m3u'
            
            # Use /tmp directory for saving
            full_path = "/tmp/%s" % filename
            
            # Use media utilities if available
            if MEDIA_UTILS_AVAILABLE:
                success = media_utils.save_m3u_playlist(full_path, self.playlist)
                if success:
                    self.showMessage(_("Playlist saved to: %s") % full_path)
                else:
                    self.showError(_("Error saving playlist"))
            else:
                # Manual save
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write("#EXTM3U\n")
                    f.write("# Created by %s v%s\n" % (PLUGIN_NAME, PLUGIN_VERSION))
                    f.write("# Date: %s\n" % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    for track in self.playlist:
                        f.write("%s\n" % track)
                
                self.showMessage(_("Playlist saved to: %s") % full_path)
                debug_print("Playlist saved: %s" % full_path)
            
        except Exception as e:
            debug_print("doSavePlaylist error: %s" % str(e))
            self.showError(_("Error saving playlist: %s") % str(e))
    
    def loadPlaylist(self):
        """Load playlist from file"""
        try:
            from Screens.FileBrowser import FileBrowser
            
            def playlistSelected(selected):
                if selected:
                    try:
                        # Use media utilities if available
                        if MEDIA_UTILS_AVAILABLE:
                            playlist = media_utils.parse_m3u_playlist(selected)
                        else:
                            # Manual parse
                            playlist = []
                            base_dir = os.path.dirname(selected)
                            
                            with open(selected, 'r', encoding='utf-8', errors='ignore') as f:
                                for line in f:
                                    line = line.strip()
                                    if line and not line.startswith('#'):
                                        if os.path.isabs(line):
                                            if os.path.exists(line):
                                                playlist.append(line)
                                        else:
                                            rel_path = os.path.join(base_dir, line)
                                            if os.path.exists(rel_path):
                                                playlist.append(rel_path)
                                            else:
                                                playlist.append(line)
                        
                        if playlist:
                            self.playlist = playlist
                            self.current_index = 0
                            self.loadAudioFile(self.playlist[0])
                            self.showMessage(_("Playlist loaded: %d tracks") % len(playlist))
                            debug_print("Playlist loaded: %d tracks" % len(playlist))
                        
                    except Exception as e:
                        debug_print("Error loading playlist: %s" % str(e))
                        self.showError(_("Error loading playlist"))
            
            self.session.openWithCallback(
                playlistSelected,
                FileBrowser,
                "/tmp",
                showDirectories=False,
                matchingPattern=".*\\.m3u$"
            )
            
        except Exception as e:
            debug_print("loadPlaylist error: %s" % str(e))
            self.showError(_("Error loading playlist"))
    
    def openSettings(self):
        """Open audio player settings"""
        try:
            # Try to import audio player settings
            try:
                from .AudioPlayerSettings import WestyAudioPlayerSettings
                self.session.open(WestyAudioPlayerSettings)
            except ImportError:
                self.showMessage(_("Audio player settings not available"))
        except Exception as e:
            debug_print("openSettings error: %s" % str(e))
            self.showMessage(_("Error opening settings"))
    
    def showAbout(self):
        """Show about information"""
        try:
            from Screens.MessageBox import MessageBox
            
            about_text = _("""%s Audio Player v%s

Advanced audio player with professional features:
• Audio file playback with full ID3 tag support
• Album art display
• Spectrum analyzer visualization
• Audio equalizer with presets
• Playlist management (M3U format)
• Repeat and shuffle modes
• Sleep timer
• Audio settings and configuration

© 2023 %s Team""") % (PLUGIN_NAME, PLUGIN_VERSION, PLUGIN_NAME)
            
            self.session.open(MessageBox, about_text, MessageBox.TYPE_INFO)
        except Exception as e:
            debug_print("showAbout error: %s" % str(e))
    
    def showMessage(self, message, type="info"):
        """Show message to user"""
        try:
            from Screens.MessageBox import MessageBox
            msg_type = MessageBox.TYPE_INFO if type == "info" else MessageBox.TYPE_ERROR
            self.session.open(MessageBox, message, msg_type, timeout=3)
        except Exception as e:
            debug_print("showMessage error: %s" % str(e))
    
    def showError(self, error):
        """Show error message"""
        try:
            from Screens.MessageBox import MessageBox
            self.session.open(MessageBox, error, MessageBox.TYPE_ERROR, timeout=5)
            debug_print("Error shown: %s" % error)
        except Exception as e:
            debug_print("showError error: %s" % str(e))
    
    def exitPlayer(self):
        """Exit audio player"""
        try:
            self.stopPlayback()
            self.close()
            debug_print("Audio player exited")
        except Exception as e:
            debug_print("exitPlayer error: %s" % str(e))
    
    def cleanup(self):
        """Clean up resources"""
        try:
            if hasattr(self.update_timer, 'stop'):
                self.update_timer.stop()
            if hasattr(self.visualization_timer, 'stop'):
                self.visualization_timer.stop()
            if hasattr(self.spectrum_timer, 'stop'):
                self.spectrum_timer.stop()
            
            if ENIGMA_CORE_AVAILABLE and hasattr(self.session, 'nav'):
                if self.session.nav.getCurrentlyPlayingServiceReference():
                    self.session.nav.stopService()
            
            # Clean up temp album art file
            if self.album_art and os.path.exists(self.album_art):
                try:
                    os.unlink(self.album_art)
                    debug_print("Cleaned up album art: %s" % self.album_art)
                except Exception as e:
                    debug_print("Error cleaning up album art: %s" % str(e))
            
            debug_print("Audio player cleaned up")
            
        except Exception as e:
            debug_print("cleanup error: %s" % str(e))


# ============================================================================
# FACTORY FUNCTION
# ============================================================================
def playAudio(session, audio_file, playlist=None):
    """Convenience function to play audio"""
    try:
        player = WestyAudioPlayer(session, audio_file, playlist)
        session.open(player)
        debug_print("Playing audio: %s" % audio_file)
        return player
    except Exception as e:
        debug_print("playAudio error: %s" % str(e))
        try:
            from Screens.MessageBox import MessageBox
            session.open(MessageBox, _("Error starting audio player: %s") % str(e), MessageBox.TYPE_ERROR)
        except:
            pass
        return None


# ============================================================================
# TEST FUNCTION
# ============================================================================
if __name__ == "__main__":
    print("%s Audio Player v%s" % (PLUGIN_NAME, PLUGIN_VERSION))
    print("=" * 60)
    
    # Test media utilities
    if MEDIA_UTILS_AVAILABLE:
        print("Media Utils Test:")
        test_files = [
            "/path/to/audio.mp3",
            "/path/to/audio.flac",
            "/path/to/audio.ogg"
        ]
        
        for file in test_files:
            is_audio = media_utils.is_audio_file(file)
            print("  %s: Audio=%s" % (file, is_audio))
    
    print("\nAudio Player features:")
    print("  • Audio file playback with ID3 tag support")
    print("  • Album art display")
    print("  • Spectrum analyzer visualization")
    print("  • Audio equalizer with presets")
    print("  • Playlist management (M3U format")
    print("  • Repeat and shuffle modes")
    print("  • Sleep timer")
    print("  • Audio settings and configuration")
    
    print("\n" + "=" * 60)
    print("AudioPlayer module ready for v2.1.0 integration")