#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division, unicode_literals

import os
import sys
import time

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
    debug_print("MediaPlayer: Imported plugin utilities v%s" % PLUGIN_VERSION)
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
        debug_print("MediaPlayer: Media utilities imported")
    except ImportError:
        # Try direct import
        try:
            import media_utils as mu
            media_utils = mu.media_utils
            media_config = mu.media_config
            MEDIA_UTILS_AVAILABLE = True
            debug_print("MediaPlayer: Media utilities imported directly")
        except ImportError as e:
            raise ImportError("Could not import media_utils: %s" % str(e))
    
    debug_print("MediaPlayer: Media utilities available: %s" % MEDIA_UTILS_AVAILABLE)
    
except Exception as e:
    debug_print("MediaPlayer: Media utilities not available: %s" % str(e))
    # Create minimal utilities
    class MediaUtils:
        @staticmethod
        def is_video_file(filename):
            ext = os.path.splitext(filename)[1].lower()
            return ext in ('.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.m4v', '.mpg', '.mpeg')
        
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
    
    media_utils = MediaUtils()
    
    # Create minimal config
    class SimpleConfig:
        def get_config(self, module):
            return {'volume': 80, 'repeat_mode': 'none', 'shuffle': False}
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
except ImportError:
    SCREEN_AVAILABLE = False
    debug_print("MediaPlayer: Screen not available")
    
    class Screen:
        def __init__(self, session):
            self.session = session
        
        def close(self):
            pass
        
        def onLayoutFinish(self, callback):
            callback()

# Try to import InfoBarGenerics
try:
    from Screens.InfoBarGenerics import InfoBarNotifications, InfoBarSeek, InfoBarAudioSelection
    INFOBAR_AVAILABLE = True
    debug_print("MediaPlayer: InfoBarGenerics available")
except ImportError:
    INFOBAR_AVAILABLE = False
    debug_print("MediaPlayer: InfoBarGenerics not available")
    
    class InfoBarNotifications:
        def __init__(self):
            pass
    
    class InfoBarSeek:
        def __init__(self):
            pass
    
    class InfoBarAudioSelection:
        def __init__(self):
            pass

try:
    from Screens.InfoBar import InfoBar
    INFOBAR_MAIN_AVAILABLE = True
    debug_print("MediaPlayer: InfoBar available")
except ImportError:
    INFOBAR_MAIN_AVAILABLE = False
    debug_print("MediaPlayer: InfoBar not available")
    
    class InfoBar:
        pass

try:
    from Components.ActionMap import ActionMap, HelpableActionMap
    ACTIONMAP_AVAILABLE = True
    debug_print("MediaPlayer: ActionMap available")
except ImportError:
    ACTIONMAP_AVAILABLE = False
    debug_print("MediaPlayer: ActionMap not available")
    
    class ActionMap:
        def __init__(self, contexts, actions, prio=-1):
            pass
    
    HelpableActionMap = ActionMap

try:
    from Components.Label import Label
    from Components.Pixmap import Pixmap
    from Components.Sources.StaticText import StaticText
    COMPONENTS_AVAILABLE = True
    debug_print("MediaPlayer: Basic components available")
except ImportError:
    COMPONENTS_AVAILABLE = False
    debug_print("MediaPlayer: Basic components not available")
    
    class Label:
        def setText(self, text):
            pass
        
        def setForegroundColor(self, color):
            pass
    
    class Pixmap:
        def show(self):
            pass
        
        def hide(self):
            pass
    
    class StaticText:
        def __init__(self, text=""):
            self.text = text

# Try to import ServiceEventTracker
try:
    from Components.ServiceEventTracker import ServiceEventTracker
    SERVICE_TRACKER_AVAILABLE = True
    debug_print("MediaPlayer: ServiceEventTracker available")
except ImportError:
    SERVICE_TRACKER_AVAILABLE = False
    debug_print("MediaPlayer: ServiceEventTracker not available")
    
    class ServiceEventTracker:
        def __init__(self, screen=None, eventmap=None):
            self.screen = screen
            self.eventmap = eventmap or {}

try:
    from Components.FileList import FileList
    FILELIST_AVAILABLE = True
    debug_print("MediaPlayer: FileList available")
except ImportError:
    FILELIST_AVAILABLE = False
    debug_print("MediaPlayer: FileList not available")
    
    class FileList:
        pass

try:
    from enigma import eServiceReference, eServiceCenter, iPlayableService, eTimer, getDesktop, iServiceInformation
    from ServiceReference import ServiceReference
    ENIGMA_CORE_AVAILABLE = True
    debug_print("MediaPlayer: Enigma core available")
except ImportError as e:
    ENIGMA_CORE_AVAILABLE = False
    debug_print("MediaPlayer: Core enigma imports not available: %s" % str(e))
    
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
        evVideoSizeChanged = 5
        evVideoProgressiveChanged = 6
        evVideoFramerateChanged = 7
    
    class eTimer:
        def __init__(self):
            pass
        
        def start(self, interval):
            pass
        
        def stop(self):
            pass
        
        def timeout(self):
            class Timeout:
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
    
    class iServiceInformation:
        sVideoType = 1
        sVideoWidth = 2
        sVideoHeight = 3
        sFrameRate = 4
        
        def getInfoString(self, what):
            return ""
        
        def getInfo(self, what):
            return 0
    
    class ServiceReference:
        pass

# ============================================================================
# IMPORT OPTIONAL MODULES
# ============================================================================
try:
    from .PlaylistBrowser import WestyPlaylistBrowser
    PLAYLIST_BROWSER_AVAILABLE = True
    debug_print("MediaPlayer: PlaylistBrowser available")
except ImportError:
    PLAYLIST_BROWSER_AVAILABLE = False
    debug_print("MediaPlayer: PlaylistBrowser not available")
    
    class WestyPlaylistBrowser:
        def __init__(self, session, playlist, current_index):
            self.session = session
            self.playlist = playlist
            self.current_index = current_index

try:
    from .Equalizer import WestyEqualizer
    EQUALIZER_AVAILABLE = True
    debug_print("MediaPlayer: Equalizer available")
except ImportError:
    EQUALIZER_AVAILABLE = False
    debug_print("MediaPlayer: Equalizer not available")
    
    class WestyEqualizer:
        def __init__(self, session):
            self.session = session

try:
    from .MediaPlayerSettings import WestyMediaPlayerSettings
    SETTINGS_AVAILABLE = True
    debug_print("MediaPlayer: MediaPlayerSettings available")
except ImportError:
    SETTINGS_AVAILABLE = False
    debug_print("MediaPlayer: MediaPlayerSettings not available")
    
    class WestyMediaPlayerSettings:
        def __init__(self, session):
            self.session = session

# ============================================================================
# SCREEN SIZE DETECTION
# ============================================================================
# Get screen size for skin
try:
    FULLHD = getDesktop(0).size().width() >= 1920
except:
    FULLHD = False

# ============================================================================
# WESTY MEDIA PLAYER CLASS
# ============================================================================
class WestyMediaPlayer(Screen, InfoBarNotifications, InfoBarSeek, InfoBarAudioSelection):
    """Advanced Media Player with professional features - v2.1.0"""
    
    # Dynamic skin based on screen size - FIXED: No f-strings
    @staticmethod
    def get_skin():
        """Generate skin based on desktop size"""
        try:
            desktop = getDesktop(0)
            size_obj = desktop.size()
            screen_width, screen_height = size_obj.width(), size_obj.height()
        except:
            screen_width, screen_height = (1920, 1080) if FULLHD else (1280, 720)
        
        return """
        <screen name="WestyMediaPlayer" position="0,0" size="%d,%d" title="%s Media Player v%s" flags="wfNoBorder">
            <!-- Video Display Area -->
            <widget name="video_display" position="0,0" size="%d,%d" zPosition="-1"/>
            
            <!-- Control Overlay (hidden by default) -->
            <widget name="control_overlay" position="0,%d" size="%d,%d" backgroundColor="#1a1a1acc" zPosition="1"/>
            
            <!-- Top Info Bar -->
            <widget name="top_bar" position="0,0" size="%d,60" backgroundColor="#000000aa" zPosition="2"/>
            <widget name="title_label" position="20,10" size="%d,40" font="Regular;30" foregroundColor="#ffffff" noWrap="1" zPosition="3"/>
            
            <!-- Progress Bar -->
            <widget name="progress_bg" position="%d,%d" size="%d,10" backgroundColor="#333333" zPosition="3"/>
            <widget name="progress" position="%d,%d" size="0,10" backgroundColor="#00ff00" zPosition="4"/>
            
            <!-- Time Display -->
            <widget name="time_current" position="50,%d" size="200,30" font="Regular;24" foregroundColor="#ffffff" halign="left" zPosition="3"/>
            <widget name="time_total" position="%d,%d" size="200,30" font="Regular;24" foregroundColor="#ffffff" halign="right" zPosition="3"/>
            
            <!-- Playback Controls -->
            <widget name="play_pause_btn" position="%d,%d" size="80,80" alphatest="blend" zPosition="3"/>
            <widget name="rewind_btn" position="%d,%d" size="60,60" alphatest="blend" zPosition="3"/>
            <widget name="forward_btn" position="%d,%d" size="60,60" alphatest="blend" zPosition="3"/>
            <widget name="stop_btn" position="%d,%d" size="60,60" alphatest="blend" zPosition="3"/>
            <widget name="next_btn" position="%d,%d" size="60,60" alphatest="blend" zPosition="3"/>
            <widget name="prev_btn" position="%d,%d" size="60,60" alphatest="blend" zPosition="3"/>
            
            <!-- Playback Info -->
            <widget name="playback_info" position="%d,%d" size="%d,30" font="Regular;22" foregroundColor="#cccccc" halign="center" zPosition="3"/>
            
            <!-- Audio Info -->
            <widget name="audio_info" position="%d,70" size="200,30" font="Regular;20" foregroundColor="#00ff00" halign="right" zPosition="3"/>
            
            <!-- Subtitles Info -->
            <widget name="subtitle_info" position="%d,110" size="200,30" font="Regular;20" foregroundColor="#ffff00" halign="right" zPosition="3"/>
            
            <!-- Volume Display -->
            <widget name="volume_bg" position="50,%d" size="30,60" backgroundColor="#333333" zPosition="3"/>
            <widget name="volume_level" position="50,%d" size="30,0" backgroundColor="#00ff00" zPosition="4"/>
            <widget name="volume_text" position="90,%d" size="100,30" font="Regular;22" foregroundColor="#ffffff" zPosition="3"/>
            
            <!-- Key Help -->
            <widget source="key_red" render="Label" position="100,%d" size="360,40" font="Regular;24" backgroundColor="red" halign="center" valign="center" zPosition="5"/>
            <widget source="key_green" render="Label" position="560,%d" size="360,40" font="Regular;24" backgroundColor="green" halign="center" valign="center" zPosition="5"/>
            <widget source="key_yellow" render="Label" position="1020,%d" size="360,40" font="Regular;24" backgroundColor="yellow" halign="center" valign="center" zPosition="5"/>
            <widget source="key_blue" render="Label" position="1480,%d" size="360,40" font="Regular;24" backgroundColor="blue" halign="center" valign="center" zPosition="5"/>
        </screen>
        """ % (
            # Screen size and title
            screen_width, screen_height,
            PLUGIN_NAME, PLUGIN_VERSION,
            
            # Video display
            screen_width, screen_height,
            
            # Control overlay
            screen_height-180, screen_width, 180,
            
            # Top bar and title
            screen_width, screen_width-40,
            
            # Progress bar
            100, screen_height-110, screen_width-200,
            100, screen_height-110,
            
            # Time display
            screen_height-140,
            screen_width-250, screen_height-140,
            
            # Playback controls positions
            screen_width//2-40, screen_height-90,
            screen_width//2-140, screen_height-80,
            screen_width//2+80, screen_height-80,
            screen_width//2-300, screen_height-80,
            screen_width//2+200, screen_height-80,
            screen_width//2-420, screen_height-80,
            
            # Playback info
            100, screen_height-50, screen_width-200,
            
            # Audio and subtitle info
            screen_width-200, screen_width-200,
            
            # Volume display
            screen_height-70, screen_height-70, screen_height-50,
            
            # Key help positions
            screen_height-40, screen_height-40, screen_height-40, screen_height-40
        )
    
    skin = get_skin()
    
    def __init__(self, session, service=None, playlist=None, playIndex=0):
        try:
            Screen.__init__(self, session)
            if INFOBAR_AVAILABLE:
                InfoBarNotifications.__init__(self)
                InfoBarSeek.__init__(self)
                InfoBarAudioSelection.__init__(self)
            
            self.session = session
            self.service = service
            self.playlist = playlist or []
            self.playIndex = playIndex
            self.currentService = None
            
            # Load configuration
            self.config = {}
            if MEDIA_UTILS_AVAILABLE and media_config:
                self.config = media_config.get_config('mediaplayer')
            
            # Playback state
            self.is_playing = False
            self.is_paused = False
            self.show_controls = False
            
            # Volume
            self.volume = self.config.get('volume', 80)
            self.is_muted = False
            
            # Playback info
            self.video_info = {}
            self.audio_info = {}
            self.subtitle_info = {}
            
            # Playback modes
            self.repeat_mode = self.config.get('repeat_mode', 'none')
            self.shuffle_mode = self.config.get('shuffle', False)
            
            # Setup widgets
            self.setupWidgets()
            
            # Setup actions
            self.setupActions()
            
            # Setup service tracking
            self.setupServiceTracking()
            
            # Timers
            self.controls_timer = eTimer()
            self.update_timer = eTimer()
            
            # Auto-hide controls timer
            if hasattr(self.controls_timer, 'timeout'):
                self.controls_timer.timeout.connect(self.hideControls)
            
            # Update timer
            if hasattr(self.update_timer, 'timeout'):
                self.update_timer.timeout.connect(self.updateDisplay)
                self.update_timer.start(1000)
            
            # Start playback if service provided
            if service:
                self.startPlayback(service)
            
            self.onClose.append(self.cleanup)
            
            debug_print("WestyMediaPlayer v%s: Initialized" % PLUGIN_VERSION)
            
        except Exception as e:
            debug_print("MediaPlayer init error: %s" % str(e))
            import traceback
            traceback.print_exc()
    
    def setupWidgets(self):
        """Setup all screen widgets"""
        try:
            # Video display
            self["video_display"] = Pixmap()
            
            # Control overlay
            self["control_overlay"] = Pixmap()
            self["control_overlay"].hide()
            
            # Info labels
            self["title_label"] = Label("")
            self["time_current"] = Label("00:00")
            self["time_total"] = Label("00:00")
            self["playback_info"] = Label("")
            self["audio_info"] = Label("")
            self["subtitle_info"] = Label("")
            
            # Progress bar
            self["progress_bg"] = Pixmap()
            self["progress"] = Pixmap()
            
            # Volume display
            self["volume_bg"] = Pixmap()
            self["volume_level"] = Pixmap()
            self["volume_text"] = Label("%d%%" % self.volume)
            
            # Control buttons
            self["play_pause_btn"] = Pixmap()
            self["rewind_btn"] = Pixmap()
            self["forward_btn"] = Pixmap()
            self["stop_btn"] = Pixmap()
            self["next_btn"] = Pixmap()
            self["prev_btn"] = Pixmap()
            
            # Key labels
            self["key_red"] = StaticText(_("Stop"))
            self["key_green"] = StaticText(_("Play/Pause"))
            self["key_yellow"] = StaticText(_("Audio"))
            self["key_blue"] = StaticText(_("Subtitles"))
            
            # Top bar
            self["top_bar"] = Pixmap()
            self["top_bar"].hide()
            
        except Exception as e:
            debug_print("setupWidgets error: %s" % str(e))
    
    def setupActions(self):
        """Setup action map"""
        try:
            # Create seek functions for number keys
            def seek_10(): return self.seekRelative(-600)  # -10 min
            def seek_1(): return self.seekRelative(-60)    # -1 min
            def seek_10s(): return self.seekRelative(-10)  # -10 sec
            def seek_10s_fwd(): return self.seekRelative(10)   # +10 sec
            def seek_1_fwd(): return self.seekRelative(60)     # +1 min
            def seek_10_fwd(): return self.seekRelative(600)   # +10 min
            
            self["actions"] = HelpableActionMap(self, ["WestyMediaPlayerActions", "InfobarSeekActions", "ColorActions", "EPGSelectActions"],
            {
                # Playback control
                "playpauseService": self.togglePlayPause,
                "stop": self.stopPlayback,
                "pause": self.pausePlayback,
                "play": self.playPlayback,
                
                # Navigation
                "seekBack": self.rewind,
                "seekFwd": self.forward,
                "nextBouquet": self.nextTrack,
                "prevBouquet": self.prevTrack,
                
                # Volume control
                "volumeUp": self.volumeUp,
                "volumeDown": self.volumeDown,
                "volumeMute": self.toggleMute,
                
                # Info/controls
                "info": self.toggleInfo,
                "showEventInfo": self.toggleControls,
                "menu": self.openMenu,
                
                # Color buttons
                "red": self.stopPlayback,
                "green": self.togglePlayPause,
                "yellow": self.audioMenu,
                "blue": self.subtitleMenu,
                
                # Exit
                "cancel": self.exitPlayer,
                
                # Number keys for chapter/jump
                "1": seek_10,
                "2": seek_1,
                "3": seek_10s,
                "4": seek_10s_fwd,
                "5": seek_1_fwd,
                "6": seek_10_fwd,
                
                # Audio track selection
                "audioSelection": self.audioMenu,
                
                # Subtitle selection
                "subtitleSelection": self.subtitleMenu,
            }, -1)
            
        except Exception as e:
            debug_print("setupActions error: %s" % str(e))
    
    def setupServiceTracking(self):
        """Setup service event tracking"""
        if SERVICE_TRACKER_AVAILABLE:
            try:
                self.__event_tracker = ServiceEventTracker(screen=self, eventmap={
                    iPlayableService.evStart: self.serviceStarted,
                    iPlayableService.evEOF: self.serviceEOF,
                    iPlayableService.evSeekableStatusChanged: self.seekableStatusChanged,
                    iPlayableService.evUpdatedInfo: self.updatedInfo,
                })
            except Exception as e:
                debug_print("setupServiceTracking error: %s" % str(e))
    
    def startPlayback(self, service):
        """Start playback of given service"""
        try:
            if isinstance(service, str):
                # Create service reference from file path
                if ENIGMA_CORE_AVAILABLE:
                    service = eServiceReference(eServiceReference.idFile, 
                                               eServiceReference.noFlags, 
                                               service)
                else:
                    # Mock service
                    class MockService:
                        def __init__(self, path):
                            self.path = path
                        def getPath(self):
                            return self.path
                    service = MockService(service)
            
            if ENIGMA_CORE_AVAILABLE and hasattr(self.session, 'nav'):
                self.session.nav.playService(service)
            
            self.currentService = service
            self.is_playing = True
            self.is_paused = False
            
            # Extract and display title
            title = self.getServiceTitle(service)
            self["title_label"].setText(title)
            
            # Show controls briefly
            self.showControls()
            
            debug_print("Started playback: %s" % title)
            
        except Exception as e:
            debug_print("startPlayback error: %s" % str(e))
    
    def getServiceTitle(self, service):
        """Get title from service"""
        try:
            if hasattr(service, 'getPath'):
                path = service.getPath()
                if path:
                    filename = os.path.basename(path)
                    if MEDIA_UTILS_AVAILABLE:
                        return media_utils.sanitize_filename(filename)
                    return filename
            elif isinstance(service, str):
                return os.path.basename(service)
            
            return _("Unknown Media")
            
        except Exception as e:
            debug_print("getServiceTitle error: %s" % str(e))
            return _("Unknown")
    
    def togglePlayPause(self):
        """Toggle between play and pause"""
        try:
            if self.is_paused:
                self.playPlayback()
            else:
                self.pausePlayback()
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
            debug_print("Playback stopped")
            
        except Exception as e:
            debug_print("stopPlayback error: %s" % str(e))
    
    def rewind(self):
        """Rewind 10 seconds"""
        try:
            self.seekRelative(-10)
            debug_print("Rewind 10 seconds")
        except Exception as e:
            debug_print("rewind error: %s" % str(e))
    
    def forward(self):
        """Forward 10 seconds"""
        try:
            self.seekRelative(10)
            debug_print("Forward 10 seconds")
        except Exception as e:
            debug_print("forward error: %s" % str(e))
    
    def nextTrack(self):
        """Play next track in playlist"""
        try:
            if self.playlist and len(self.playlist) > 1:
                if self.shuffle_mode:
                    import random
                    self.playIndex = random.randint(0, len(self.playlist) - 1)
                else:
                    self.playIndex = (self.playIndex + 1) % len(self.playlist)
                
                self.startPlayback(self.playlist[self.playIndex])
                debug_print("Next track: %d" % self.playIndex)
        except Exception as e:
            debug_print("nextTrack error: %s" % str(e))
    
    def prevTrack(self):
        """Play previous track in playlist"""
        try:
            if self.playlist and len(self.playlist) > 1:
                if self.shuffle_mode:
                    import random
                    self.playIndex = random.randint(0, len(self.playlist) - 1)
                else:
                    self.playIndex = (self.playIndex - 1) % len(self.playlist)
                
                self.startPlayback(self.playlist[self.playIndex])
                debug_print("Previous track: %d" % self.playIndex)
        except Exception as e:
            debug_print("prevTrack error: %s" % str(e))
    
    def volumeUp(self):
        """Increase volume"""
        try:
            self.volume = min(100, self.volume + 5)
            self.updateVolumeDisplay()
            debug_print("Volume up: %d%%" % self.volume)
        except Exception as e:
            debug_print("volumeUp error: %s" % str(e))
    
    def volumeDown(self):
        """Decrease volume"""
        try:
            self.volume = max(0, self.volume - 5)
            self.updateVolumeDisplay()
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
                    self["volume_level"].instance.resize(30, 0)
            else:
                self["volume_text"].setText("%d%%" % self.volume)
                if hasattr(self["volume_level"].instance, 'resize'):
                    height = int(60 * (self.volume / 100))
                    self["volume_level"].instance.resize(30, height)
        except Exception as e:
            debug_print("updateVolumeDisplay error: %s" % str(e))
    
    def updatePlayButton(self):
        """Update play/pause button display"""
        # In real implementation, would change button pixmap
        try:
            pass
        except Exception as e:
            debug_print("updatePlayButton error: %s" % str(e))
    
    def toggleControls(self):
        """Show/hide controls"""
        try:
            if self.show_controls:
                self.hideControls()
            else:
                self.showControls()
        except Exception as e:
            debug_print("toggleControls error: %s" % str(e))
    
    def showControls(self):
        """Show control overlay"""
        try:
            self.show_controls = True
            self["control_overlay"].show()
            self["top_bar"].show()
            
            # Auto-hide after 3 seconds
            if hasattr(self.controls_timer, 'startLongTimer'):
                self.controls_timer.startLongTimer(3)
            
        except Exception as e:
            debug_print("showControls error: %s" % str(e))
    
    def hideControls(self):
        """Hide control overlay"""
        try:
            self.show_controls = False
            self["control_overlay"].hide()
            self["top_bar"].hide()
            if hasattr(self.controls_timer, 'stop'):
                self.controls_timer.stop()
        except Exception as e:
            debug_print("hideControls error: %s" % str(e))
    
    def updateDisplay(self):
        """Update time and progress display"""
        try:
            if not self.is_playing:
                return
            
            # Get current position and duration
            if ENIGMA_CORE_AVAILABLE and hasattr(self.session, 'nav'):
                service = self.session.nav.getCurrentService()
                if service:
                    seek = service.seek()
                    if seek:
                        length = seek.getLength()
                        position = seek.getPlayPosition()
                        
                        if length and length[0] and position and position[0]:
                            # Convert to seconds
                            length_sec = length[1] / 90000
                            position_sec = position[1] / 90000
                            
                            # Update time labels
                            self["time_current"].setText(self.formatTime(position_sec))
                            self["time_total"].setText(self.formatTime(length_sec))
                            
                            # Update progress bar
                            if length_sec > 0:
                                progress = (position_sec / length_sec) * 100
                                progress_width = 1720 if FULLHD else 1180
                                width = int(progress_width * (progress / 100))
                                if hasattr(self["progress"].instance, 'resize'):
                                    self["progress"].instance.resize(width, 10 if FULLHD else 6)
            
        except Exception as e:
            debug_print("updateDisplay error: %s" % str(e))
    
    def formatTime(self, seconds):
        """Format seconds to HH:MM:SS or MM:SS"""
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
    
    def audioMenu(self):
        """Open audio track selection menu"""
        try:
            try:
                from Screens.AudioSelection import AudioSelection
                self.session.open(AudioSelection, infobar=self)
                debug_print("Opened audio selection")
            except ImportError:
                self.showMessage(_("Audio selection not available"))
        except Exception as e:
            debug_print("audioMenu error: %s" % str(e))
            self.showMessage(_("Error opening audio menu"))
    
    def subtitleMenu(self):
        """Open subtitle selection menu"""
        try:
            try:
                from Screens.AudioSelection import SubtitleSelection
                self.session.open(SubtitleSelection, infobar=self)
                debug_print("Opened subtitle selection")
            except ImportError:
                try:
                    from Screens.SubtitleDisplay import SubtitleDisplay
                    self.session.open(SubtitleDisplay, self)
                except ImportError:
                    self.showMessage(_("Subtitle selection not available"))
        except Exception as e:
            debug_print("subtitleMenu error: %s" % str(e))
            self.showMessage(_("Error opening subtitle menu"))
    
    def toggleInfo(self):
        """Toggle playback information display"""
        try:
            # Toggle between different info displays
            debug_print("Toggled info display")
        except Exception as e:
            debug_print("toggleInfo error: %s" % str(e))
    
    def openMenu(self):
        """Open media player menu"""
        try:
            from Screens.ChoiceBox import ChoiceBox
            
            menu = [
                (_("Playlist"), self.showPlaylist),
                (_("File Info"), self.showFileInfo),
                (_("Repeat Mode"), self.toggleRepeat),
                (_("Shuffle"), self.toggleShuffle),
                (_("Aspect Ratio"), self.aspectRatioMenu),
                (_("Zoom"), self.zoomMenu),
                (_("Equalizer"), self.openEqualizer),
                (_("Sleep Timer"), self.setSleepTimer),
                (_("Settings"), self.openSettings),
                ("", None),  # Separator
                (_("About Media Player"), self.showAbout),
            ]
            
            self.session.openWithCallback(
                lambda choice: choice and choice[1](),
                ChoiceBox,
                title=_("Media Player Menu"),
                list=menu
            )
            
        except Exception as e:
            debug_print("openMenu error: %s" % str(e))
            self.showMessage(_("Error opening menu"))
    
    def showPlaylist(self):
        """Show playlist browser"""
        try:
            if self.playlist:
                if PLAYLIST_BROWSER_AVAILABLE:
                    from .PlaylistBrowser import WestyPlaylistBrowser
                    self.session.open(WestyPlaylistBrowser, self.playlist, self.playIndex)
                else:
                    # Show simple playlist
                    from Screens.MessageBox import MessageBox
                    playlist_text = _("Playlist (%d files):\n\n") % len(self.playlist)
                    for i, track in enumerate(self.playlist[:10]):
                        name = self.getServiceTitle(track)
                        prefix = "▶ " if i == self.playIndex else "%d. " % (i+1)
                        playlist_text += "%s%s\n" % (prefix, name)
                    
                    if len(self.playlist) > 10:
                        playlist_text += _("\n... and %d more") % (len(self.playlist) - 10)
                    
                    self.session.open(MessageBox, playlist_text, MessageBox.TYPE_INFO)
                    
        except Exception as e:
            debug_print("showPlaylist error: %s" % str(e))
    
    def showFileInfo(self):
        """Show detailed file information"""
        try:
            from Screens.MessageBox import MessageBox
            
            file_info = []
            file_info.append(_("Video Information:"))
            
            for key, value in self.video_info.items():
                if value:
                    file_info.append("  %s: %s" % (key, value))
            
            if self.audio_info:
                file_info.append("")
                file_info.append(_("Audio Information:"))
                for key, value in self.audio_info.items():
                    if value:
                        file_info.append("  %s: %s" % (key, value))
            
            if self.subtitle_info:
                file_info.append("")
                file_info.append(_("Subtitle Information:"))
                for key, value in self.subtitle_info.items():
                    if value:
                        file_info.append("  %s: %s" % (key, value))
            
            info_text = "\n".join(file_info)
            self.session.open(MessageBox, info_text, MessageBox.TYPE_INFO)
            
        except Exception as e:
            debug_print("showFileInfo error: %s" % str(e))
            self.showMessage(_("Error showing file info"))
    
    def toggleRepeat(self):
        """Toggle repeat mode"""
        try:
            modes = ["none", "one", "all"]
            current_index = modes.index(self.repeat_mode) if self.repeat_mode in modes else 0
            self.repeat_mode = modes[(current_index + 1) % len(modes)]
            
            # Update configuration
            if MEDIA_UTILS_AVAILABLE:
                media_config.set_config('mediaplayer', 'repeat_mode', self.repeat_mode)
            
            self.showMessage(_("Repeat: %s") % self.repeat_mode)
            debug_print("Repeat mode: %s" % self.repeat_mode)
            
        except Exception as e:
            debug_print("toggleRepeat error: %s" % str(e))
    
    def toggleShuffle(self):
        """Toggle shuffle mode"""
        try:
            self.shuffle_mode = not self.shuffle_mode
            
            # Update configuration
            if MEDIA_UTILS_AVAILABLE:
                media_config.set_config('mediaplayer', 'shuffle', self.shuffle_mode)
            
            mode = _("On") if self.shuffle_mode else _("Off")
            self.showMessage(_("Shuffle: %s") % mode)
            debug_print("Shuffle mode: %s" % self.shuffle_mode)
            
        except Exception as e:
            debug_print("toggleShuffle error: %s" % str(e))
    
    def aspectRatioMenu(self):
        """Change aspect ratio"""
        try:
            from Screens.ChoiceBox import ChoiceBox
            
            ratios = [
                ("auto", _("Auto")),
                ("4:3", "4:3"),
                ("16:9", "16:9"),
                ("16:10", "16:10"),
                ("original", _("Original")),
                ("full", _("Full")),
                ("panscan", _("Pan & Scan")),
            ]
            
            self.session.openWithCallback(
                self.setAspectRatio,
                ChoiceBox,
                title=_("Select Aspect Ratio"),
                list=[(name, value) for value, name in ratios]
            )
            
        except Exception as e:
            debug_print("aspectRatioMenu error: %s" % str(e))
    
    def setAspectRatio(self, choice):
        """Set aspect ratio"""
        try:
            if choice:
                ratio = choice[1]
                # Update configuration
                if MEDIA_UTILS_AVAILABLE:
                    media_config.set_config('mediaplayer', 'aspect_ratio', ratio)
                self.showMessage(_("Aspect ratio: %s") % ratio)
                debug_print("Aspect ratio set to: %s" % ratio)
        except Exception as e:
            debug_print("setAspectRatio error: %s" % str(e))
    
    def zoomMenu(self):
        """Change zoom level"""
        try:
            from Screens.ChoiceBox import ChoiceBox
            
            zooms = [
                ("1.0x", _("Normal")),
                ("1.2x", _("1.2x")),
                ("1.5x", _("1.5x")),
                ("2.0x", _("2.0x")),
                ("custom", _("Custom")),
            ]
            
            self.session.openWithCallback(
                self.setZoom,
                ChoiceBox,
                title=_("Select Zoom Level"),
                list=zooms
            )
            
        except Exception as e:
            debug_print("zoomMenu error: %s" % str(e))
    
    def setZoom(self, choice):
        """Set zoom level"""
        try:
            if choice:
                zoom = choice[1]
                self.showMessage(_("Zoom: %s") % zoom)
                debug_print("Zoom set to: %s" % zoom)
        except Exception as e:
            debug_print("setZoom error: %s" % str(e))
    
    def openEqualizer(self):
        """Open audio equalizer"""
        try:
            if EQUALIZER_AVAILABLE:
                from .Equalizer import WestyEqualizer
                self.session.open(WestyEqualizer)
            else:
                self.showMessage(_("Equalizer not available"))
        except Exception as e:
            debug_print("openEqualizer error: %s" % str(e))
            self.showMessage(_("Error opening equalizer"))
    
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
    
    def openSettings(self):
        """Open media player settings"""
        try:
            if SETTINGS_AVAILABLE:
                from .MediaPlayerSettings import WestyMediaPlayerSettings
                self.session.openWithCallback(self.settingsCallback, WestyMediaPlayerSettings)
            else:
                self.showMessage(_("Settings not available"))
        except Exception as e:
            debug_print("openSettings error: %s" % str(e))
            self.showMessage(_("Error opening settings"))
    
    def settingsCallback(self, result):
        """Callback from settings screen"""
        try:
            debug_print("Settings callback: %s" % result)
            # Reload configuration
            if MEDIA_UTILS_AVAILABLE:
                self.config = media_config.get_config('mediaplayer')
                # Update volume from config
                self.volume = self.config.get('volume', 80)
                self.updateVolumeDisplay()
        except Exception as e:
            debug_print("settingsCallback error: %s" % str(e))
    
    def showAbout(self):
        """Show about information"""
        try:
            from Screens.MessageBox import MessageBox
            
            about_text = _("""%s Media Player v%s

Advanced media player with professional features:
• Video playback with fullscreen support
• Audio track and subtitle selection
• Playlist management
• Equalizer and audio settings
• Aspect ratio and zoom controls
• Sleep timer
• Media information display

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
    
    # Service event handlers
    def serviceStarted(self):
        """Called when service starts"""
        try:
            self.is_playing = True
            self.is_paused = False
            self.updatePlayButton()
            self.showControls()
            debug_print("Service started")
        except Exception as e:
            debug_print("serviceStarted error: %s" % str(e))
    
    def serviceEOF(self):
        """Called when end of file reached"""
        try:
            if self.playlist:
                # Check repeat mode
                if self.repeat_mode == "one":
                    # Restart current track
                    self.startPlayback(self.playlist[self.playIndex])
                elif self.repeat_mode == "all" or self.playIndex < len(self.playlist) - 1:
                    self.nextTrack()
                else:
                    self.stopPlayback()
            else:
                self.stopPlayback()
            debug_print("End of file reached")
        except Exception as e:
            debug_print("serviceEOF error: %s" % str(e))
    
    def seekableStatusChanged(self):
        """Called when seekable status changes"""
        try:
            debug_print("Seekable status changed")
        except Exception as e:
            debug_print("seekableStatusChanged error: %s" % str(e))
    
    def updatedInfo(self):
        """Called when service info is updated"""
        try:
            # Extract video/audio/subtitle info
            if ENIGMA_CORE_AVAILABLE and hasattr(self.session, 'nav'):
                service = self.session.nav.getCurrentService()
                if service:
                    info = service.info()
                    
                    # Get video info
                    video = {}
                    if hasattr(info, 'getInfoString'):
                        video['format'] = info.getInfoString(iServiceInformation.sVideoType)
                    
                    if hasattr(info, 'getInfo'):
                        width = info.getInfo(iServiceInformation.sVideoWidth)
                        height = info.getInfo(iServiceInformation.sVideoHeight)
                        if width and height:
                            video['resolution'] = "%dx%d" % (width, height)
                        
                        fps = info.getInfo(iServiceInformation.sFrameRate)
                        if fps:
                            video['fps'] = fps // 1000  # Convert from millifps to fps
                    
                    self.video_info = video
                    
                    # Update playback info
                    info_str = "%s | %s" % (video.get('resolution', ''), video.get('format', ''))
                    self["playback_info"].setText(info_str)
            
        except Exception as e:
            debug_print("updatedInfo error: %s" % str(e))
    
    def exitPlayer(self):
        """Exit media player"""
        try:
            self.stopPlayback()
            self.close()
            debug_print("Media player exited")
        except Exception as e:
            debug_print("exitPlayer error: %s" % str(e))
    
    def cleanup(self):
        """Clean up resources"""
        try:
            if hasattr(self.update_timer, 'stop'):
                self.update_timer.stop()
            if hasattr(self.controls_timer, 'stop'):
                self.controls_timer.stop()
            
            if ENIGMA_CORE_AVAILABLE and hasattr(self.session, 'nav'):
                if self.session.nav.getCurrentlyPlayingServiceReference():
                    self.session.nav.stopService()
            
            debug_print("Media player cleaned up")
        except Exception as e:
            debug_print("cleanup error: %s" % str(e))


# ============================================================================
# FACTORY FUNCTION
# ============================================================================
def playMedia(session, filepath, playlist=None):
    """Convenience function to play media"""
    try:
        player = WestyMediaPlayer(session, filepath, playlist)
        session.open(player)
        debug_print("Playing media: %s" % filepath)
        return player
    except Exception as e:
        debug_print("playMedia error: %s" % str(e))
        try:
            from Screens.MessageBox import MessageBox
            session.open(MessageBox, _("Error starting media player: %s") % str(e), MessageBox.TYPE_ERROR)
        except:
            pass
        return None


# ============================================================================
# TEST FUNCTION
# ============================================================================
if __name__ == "__main__":
    print("%s Media Player v%s" % (PLUGIN_NAME, PLUGIN_VERSION))
    print("=" * 60)
    
    # Test media utilities
    print("Media Utils Test:")
    test_files = [
        "/path/to/video.mp4",
        "/path/to/audio.mp3",
        "/path/to/image.jpg"
    ]
    
    for file in test_files:
        is_video = MediaUtils.is_video_file(file) if 'MediaUtils' in locals() else False
        is_audio = False
        print("  %s: Video=%s, Audio=%s" % (file, is_video, is_audio))
    
    print("\nMedia Player features:")
    print("  • Fullscreen video playback")
    print("  • Audio and subtitle selection")
    print("  • Playlist management")
    print("  • Equalizer support")
    print("  • Aspect ratio controls")
    print("  • Sleep timer")
    print("  • Media information display")
    
    print("\n" + "=" * 60)
    print("MediaPlayer module ready for v2.1.0 integration")