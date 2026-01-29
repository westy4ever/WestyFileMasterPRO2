#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division, unicode_literals

import os
import re
import sys

# ============================================================================
# IMPORT PLUGIN UTILITIES
# ============================================================================
try:
    from . import (
        _,
        debug_print,
        ensure_str,
        ensure_unicode,
        path_exists,
        isdir_unicode,
        isfile_unicode,
        PLUGIN_PATH,
        get_icon_path
    )
    # Try to import performance cache
    try:
        from .CacheManager import file_info_cache, image_cache
        CACHE_AVAILABLE = True
        debug_print("FileList: CacheManager imported successfully")
    except ImportError:
        CACHE_AVAILABLE = False
        debug_print("FileList: CacheManager not available")

except ImportError:
    # Fallback for testing
    def _(text): return text
    def debug_print(*args, **kwargs):
        if args: print("[FileList]", *args)
    def ensure_str(s, encoding='utf-8'): return str(s)
    ensure_unicode = ensure_str
    def path_exists(path): return os.path.exists(str(path))
    def isdir_unicode(path): return os.path.isdir(str(path))
    def isfile_unicode(path): return os.path.isfile(str(path))
    PLUGIN_PATH = os.path.dirname(os.path.abspath(__file__))
    def get_icon_path(icon_name):
        # Simple icon path lookup
        paths = [
            os.path.join(PLUGIN_PATH, "images", icon_name),
            os.path.join(os.path.dirname(PLUGIN_PATH), "images", icon_name),
            "/usr/lib/enigma2/python/Plugins/Extensions/WestyFileMasterPRO/images/" + icon_name
        ]
        for path in paths:
            if os.path.exists(path):
                return path
        return None
    CACHE_AVAILABLE = False
# ============================================================================
# ENIGMA2 FILELIST BASE CLASS
# ============================================================================
try:
    from Components.FileList import FileList as FileListBase
    from enigma import RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_VALIGN_CENTER
    from enigma import eListboxPythonMultiContent, gFont
    from Tools.LoadPixmap import LoadPixmap
    ENIGMA2_FILELIST_AVAILABLE = True
    debug_print("FileList: Enigma2 FileList available")
except ImportError as e:
    debug_print(f"FileList: Enigma2 FileList not available: {e}")
    ENIGMA2_FILELIST_AVAILABLE = False
    
    # Mock FileListBase
    class FileListBase:
        def __init__(self, directory, **kwargs):
            self.current_directory = ensure_str(directory)
            self.list = []
            self.instance = None
            self.current_index = 0
        
        def changeDir(self, directory, select=None):
            self.current_directory = directory
            return True
        
        def refresh(self):
            pass
        
        def execBegin(self): pass
        def execEnd(self): pass
        
        def getSelection(self):
            if self.list and 0 <= self.current_index < len(self.list):
                return self.list[self.current_index]
            return None
        
        def getCurrent(self):
            return self.getSelection()
        
        def getSelectionIndex(self):
            return self.current_index
        
        def getIndex(self):
            return self.current_index
        
        def setIndex(self, index):
            if 0 <= index < len(self.list):
                self.current_index = index
        
        def moveSelection(self, direction):
            pass
        
        def moveUp(self):
            if self.current_index > 0:
                self.current_index -= 1
        
        def moveDown(self):
            if self.current_index < len(self.list) - 1:
                self.current_index += 1
        
        def pageUp(self):
            self.current_index = max(0, self.current_index - 10)
        
        def pageDown(self):
            self.current_index = min(len(self.list) - 1, self.current_index + 10)
        
        def setList(self, lst):
            self.list = lst
    
    # Mock constants and functions
    def LoadPixmap(path=None):
        debug_print(f"LoadPixmap called for: {path}")
        return None
    
    RT_HALIGN_LEFT = 0
    RT_HALIGN_RIGHT = 1
    RT_VALIGN_CENTER = 1
    
    class eListboxPythonMultiContent:
        TYPE_PIXMAP_ALPHABLEND = 1
        TYPE_TEXT = 0
    
    class gFont:
        pass

# ============================================================================
# WESTY FILELIST CLASS
# ============================================================================
class WestyFileList(FileListBase):
    """Enhanced FileList with icons, multi-selection, and pane highlighting"""
    
    def __init__(self, directory, active=False, show_hidden=False, **kwargs):
        """
        Initialize enhanced FileList
        
        Args:
            directory: Starting directory
            active: Whether this pane is active
            show_hidden: Whether to show hidden files
            **kwargs: Additional parameters for parent FileList
        """
        
        # Store custom parameters
        self.show_hidden = show_hidden
        self.active = active
        self.highlight_color = "#00ff00" if active else "#ffffff"
        self.normal_color = "#cccccc"
        self.selected_color = "#ff9900"
        self.selected_bg_color = "#2a3b4c"
        self.current_selection_color = "#ffff00"

        # PERFORMANCE SETTINGS (NEW)
        try:
            from Components.config import config
            self.show_icons = config.plugins.westyfilemaster.show_icons.value
            self.compact_view = config.plugins.westyfilemaster.compact_view.value
            self.enable_cache = config.plugins.westyfilemaster.enable_cache.value
            self.virtual_scroll = config.plugins.westyfilemaster.virtual_scroll.value
            self.cache_size = int(config.plugins.westyfilemaster.cache_size.value)
        except Exception as e:
            debug_print(f"FileList: Could not load performance settings: {e}")
            self.show_icons = True
            self.compact_view = False
            self.enable_cache = True
            self.virtual_scroll = True
            self.cache_size = 1000
        
        # Multi-selection support
        self.selection_manager = None
        self.pane_id = "left" if active else "right"
        self.last_selected_index = None
        self.keys_held = {}
        
        # Performance tracking
        self.visible_range = 50  # Render ±50 items from current position
        self.item_positions = {}  # Track item positions for virtual scroll
        self.current_render_index = 0
       
        # Cache references
        if CACHE_AVAILABLE and self.enable_cache:
            self.file_cache = file_info_cache
            self.image_cache = image_cache
            # Update cache size if config changed
            if hasattr(self.file_cache, 'max_size'):
                self.file_cache.max_size = self.cache_size
        else:
            self.file_cache = None
            self.image_cache = None

        # Ensure directory is proper string
        directory = ensure_str(directory)
        if not directory.endswith('/'):
            directory += '/'
        
        debug_print(f"WestyFileList: Initializing directory={directory}, active={active}, show_hidden={show_hidden}")
        
        # Extract parameters for parent
        parent_kwargs = {
            'showDirectories': kwargs.pop('showDirectories', True),
            'showFiles': kwargs.pop('showFiles', True),
            'showMountpoints': kwargs.pop('showMountpoints', True),
            'matchingPattern': kwargs.pop('matchingPattern', None),
            'useServiceRef': kwargs.pop('useServiceRef', False),
            'inhibitDirs': kwargs.pop('inhibitDirs', False),
            'inhibitMounts': kwargs.pop('inhibitMounts', False),
            'isTop': kwargs.pop('isTop', False),
            'enableWrapAround': kwargs.pop('enableWrapAround', True),
            'additionalExtensions': kwargs.pop('additionalExtensions', None),
        }
        
        # Call parent constructor
        try:
            FileListBase.__init__(self, directory, **parent_kwargs)
        except TypeError as e:
            debug_print(f"WestyFileList: Parent init failed: {e}")
            # Fallback with minimal parameters
            try:
                FileListBase.__init__(self, directory)
            except:
                # Last resort
                self.current_directory = directory
                self.list = []
    
    # ========================================================================
    # CORE METHODS
    # ========================================================================
    def setActive(self, active):
        """Set this pane as active/inactive"""
        self.active = active
        self.highlight_color = "#00ff00" if active else "#ffffff"
        debug_print(f"WestyFileList: Set active={active}")
        self.refresh()
    
    def setSelectionManager(self, manager, pane_id):
        """Set the selection manager and pane ID"""
        self.selection_manager = manager
        self.pane_id = pane_id
        debug_print(f"WestyFileList: Set selection manager for pane {pane_id}")
    
    def setPaneId(self, pane_id):
        """Set the pane ID"""
        self.pane_id = pane_id
    
    def changeDir(self, directory, select=None):
        """Override changeDir to handle unicode and hidden files"""
        directory = ensure_str(directory)
        if not directory.endswith('/'):
            directory += '/'
        
        debug_print(f"WestyFileList: Changing to directory: {directory}")
        
        # Call parent method
        try:
            result = FileListBase.changeDir(self, directory, select)
        except Exception as e:
            debug_print(f"WestyFileList: Parent changeDir failed: {e}")
            self.current_directory = directory
            result = True
        
        # Filter out hidden files if not showing them
        if not self.show_hidden and hasattr(self, 'list') and self.list:
            filtered_list = []
            for item in self.list:
                if not self._is_hidden_item(item):
                    filtered_list.append(item)
            self.list = filtered_list
        
        return result
    
    def _is_hidden_item(self, item):
        """Check if item is hidden (starts with dot)"""
        try:
            if isinstance(item, (tuple, list)) and len(item) > 0:
                filename = item[0]
            else:
                filename = str(item)
            
            name = os.path.basename(ensure_str(filename))
            return name.startswith('.')
        except:
            return False
    
    # ========================================================================
    # LIST ENTRY BUILDING
    # ========================================================================
    def buildEntryComponent(self, name, absolute, isDir, isLink):
        """Build list entry with appropriate coloring and icons"""
        # VIRTUAL SCROLLING: Check if item should be rendered
        if self.virtual_scroll:
            try:
                current_idx = self.getSelectionIndex()
                item_idx = self.current_render_index
                
                # Only render items within visible range
                if abs(current_idx - item_idx) > self.visible_range:
                    # Return minimal entry for spacing
                    return [(absolute, isDir, isLink)]
            except:
                pass  # Fallback if virtual scroll fails

        self.current_render_index += 1

        name_str = ensure_str(name)
        absolute_str = ensure_str(absolute)

        # Check selection states
        is_current_selection = self._is_current_selection(name_str)
        is_multi_selected = False

        if self.selection_manager:
            is_multi_selected = self.selection_manager.is_selected(absolute_str, self.pane_id)

        # Determine colors
        if is_multi_selected:
            text_color = self.selected_color
            bg_color = self.selected_bg_color
        elif is_current_selection and self.active:
            text_color = self.current_selection_color
            bg_color = "#2a3b4c"
        elif self.active:
            text_color = self.highlight_color
            bg_color = None
        else:
            text_color = self.normal_color
            bg_color = None

        # Handle hidden files
        is_hidden = name_str.startswith('.')
        if is_hidden:
            text_color = "#888888"

        # Start building entry
        res = [(absolute_str, isDir, isLink)]

        # Add icon with selection indicator
        icon = None
        if self.show_icons:
            icon = self._get_icon_for_item(name_str, isDir, isLink)

            # Selection indicator for multi-selected items
            if is_multi_selected:
                selection_icon_path = get_icon_path("selected.png")
                if selection_icon_path and os.path.exists(selection_icon_path):
                    try:
                        selection_icon = LoadPixmap(path=selection_icon_path)
                        res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, 
                                8, 2, 24, 24, selection_icon))
                    except:
                        pass
                else:
                    # Fallback text indicator
                    res.append((eListboxPythonMultiContent.TYPE_TEXT,
                            10, 4, 20, 20,
                            0, RT_HALIGN_CENTER, "✓", "#00ff00"))

            # Main icon
            if icon:
                res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, 
                        35, 4, 20, 20, icon))
            else:
                # Placeholder
                res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, 
                        35, 4, 20, 20, None))
        else:
            # No icons mode - adjust positioning
            text_x_pos = 35  # Start text where icon would be

        # File name with selection number
        display_name = name_str
        if is_hidden:
            display_name = "• " + display_name

        if is_multi_selected and self.selection_manager:
            try:
                selected_paths = self.selection_manager.get_selected_paths(self.pane_id)
                selection_index = selected_paths.index(absolute_str) + 1
                display_name = f"[{selection_index}] {display_name}"
            except:
                pass

        # Add text entry based on icon mode
        if self.show_icons:
            res.append((eListboxPythonMultiContent.TYPE_TEXT, 
                    60, 1, 1150, 25, 
                    0, RT_HALIGN_LEFT, display_name, text_color, bg_color))
        else:
            # Compact mode without icons
            res.append((eListboxPythonMultiContent.TYPE_TEXT, 
                    35, 1, 1175, 25, 
                    0, RT_HALIGN_LEFT, display_name, text_color, bg_color))

        # File size for files
        if not isDir:
            try:
                size = os.path.getsize(absolute_str)
                size_str = self._format_size(size)
                res.append((eListboxPythonMultiContent.TYPE_TEXT,
                        -50, 1, 100, 25,
                        0, RT_HALIGN_RIGHT, size_str, "#888888"))
            except:
                pass

        # Permissions indicator
        perm_str = self._get_permissions_string(absolute_str)
        if perm_str:
            res.append((eListboxPythonMultiContent.TYPE_TEXT,
                    -160, 1, 100, 25,
                    0, RT_HALIGN_RIGHT, perm_str, "#666666"))

        return res
    
    def _is_current_selection(self, filename):
        """Check if this is the currently highlighted item"""
        selection = self.getSelection()
        if selection:
            current_filename = selection[0]
            return ensure_str(current_filename) == ensure_str(filename)
        return False
    
    def _get_icon_for_item(self, filename, isDir, isLink):
        """Get appropriate icon for file/directory"""
        if not self.show_icons:
            return None  # Icons disabled
            
        if isLink:
            icon_name = "link.png"
        elif isDir:
            icon_name = "folder.png"
        else:
            # Determine by extension
            _, ext = os.path.splitext(filename)
            ext = ext[1:].lower() if ext else ""
            
            icon_map = {
                # Programming
                'py': 'python.png', 'pyc': 'python.png', 'pyo': 'python.png',
                'sh': 'script.png', 'bash': 'script.png',
                'js': 'script.png', 'html': 'script.png', 'css': 'script.png',
                'xml': 'script.png', 'json': 'script.png',
                
                # Text
                'txt': 'text.png', 'log': 'text.png',
                'cfg': 'text.png', 'conf': 'text.png', 'ini': 'text.png',
                
                # Media
                'jpg': 'image.png', 'jpeg': 'image.png', 'png': 'image.png',
                'gif': 'image.png', 'bmp': 'image.png',
                
                'mp3': 'audio.png', 'wav': 'audio.png', 'flac': 'audio.png',
                'ogg': 'audio.png', 'aac': 'audio.png',
                
                'mp4': 'video.png', 'avi': 'video.png', 'mkv': 'video.png',
                'mov': 'video.png', 'flv': 'video.png',
                
                # Archives
                'zip': 'archive.png', 'rar': 'archive.png', 'tar': 'archive.png',
                'gz': 'archive.png', 'bz2': 'archive.png',
                
                # Documents
                'pdf': 'document.png', 'doc': 'document.png', 'docx': 'document.png',
                'xls': 'document.png', 'xlsx': 'document.png',
                
                # System
                'iso': 'disk.png', 'img': 'disk.png',
            }
            
            icon_name = icon_map.get(ext, 'file.png')
        
        # Load the icon
        icon_path = get_icon_path(icon_name)
        if icon_path and os.path.exists(icon_path):
            try:
                if self.image_cache and self.enable_cache:
                    # Use cached icon
                    return self.image_cache.get_icon(icon_path, LoadPixmap)
                else:
                    return LoadPixmap(path=icon_path)
            except Exception as e:
                debug_print(f"WestyFileList: Failed to load icon {icon_path}: {e}")
        
        # Try default file icon
        default_path = get_icon_path('file.png')
        if default_path and os.path.exists(default_path):
            try:
                if self.image_cache and self.enable_cache:
                    return self.image_cache.get_icon(default_path, LoadPixmap)
                else:
                    return LoadPixmap(path=default_path)
            except:
                pass
        
        return None
    
    def _get_file_info_with_cache(self, path):
        """Get file information with caching"""
        if not self.enable_cache or not self.file_cache:
            return self._get_file_info_uncached(path)
       
        try:
            # Use cache with fallback function
            def get_file_info_func(p):
                return {
                    'name': os.path.basename(p),
                    'size': os.path.getsize(p) if os.path.isfile(p) else 0,
                    'mtime': os.path.getmtime(p),
                    'mode': os.stat(p).st_mode
                }
            
            return self.file_cache.get(path, get_file_info_func)
        except Exception as e:
            debug_print(f"Cache error for {path}: {e}")
            return self._get_file_info_uncached(path)
    
    def _get_file_info_uncached(self, path):
        """Get file info without cache (fallback)"""
        try:
            return {
                'name': os.path.basename(path),
                'size': os.path.getsize(path) if os.path.isfile(path) else 0,
                'mtime': os.path.getmtime(path),
                'mode': os.stat(path).st_mode
            }
        except:
           return {'name': os.path.basename(path), 'size': 0, 'mtime': 0, 'mode': 0}    
    def _format_size(self, size):
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                if unit == 'B':
                    return f"{size:.0f} {unit}"
                else:
                    return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
    
    def _get_permissions_string(self, path):
        """Get Unix permissions string"""
        try:
            import stat
            mode = os.stat(ensure_str(path)).st_mode
            
            # File type
            if stat.S_ISDIR(mode):
                perms = 'd'
            elif stat.S_ISLNK(mode):
                perms = 'l'
            else:
                perms = '-'
            
            # Owner permissions
            perms += 'r' if mode & stat.S_IRUSR else '-'
            perms += 'w' if mode & stat.S_IWUSR else '-'
            perms += 'x' if mode & stat.S_IXUSR else '-'
            
            # Group permissions
            perms += 'r' if mode & stat.S_IRGRP else '-'
            perms += 'w' if mode & stat.S_IWGRP else '-'
            perms += 'x' if mode & stat.S_IXGRP else '-'
            
            # Other permissions
            perms += 'r' if mode & stat.S_IROTH else '-'
            perms += 'w' if mode & stat.S_IWOTH else '-'
            perms += 'x' if mode & stat.S_IXOTH else '-'
            
            return perms
        except:
            return ""
    
    # ========================================================================
    # PUBLIC METHODS
    # ========================================================================
    def refresh(self):
        """Refresh list with current active state"""
        debug_print(f"WestyFileList: Refreshing, active={self.active}")

        # Reset virtual scrolling state
        self.current_render_index = 0
        self.item_positions.clear()
        
        if hasattr(self, 'current_directory') and self.current_directory:
            self.changeDir(self.current_directory)
        else:
            try:
                FileListBase.refresh(self)
            except:
                pass
    
    def getFilename(self):
        """Get selected filename"""
        selection = self.getSelection()
        if selection and len(selection) > 0:
            return ensure_str(selection[0])
        return None
    
    def getCurrentDirectory(self):
        """Get current directory"""
        if hasattr(self, 'current_directory'):
            return ensure_str(self.current_directory)
        return ""
    
    def canDescent(self):
        """Check if current selection is a directory"""
        selection = self.getSelection()
        if selection and len(selection) > 1:
            return bool(selection[1])
        return False
    
    def descent(self):
        """Enter selected directory"""
        selection = self.getSelection()
        if selection and selection[1]:  # is directory
            new_dir = os.path.join(self.getCurrentDirectory(), selection[0])
            self.changeDir(new_dir)
            # Clear selection when entering directory
            if self.selection_manager:
                self.selection_manager.clear_selection(self.pane_id)
            return True
        return False
    
    def getItemHeight(self):
        """Get item height based on settings"""
        if self.compact_view:
            return 30  # Compact mode
        else:
            return 40  # Normal mode
    # ========================================================================
    # NAVIGATION METHODS
    # ========================================================================
    def up(self):
        """Move selection up"""
        try:
            if hasattr(self, 'instance'):
                self.instance.moveSelection(self.instance.moveUp)
            elif hasattr(self, 'moveUp'):
                self.moveUp()
        except:
            pass
        self.refresh()
    
    def down(self):
        """Move selection down"""
        try:
            if hasattr(self, 'instance'):
                self.instance.moveSelection(self.instance.moveDown)
            elif hasattr(self, 'moveDown'):
                self.moveDown()
        except:
            pass
        self.refresh()
    
    def pageUp(self):
        """Page up"""
        try:
            if hasattr(self, 'instance'):
                self.instance.moveSelection(self.instance.pageUp)
            elif hasattr(self, 'pageUp'):
                self.pageUp()
        except:
            pass
        self.refresh()
    
    def pageDown(self):
        """Page down"""
        try:
            if hasattr(self, 'instance'):
                self.instance.moveSelection(self.instance.pageDown)
            elif hasattr(self, 'pageDown'):
                self.pageDown()
        except:
            pass
        self.refresh()
    
    # ========================================================================
    # SELECTION HANDLING
    # ========================================================================
    def handleOk(self):
        """Handle OK button press for multi-selection"""
        selection = self.getSelection()
        if not selection:
            return False
        
        filename = selection[0]
        current_dir = self.getCurrentDirectory()
        full_path = os.path.join(current_dir, filename)
        
        file_info = {
            'name': filename,
            'full_path': full_path,
            'isdir': bool(selection[1]) if len(selection) > 1 else False,
            'size': 0
        }
        
        # Get file size
        try:
            if not file_info['isdir']:
                file_info['size'] = os.path.getsize(full_path)
        except:
            pass
        
        if not self.selection_manager:
            return False
        
        # Toggle selection
        self.selection_manager.toggle_selection(full_path, file_info, self.pane_id)
        self.last_selected_index = self.getSelectionIndex()
        
        self.refresh()
        return True
    
    def clearSelectionState(self):
        """Clear selection state"""
        self.last_selected_index = None
        self.keys_held.clear()
        self.refresh()
    
    def selectAllVisible(self):
        """Select all visible items"""
        if not self.selection_manager:
            return 0
        
        count = 0
        items = self.getFileListItems()
        
        for item in items:
            if isinstance(item, (list, tuple)) and len(item) > 0:
                filename = item[0]
                current_dir = self.getCurrentDirectory()
                full_path = os.path.join(current_dir, filename)
                
                if self.selection_manager.is_selected(full_path, self.pane_id):
                    continue
                
                file_info = {
                    'name': filename,
                    'full_path': full_path,
                    'isdir': bool(item[1]) if len(item) > 1 else False,
                    'size': 0
                }
                
                self.selection_manager.select_item(full_path, file_info, self.pane_id)
                count += 1
        
        self.refresh()
        return count
    
    def deselectAll(self):
        """Deselect all items"""
        if self.selection_manager:
            self.selection_manager.clear_selection(self.pane_id)
            self.refresh()
    
    def getFileListItems(self):
        """Get current list of file items"""
        if hasattr(self, 'list'):
            return self.list
        return []
    
    def updateSelectionDisplay(self):
        """Update display to reflect selections"""
        self.refresh()
    
    # ========================================================================
    # COMPATIBILITY METHODS
    # ========================================================================
    def execBegin(self):
        """Called when screen begins execution"""
        if hasattr(super(), 'execBegin'):
            super().execBegin()
    
    def execEnd(self):
        """Called when screen ends execution"""
        if hasattr(super(), 'execEnd'):
            super().execEnd()
    
    def getSelectionIndex(self):
        """Get current selection index"""
        if hasattr(super(), 'getSelectionIndex'):
            return super().getSelectionIndex()
        return 0
    
    def getIndex(self):
        """Get current index"""
        return self.getSelectionIndex()
    
    def setIndex(self, index):
        """Set current index"""
        if hasattr(super(), 'setIndex'):
            super().setIndex(index)
    
    def moveSelection(self, direction):
        """Move selection"""
        if hasattr(super(), 'moveSelection'):
            super().moveSelection(direction)
    
    def setList(self, lst):
        """Set list items"""
        if hasattr(super(), 'setList'):
            super().setList(lst)
        else:
            self.list = lst

# ========================================================================
# TEST FUNCTION
# ========================================================================
if __name__ == "__main__":
    print("Westy FileList Test")
    print("=" * 60)
    
    # Test initialization
    try:
        fl = WestyFileList("/tmp", active=True, show_hidden=False)
        print(f"✓ FileList initialized")
        print(f"  Directory: {fl.getCurrentDirectory()}")
        print(f"  Active: {fl.active}")
        print(f"  Show hidden: {fl.show_hidden}")
    except Exception as e:
        print(f"✗ FileList test failed: {e}")
    
    # Test icon path resolution
    print("\nIcon path test:")
    icon_path = get_icon_path("folder.png")
    print(f"  Folder icon: {icon_path}")
    print(f"  Exists: {os.path.exists(icon_path) if icon_path else False}")
    
    print("=" * 60)