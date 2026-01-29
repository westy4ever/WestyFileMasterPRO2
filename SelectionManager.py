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
    )
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
            except UnicodeDecodeError as e:
                print("Error: {}".format(e))
                return s.decode('latin-1', 'ignore')
        return str(s)
    
    ensure_unicode = ensure_str


class SelectionManager:
    """Manages multi-selection of files and directories across panes"""
    
    def __init__(self):
        self.selected_items = {}  # key: (pane_id, path), value: file_info dict
        self.total_size = 0
        self.current_pane = "left"  # Track which pane selections belong to
        self.keys_held = {}  # Track Ctrl/Shift key state
    
    def set_current_pane(self, pane_id):
        """Set the current active pane"""
        self.current_pane = pane_id
    
    def get_current_pane(self):
        """Get current active pane"""
        return self.current_pane
    
    def select_item(self, path, file_info, pane_id=None):
        """Add item to selection"""
        if pane_id is None:
            pane_id = self.current_pane
        
        key = (pane_id, path)
        if key not in self.selected_items:
            self.selected_items[key] = file_info
            self.total_size += file_info.get('size', 0)
            return True
        return False
    
    def deselect_item(self, path, pane_id=None):
        """Remove item from selection"""
        if pane_id is None:
            pane_id = self.current_pane
        
        key = (pane_id, path)
        if key in self.selected_items:
            file_info = self.selected_items.pop(key)
            self.total_size -= file_info.get('size', 0)
            return True
        return False
    
    def toggle_selection(self, path, file_info, pane_id=None):
        """Toggle item selection state"""
        if pane_id is None:
            pane_id = self.current_pane
        
        if self.is_selected(path, pane_id):
            return self.deselect_item(path, pane_id)
        else:
            return self.select_item(path, file_info, pane_id)
    
    def is_selected(self, path, pane_id=None):
        """Check if item is selected"""
        if pane_id is None:
            pane_id = self.current_pane
        
        key = (pane_id, path)
        return key in self.selected_items
    
    def get_selected_items(self, pane_id=None):
        """Get all selected items for a pane or all panes"""
        if pane_id:
            return [item for (pane, path), item in self.selected_items.items() 
                   if pane == pane_id]
        else:
            return list(self.selected_items.values())
    
    def get_selected_paths(self, pane_id=None):
        """Get all selected paths for a pane or all panes"""
        if pane_id:
            return [path for (pane, path) in self.selected_items.keys() 
                   if pane == pane_id]
        else:
            return [path for (pane, path) in self.selected_items.keys()]
    
    def get_selection_count(self, pane_id=None):
        """Get number of selected items"""
        if pane_id:
            return len([pane for pane, _ in self.selected_items.keys() 
                       if pane == pane_id])
        return len(self.selected_items)
    
    def get_total_size(self):
        """Get total size of selected items in bytes"""
        return self.total_size
    
    def clear_selection(self, pane_id=None):
        """Clear all selections or selections for specific pane"""
        if pane_id:
            # Remove only items from specific pane
            keys_to_remove = [key for key in self.selected_items.keys() 
                             if key[0] == pane_id]
            for key in keys_to_remove:
                file_info = self.selected_items.pop(key)
                self.total_size -= file_info.get('size', 0)
        else:
            # Clear all selections
            self.selected_items.clear()
            self.total_size = 0
    
    def get_formatted_summary(self):
        """Get formatted summary of selection"""
        count = self.get_selection_count()
        size = self.get_total_size()
        
        # Format size
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                size_text = f"{size:.2f} {unit}"
                break
            size /= 1024.0
        else:
            size_text = f"{size:.2f} PB"
        
        return f"{count} item{'s' if count != 1 else ''} ({size_text})"
    
    def get_items_by_pane(self):
        """Get selected items grouped by pane"""
        result = {}
        for (pane, path), item in self.selected_items.items():
            if pane not in result:
                result[pane] = []
            result[pane].append({
                'path': path,
                'info': item
            })
        return result
    
    def select_all_in_pane(self, file_list, pane_id=None):
        """Select all visible files in a pane"""
        if pane_id is None:
            pane_id = self.current_pane
        
        count = 0
        for item in file_list:
            path = item.get('full_path') or item.get('path')
            if path and not self.is_selected(path, pane_id):
                self.select_item(path, item, pane_id)
                count += 1
        return count
    
    def get_key_state(self, key):
        """Check if a key is currently held"""
        return self.keys_held.get(key, False)
    
    def set_key_state(self, key, state):
        """Set key held state"""
        self.keys_held[key] = state
    
    def clear_key_states(self):
        """Clear all key states"""
        self.keys_held.clear()
    
    def get_selection_details(self, pane_id=None):
        """Get detailed info about selected items"""
        if pane_id:
            return {path: info for (pane, path), info in self.selected_items.items() 
                   if pane == pane_id}
        else:
            return self.selected_items.copy()
    
    def get_summary_for_ui(self):
        """Get summary formatted for UI display"""
        count = self.get_selection_count()
        if count == 0:
            return "No selection"
        
        size = self.get_total_size()
        # Format size for UI
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                size_text = f"{size:.1f} {unit}"
                break
            size /= 1024.0
        else:
            size_text = f"{size:.1f} PB"
        
        return f"{count} item{'s' if count != 1 else ''} ({size_text})"


# Test function
if __name__ == "__main__":
    print("SelectionManager Test")
    print("=" * 60)
    
    # Create manager
    manager = SelectionManager()
    
    # Test basic selection
    test_file = {
        'name': 'test.txt',
        'size': 1024,
        'full_path': '/tmp/test.txt'
    }
    
    manager.select_item('/tmp/test.txt', test_file, 'left')
    print(f"Selected item: {manager.is_selected('/tmp/test.txt', 'left')}")
    print(f"Selection count: {manager.get_selection_count()}")
    print(f"Total size: {manager.get_total_size()}")
    
    # Test toggle
    manager.toggle_selection('/tmp/test.txt', test_file, 'left')
    print(f"After toggle - selected: {manager.is_selected('/tmp/test.txt', 'left')}")
    
    # Test summary
    manager.select_item('/tmp/test.txt', test_file, 'left')
    manager.select_item('/tmp/test2.txt', {'name': 'test2.txt', 'size': 2048, 'full_path': '/tmp/test2.txt'}, 'right')
    print(f"Summary: {manager.get_formatted_summary()}")
    
    # Test pane-specific operations
    print(f"Left pane count: {manager.get_selection_count('left')}")
    print(f"Right pane count: {manager.get_selection_count('right')}")
    
    # Test clear
    manager.clear_selection('left')
    print(f"After clear left - total count: {manager.get_selection_count()}")
    
    # Test UI summary
    print(f"UI Summary: {manager.get_summary_for_ui()}")
    
    print("=" * 60)