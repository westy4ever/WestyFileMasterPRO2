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
    debug_print(f"PlaylistEditor: Imported plugin utilities v{PLUGIN_VERSION}")
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
    debug_print("PlaylistEditor: Media utilities available")
except ImportError:
    MEDIA_UTILS_AVAILABLE = False
    debug_print("PlaylistEditor: Media utilities not available")

# Try to import Screens with fallbacks
try:
    from Screens.Screen import Screen
    SCREEN_AVAILABLE = True
    debug_print("PlaylistEditor: Screen available")
except ImportError:
    SCREEN_AVAILABLE = False
    debug_print("PlaylistEditor: Screen not available")
    
    class Screen:
        def __init__(self, session):
            self.session = session
        
        def close(self):
            pass

try:
    from Components.ActionMap import ActionMap
    ACTIONMAP_AVAILABLE = True
    debug_print("PlaylistEditor: ActionMap available")
except ImportError:
    ACTIONMAP_AVAILABLE = False
    debug_print("PlaylistEditor: ActionMap not available")
    
    class ActionMap:
        def __init__(self, contexts, actions, prio=-1):
            pass

try:
    from Components.Label import Label
    from Components.Sources.StaticText import StaticText
    from Components.MenuList import MenuList
    COMPONENTS_AVAILABLE = True
    debug_print("PlaylistEditor: Basic components available")
except ImportError:
    COMPONENTS_AVAILABLE = False
    debug_print("PlaylistEditor: Basic components not available")
    
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
        
        def moveToIndex(self, index):
            if 0 <= index < len(self.list):
                self.index = index

class WestyPlaylistEditor(Screen):
    """Playlist editor for audio files - v2.1.0"""
    
    skin = """
        <screen name="WestyPlaylistEditor" position="center,center" size="800,600" title="{plugin_name} Playlist Editor v{version}">
            <widget name="playlist" position="50,50" size="700,450" itemHeight="40" scrollbarMode="showOnDemand"/>
            <widget source="key_red" render="Label" position="50,520" size="200,30" font="Regular;22" backgroundColor="red" halign="center"/>
            <widget source="key_green" render="Label" position="300,520" size="200,30" font="Regular;22" backgroundColor="green" halign="center"/>
            <widget source="key_yellow" render="Label" position="550,520" size="200,30" font="Regular;22" backgroundColor="yellow" halign="center"/>
            <widget source="key_blue" render="Label" position="50,560" size="200,30" font="Regular;22" backgroundColor="blue" halign="center"/>
        </screen>
    """.format(plugin_name=PLUGIN_NAME, version=PLUGIN_VERSION)
    
    def __init__(self, session, playlist):
        try:
            Screen.__init__(self, session)
            self.session = session
            self.playlist = playlist[:]  # Make a copy
            self.modified = False
            
            # Create menu items
            playlist_items = []
            for i, filepath in enumerate(self.playlist):
                filename = os.path.basename(filepath)
                # Use media utilities for sanitization if available
                if MEDIA_UTILS_AVAILABLE:
                    display_name = media_utils.sanitize_filename(filename)
                else:
                    display_name = filename
                
                playlist_items.append((f"{i+1:02d}. {display_name}", filepath))
            
            self["playlist"] = MenuList(playlist_items)
            
            self["key_red"] = StaticText(_("Cancel"))
            self["key_green"] = StaticText(_("Save"))
            self["key_yellow"] = StaticText(_("Remove"))
            self["key_blue"] = StaticText(_("Add"))
            
            self["actions"] = ActionMap(["ColorActions", "DirectionActions"],
            {
                "cancel": self.cancel,
                "red": self.cancel,
                "green": self.save,
                "yellow": self.removeSelected,
                "blue": self.addTrack,
                "up": self.up,
                "down": self.down,
                "menu": self.showMenu,
            }, -1)
            
            debug_print(f"PlaylistEditor v{PLUGIN_VERSION}: Initialized with {len(playlist)} tracks")
            
        except Exception as e:
            debug_print(f"PlaylistEditor init error: {e}")
            import traceback
            traceback.print_exc()
    
    def up(self):
        try:
            self["playlist"].selectPrevious()
        except Exception as e:
            debug_print(f"up error: {e}")
    
    def down(self):
        try:
            self["playlist"].selectNext()
        except Exception as e:
            debug_print(f"down error: {e}")
    
    def removeSelected(self):
        """Remove selected track from playlist"""
        try:
            index = self["playlist"].getSelectionIndex()
            if 0 <= index < len(self.playlist):
                removed = self.playlist[index]
                del self.playlist[index]
                self.modified = True
                self.updateList()
                
                debug_print(f"Removed track: {os.path.basename(removed)}")
                self.showMessage(_("Track removed"))
        except Exception as e:
            debug_print(f"removeSelected error: {e}")
    
    def addTrack(self):
        """Add track to playlist"""
        try:
            from Screens.FileBrowser import FileBrowser
            
            def trackSelected(selected):
                if selected and os.path.exists(selected):
                    # Check if it's an audio file
                    if MEDIA_UTILS_AVAILABLE:
                        is_audio = media_utils.is_audio_file(selected)
                    else:
                        ext = os.path.splitext(selected)[1].lower()
                        is_audio = ext in ('.mp3', '.flac', '.ogg', '.wav', '.aac', '.m4a')
                    
                    if is_audio:
                        self.playlist.append(selected)
                        self.modified = True
                        self.updateList()
                        
                        debug_print(f"Added track: {os.path.basename(selected)}")
                        self.showMessage(_("Track added"))
                    else:
                        self.showError(_("Not an audio file"))
            
            self.session.openWithCallback(
                trackSelected,
                FileBrowser,
                "/media/hdd/",
                showDirectories=False,
                matchingPattern=".*\\.(mp3|flac|ogg|wav|aac|m4a)$"
            )
        except Exception as e:
            debug_print(f"addTrack error: {e}")
            self.showError(_("Error adding track"))
    
    def updateList(self):
        """Update the displayed list"""
        try:
            playlist_items = []
            for i, filepath in enumerate(self.playlist):
                filename = os.path.basename(filepath)
                # Use media utilities for sanitization if available
                if MEDIA_UTILS_AVAILABLE:
                    display_name = media_utils.sanitize_filename(filename)
                else:
                    display_name = filename
                
                playlist_items.append((f"{i+1:02d}. {display_name}", filepath))
            
            current_index = self["playlist"].getSelectionIndex()
            self["playlist"].setList(playlist_items)
            
            # Restore selection if possible
            if current_index < len(playlist_items):
                self["playlist"].moveToIndex(current_index)
            
            debug_print(f"Playlist updated: {len(self.playlist)} tracks")
            
        except Exception as e:
            debug_print(f"updateList error: {e}")
    
    def save(self):
        """Save playlist changes"""
        try:
            if self.modified:
                self.close(self.playlist)
                debug_print("Playlist saved with modifications")
            else:
                self.close(None)
                debug_print("Playlist unchanged")
        except Exception as e:
            debug_print(f"save error: {e}")
            self.close(None)
    
    def cancel(self):
        """Cancel editing"""
        try:
            self.close(None)
            debug_print("Playlist editing cancelled")
        except Exception as e:
            debug_print(f"cancel error: {e}")
    
    def showMenu(self):
        """Show editor menu"""
        try:
            from Screens.ChoiceBox import ChoiceBox
            
            menu = [
                (_("Move Up"), self.moveUp),
                (_("Move Down"), self.moveDown),
                (_("Clear All"), self.clearAll),
                (_("Sort by Name"), self.sortByName),
                (_("Sort by Path"), self.sortByPath),
                (_("Save Playlist As..."), self.saveAs),
            ]
            
            self.session.openWithCallback(
                self.menuCallback,
                ChoiceBox,
                title=_("Playlist Editor Menu"),
                list=menu
            )
        except Exception as e:
            debug_print(f"showMenu error: {e}")
    
    def menuCallback(self, choice):
        """Handle menu choice"""
        try:
            if choice:
                debug_print(f"Menu choice: {choice[0]}")
                choice[1]()
        except Exception as e:
            debug_print(f"menuCallback error: {e}")
    
    def moveUp(self):
        """Move selected track up"""
        try:
            index = self["playlist"].getSelectionIndex()
            if index > 0:
                self.playlist[index], self.playlist[index-1] = self.playlist[index-1], self.playlist[index]
                self.modified = True
                self.updateList()
                self["playlist"].moveToIndex(index-1)
                
                debug_print(f"Moved track {index} up to {index-1}")
        except Exception as e:
            debug_print(f"moveUp error: {e}")
    
    def moveDown(self):
        """Move selected track down"""
        try:
            index = self["playlist"].getSelectionIndex()
            if index < len(self.playlist) - 1:
                self.playlist[index], self.playlist[index+1] = self.playlist[index+1], self.playlist[index]
                self.modified = True
                self.updateList()
                self["playlist"].moveToIndex(index+1)
                
                debug_print(f"Moved track {index} down to {index+1}")
        except Exception as e:
            debug_print(f"moveDown error: {e}")
    
    def clearAll(self):
        """Clear entire playlist"""
        try:
            from Screens.MessageBox import MessageBox
            self.session.openWithCallback(
                self.clearConfirmed,
                MessageBox,
                _("Clear entire playlist?"),
                MessageBox.TYPE_YESNO
            )
        except Exception as e:
            debug_print(f"clearAll error: {e}")
    
    def clearConfirmed(self, result):
        """Handle clear confirmation"""
        try:
            if result:
                self.playlist = []
                self.modified = True
                self.updateList()
                debug_print("Playlist cleared")
                self.showMessage(_("Playlist cleared"))
        except Exception as e:
            debug_print(f"clearConfirmed error: {e}")
    
    def sortByName(self):
        """Sort playlist by filename"""
        try:
            self.playlist.sort(key=lambda x: os.path.basename(x).lower())
            self.modified = True
            self.updateList()
            debug_print("Playlist sorted by name")
            self.showMessage(_("Sorted by name"))
        except Exception as e:
            debug_print(f"sortByName error: {e}")
    
    def sortByPath(self):
        """Sort playlist by full path"""
        try:
            self.playlist.sort(key=lambda x: x.lower())
            self.modified = True
            self.updateList()
            debug_print("Playlist sorted by path")
            self.showMessage(_("Sorted by path"))
        except Exception as e:
            debug_print(f"sortByPath error: {e}")
    
    def saveAs(self):
        """Save playlist to new file"""
        try:
            from Screens.VirtualKeyBoard import VirtualKeyBoard
            
            default_name = "new_playlist.m3u"
            self.session.openWithCallback(
                lambda name: self.doSaveAs(name if name else default_name),
                VirtualKeyBoard,
                title=_("Enter playlist name"),
                text=default_name
            )
        except Exception as e:
            debug_print(f"saveAs error: {e}")
    
    def doSaveAs(self, filename):
        """Save playlist to new file"""
        try:
            if not filename.lower().endswith('.m3u'):
                filename += '.m3u'
            
            # Use /tmp directory for saving
            full_path = f"/tmp/{filename}"
            
            # Use media utilities if available
            if MEDIA_UTILS_AVAILABLE:
                success = media_utils.save_m3u_playlist(full_path, self.playlist)
                if success:
                    self.showMessage(_("Playlist saved as: {}").format(full_path))
                    debug_print(f"Playlist saved as: {full_path}")
                else:
                    self.showError(_("Error saving playlist"))
            else:
                # Manual save
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write("#EXTM3U\n")
                    for track in self.playlist:
                        f.write(f"{track}\n")
                
                self.showMessage(_("Playlist saved as: {}").format(full_path))
                debug_print(f"Playlist saved as: {full_path}")
            
        except Exception as e:
            debug_print(f"doSaveAs error: {e}")
            self.showError(_("Error saving playlist"))
    
    def showMessage(self, message):
        """Show message to user"""
        try:
            from Screens.MessageBox import MessageBox
            self.session.open(MessageBox, message, MessageBox.TYPE_INFO, timeout=2)
        except Exception as e:
            debug_print(f"showMessage error: {e}")
    
    def showError(self, error):
        """Show error message"""
        try:
            from Screens.MessageBox import MessageBox
            self.session.open(MessageBox, error, MessageBox.TYPE_ERROR, timeout=3)
            debug_print(f"Error shown: {error}")
        except Exception as e:
            debug_print(f"showError error: {e}")


# Test function
if __name__ == "__main__":
    print(f"{PLUGIN_NAME} Playlist Editor v{PLUGIN_VERSION}")
    print("=" * 60)
    
    print("Playlist Editor Features:")
    print("  • Add/remove audio files from playlist")
    print("  • Reorder tracks (move up/down)")
    print("  • Sort by name or path")
    print("  • Clear entire playlist")
    print("  • Save playlist to M3U format")
    print("  • Support for all common audio formats")
    
    # Create a test playlist
    test_playlist = [
        "/path/to/song1.mp3",
        "/path/to/song2.flac",
        "/path/to/song3.ogg"
    ]
    
    print(f"\nTest playlist with {len(test_playlist)} tracks:")
    for i, track in enumerate(test_playlist, 1):
        print(f"  {i}. {os.path.basename(track)}")
    
    print("\n" + "=" * 60)
    print("PlaylistEditor module ready for v2.1.0 integration")