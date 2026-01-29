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
    debug_print(f"PlaylistBrowser: Imported plugin utilities v{PLUGIN_VERSION}")
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
    from .media_utils import media_utils
    MEDIA_UTILS_AVAILABLE = True
    debug_print("PlaylistBrowser: Media utilities available")
except ImportError:
    MEDIA_UTILS_AVAILABLE = False
    debug_print("PlaylistBrowser: Media utilities not available")

# Try to import Screens with fallbacks
try:
    from Screens.Screen import Screen
    SCREEN_AVAILABLE = True
    debug_print("PlaylistBrowser: Screen available")
except ImportError:
    SCREEN_AVAILABLE = False
    debug_print("PlaylistBrowser: Screen not available")
    
    class Screen:
        def __init__(self, session):
            self.session = session
        
        def close(self):
            pass

try:
    from Components.ActionMap import ActionMap
    ACTIONMAP_AVAILABLE = True
    debug_print("PlaylistBrowser: ActionMap available")
except ImportError:
    ACTIONMAP_AVAILABLE = False
    debug_print("PlaylistBrowser: ActionMap not available")
    
    class ActionMap:
        def __init__(self, contexts, actions, prio=-1):
            pass

try:
    from Components.Label import Label
    from Components.Sources.StaticText import StaticText
    from Components.MenuList import MenuList
    COMPONENTS_AVAILABLE = True
    debug_print("PlaylistBrowser: Basic components available")
except ImportError:
    COMPONENTS_AVAILABLE = False
    debug_print("PlaylistBrowser: Basic components not available")
    
    class Label:
        def setText(self, text):
            pass
    
    class StaticText:
        def __init__(self, text=""):
            self.text = text
    
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

class WestyAudioPlaylistBrowser(Screen):
    """Playlist browser for audio player - v2.1.0"""
    
    skin = """
        <screen name="WestyAudioPlaylistBrowser" position="center,center" size="800,600" title="{plugin_name} Audio Playlist v{version}">
            <widget name="playlist" position="50,50" size="700,500" itemHeight="40" scrollbarMode="showOnDemand"/>
            <widget source="key_red" render="Label" position="50,560" size="200,30" font="Regular;22" backgroundColor="red" halign="center"/>
            <widget source="key_green" render="Label" position="300,560" size="200,30" font="Regular;22" backgroundColor="green" halign="center"/>
            <widget source="key_yellow" render="Label" position="550,560" size="200,30" font="Regular;22" backgroundColor="yellow" halign="center"/>
        </screen>
    """.format(plugin_name=PLUGIN_NAME, version=PLUGIN_VERSION)
    
    def __init__(self, session, playlist, current_index):
        try:
            Screen.__init__(self, session)
            self.session = session
            self.playlist = playlist
            self.current_index = current_index
            
            # Create menu items
            playlist_items = []
            for i, filepath in enumerate(playlist):
                filename = os.path.basename(filepath)
                # Use media utilities for sanitization if available
                if MEDIA_UTILS_AVAILABLE:
                    display_name = media_utils.sanitize_filename(filename)
                else:
                    display_name = filename
                
                prefix = "▶ " if i == current_index else f"{i+1:02d}. "
                playlist_items.append((prefix + display_name, filepath))
            
            self["playlist"] = MenuList(playlist_items)
            
            self["key_red"] = StaticText(_("Close"))
            self["key_green"] = StaticText(_("Play"))
            self["key_yellow"] = StaticText(_("Remove"))
            
            self["actions"] = ActionMap(["ColorActions"],
            {
                "cancel": self.close,
                "red": self.close,
                "green": self.playSelected,
                "yellow": self.removeSelected,
                "ok": self.playSelected,
            }, -1)
            
            debug_print(f"AudioPlaylistBrowser v{PLUGIN_VERSION}: Initialized with {len(playlist)} tracks")
            
        except Exception as e:
            debug_print(f"AudioPlaylistBrowser init error: {e}")
            import traceback
            traceback.print_exc()
    
    def playSelected(self):
        """Play selected track"""
        try:
            selection = self["playlist"].getCurrent()
            if selection:
                index = self["playlist"].getSelectionIndex()
                debug_print(f"Playing track {index}")
                self.close(index)
        except Exception as e:
            debug_print(f"playSelected error: {e}")
            self.close(None)
    
    def removeSelected(self):
        """Remove selected track from playlist"""
        try:
            index = self["playlist"].getSelectionIndex()
            if 0 <= index < len(self.playlist):
                removed = self.playlist[index]
                del self.playlist[index]
                debug_print(f"Removed track {index}: {os.path.basename(removed)}")
                self.close(-1)  # Signal to refresh
        except Exception as e:
            debug_print(f"removeSelected error: {e}")
            self.close(None)


class WestyPlaylistBrowser(Screen):
    """Playlist browser for media player - v2.1.0"""
    
    skin = """
        <screen name="WestyPlaylistBrowser" position="center,center" size="800,600" title="{plugin_name} Playlist v{version}">
            <widget name="playlist" position="50,50" size="700,500" itemHeight="40" scrollbarMode="showOnDemand"/>
            <widget source="key_red" render="Label" position="50,560" size="200,30" font="Regular;22" backgroundColor="red" halign="center"/>
            <widget source="key_green" render="Label" position="300,560" size="200,30" font="Regular;22" backgroundColor="green" halign="center"/>
            <widget source="key_yellow" render="Label" position="550,560" size="200,30" font="Regular;22" backgroundColor="yellow" halign="center"/>
        </screen>
    """.format(plugin_name=PLUGIN_NAME, version=PLUGIN_VERSION)
    
    def __init__(self, session, playlist, current_index):
        try:
            Screen.__init__(self, session)
            self.session = session
            self.playlist = playlist
            self.current_index = current_index
            
            # Try to create advanced list with MultiContent
            try:
                from Components.Sources.List import List as SourceList
                from Components.MultiContent import MultiContentEntryText
                
                playlist_items = []
                for i, item in enumerate(playlist):
                    if hasattr(item, 'getPath'):
                        name = item.getPath()
                    else:
                        name = str(item)
                    
                    filename = os.path.basename(name)
                    # Use media utilities for sanitization if available
                    if MEDIA_UTILS_AVAILABLE:
                        display_name = media_utils.sanitize_filename(filename)
                    else:
                        display_name = filename
                    
                    prefix = "▶ " if i == current_index else f"{i+1:02d}. "
                    
                    playlist_items.append((item, [
                        MultiContentEntryText(pos=(10, 10), size=(780, 30), 
                                             font=0, flags=0, text=prefix + display_name)
                    ]))
                
                self["playlist"] = SourceList(playlist_items)
                
            except ImportError:
                # Fall back to MenuList
                try:
                    playlist_items = []
                    for i, item in enumerate(playlist):
                        if hasattr(item, 'getPath'):
                            name = item.getPath()
                        else:
                            name = str(item)
                        
                        filename = os.path.basename(name)
                        # Use media utilities for sanitization if available
                        if MEDIA_UTILS_AVAILABLE:
                            display_name = media_utils.sanitize_filename(filename)
                        else:
                            display_name = filename
                        
                        prefix = "▶ " if i == current_index else f"{i+1:02d}. "
                        playlist_items.append((prefix + display_name, item))
                    
                    self["playlist"] = MenuList(playlist_items)
                    
                except ImportError:
                    # Simple list as fallback
                    self["playlist"] = MenuList([])
            
            self["key_red"] = StaticText(_("Close"))
            self["key_green"] = StaticText(_("Play"))
            self["key_yellow"] = StaticText(_("Remove"))
            
            self["actions"] = ActionMap(["ColorActions"],
            {
                "cancel": self.close,
                "red": self.close,
                "green": self.playSelected,
                "yellow": self.removeSelected,
                "ok": self.playSelected,
            }, -1)
            
            debug_print(f"PlaylistBrowser v{PLUGIN_VERSION}: Initialized with {len(playlist)} items")
            
        except Exception as e:
            debug_print(f"PlaylistBrowser init error: {e}")
            import traceback
            traceback.print_exc()
    
    def playSelected(self):
        """Play selected item"""
        try:
            selection = self["playlist"].getCurrent()
            if selection:
                # Get index from list component
                try:
                    if hasattr(self["playlist"], 'getIndex'):
                        index = self["playlist"].getIndex()
                    elif hasattr(self["playlist"], 'getSelectionIndex'):
                        index = self["playlist"].getSelectionIndex()
                    else:
                        index = 0
                    
                    debug_print(f"Playing item {index}")
                    self.close(index)
                except:
                    self.close(0)
        except Exception as e:
            debug_print(f"playSelected error: {e}")
            self.close(None)
    
    def removeSelected(self):
        """Remove selected item from playlist"""
        try:
            selection = self["playlist"].getCurrent()
            if selection:
                # Get index from list component
                try:
                    if hasattr(self["playlist"], 'getIndex'):
                        index = self["playlist"].getIndex()
                    elif hasattr(self["playlist"], 'getSelectionIndex'):
                        index = self["playlist"].getSelectionIndex()
                    else:
                        index = 0
                    
                    if 0 <= index < len(self.playlist):
                        removed = self.playlist[index]
                        del self.playlist[index]
                        debug_print(f"Removed item {index}")
                        self.close(-1)  # Signal to refresh
                except:
                    self.close(None)
        except Exception as e:
            debug_print(f"removeSelected error: {e}")
            self.close(None)


# Test function
if __name__ == "__main__":
    print(f"{PLUGIN_NAME} Playlist Browser v{PLUGIN_VERSION}")
    print("=" * 60)
    
    print("Playlist Browser Features:")
    print("  • Browse audio and video playlists")
    print("  • Visual indication of current playing track")
    print("  • Play selected track")
    print("  • Remove tracks from playlist")
    print("  • Support for large playlists")
    
    # Create test data
    test_audio_playlist = [
        "/path/to/audio1.mp3",
        "/path/to/audio2.flac",
        "/path/to/audio3.ogg"
    ]
    
    test_video_playlist = [
        "/path/to/video1.mp4",
        "/path/to/video2.avi",
        "/path/to/video3.mkv"
    ]
    
    print(f"\nAudio playlist example ({len(test_audio_playlist)} tracks):")
    for i, track in enumerate(test_audio_playlist, 1):
        print(f"  {i}. {os.path.basename(track)}")
    
    print(f"\nVideo playlist example ({len(test_video_playlist)} videos):")
    for i, video in enumerate(test_video_playlist, 1):
        print(f"  {i}. {os.path.basename(video)}")
    
    print("\n" + "=" * 60)
    print("PlaylistBrowser module ready for v2.1.0 integration")