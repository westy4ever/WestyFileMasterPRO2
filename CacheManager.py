#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CacheManager.py - Performance caching system

from __future__ import print_function, absolute_import, division, unicode_literals

import os
import time
import sys
from collections import OrderedDict

# Import plugin utilities
try:
    from . import (
        _,
        debug_print,
        ensure_str,
        ensure_unicode,
    )
except ImportError:
    # Fallback for testing
    def _(text): return text
    def debug_print(*args, **kwargs):
        if args: print(*args)
    def ensure_str(s, encoding='utf-8'): return str(s)
    ensure_unicode = ensure_str


class FileInfoCache:
    """LRU cache for file information"""
    
    def __init__(self, max_size=1000, ttl=300):
        self.max_size = max_size
        self.ttl = ttl  # Time to live in seconds
        self.cache = OrderedDict()
        self.hits = 0
        self.misses = 0
        
    def get(self, path, getter_func):
        """Get item from cache or compute it"""
        path_str = ensure_str(path)
        now = time.time()
        
        # Check cache
        if path_str in self.cache:
            info, timestamp = self.cache[path_str]
            
            # Check if still valid
            if now - timestamp < self.ttl:
                # Move to end (most recently used)
                self.cache.move_to_end(path_str)
                self.hits += 1
                return info
            else:
                # Expired, remove it
                del self.cache[path_str]
        
        # Not in cache or expired
        self.misses += 1
        
        # Get fresh data
        info = getter_func(path_str)
        
        # Add to cache
        self._add_to_cache(path_str, info, now)
        
        return info
    
    def _add_to_cache(self, key, value, timestamp):
        """Add item to cache with LRU eviction"""
        # Remove if exists
        if key in self.cache:
            del self.cache[key]
        
        # Add new item
        self.cache[key] = (value, timestamp)
        
        # Evict if needed
        if len(self.cache) > self.max_size:
            # Remove oldest
            self.cache.popitem(last=False)
    
    def clear(self):
        """Clear entire cache"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
    
    def invalidate(self, path):
        """Remove specific path from cache"""
        path_str = ensure_str(path)
        if path_str in self.cache:
            del self.cache[path_str]
    
    def invalidate_directory(self, dir_path):
        """Remove all cached items in a directory"""
        dir_path_str = ensure_str(dir_path)
        to_remove = []
        
        for key in self.cache.keys():
            if key.startswith(dir_path_str):
                to_remove.append(key)
        
        for key in to_remove:
            del self.cache[key]
    
    def get_stats(self):
        """Get cache statistics"""
        total = self.hits + self.misses
        hit_rate = self.hits / total * 100 if total > 0 else 0
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': f"{hit_rate:.1f}%",
            'usage': f"{len(self.cache) / self.max_size * 100:.1f}%" if self.max_size > 0 else "0%"
        }


class ImageCache:
    """Cache for loaded icons and images"""
    
    def __init__(self, max_size=50):
        self.max_size = max_size
        self.cache = OrderedDict()
        
    def get_icon(self, icon_path, loader_func):
        """Get icon from cache or load it"""
        if icon_path in self.cache:
            # Move to end (most recently used)
            self.cache.move_to_end(icon_path)
            return self.cache[icon_path]
        
        # Load icon
        icon = loader_func(icon_path)
        
        # Cache it
        self.cache[icon_path] = icon
        
        # Evict if needed
        if len(self.cache) > self.max_size:
            self.cache.popitem(last=False)
        
        return icon
    
    def clear(self):
        """Clear image cache"""
        self.cache.clear()


# Global cache instances
file_info_cache = FileInfoCache(max_size=1000, ttl=300)
image_cache = ImageCache(max_size=50)


# Helper functions
def get_cached_file_info(path):
    """Helper function to get cached file info"""
    from .Directories import SmartDirectoryManager
    
    return file_info_cache.get(
        path,
        lambda p: SmartDirectoryManager.getFileInfo(p)
    )


def clear_caches():
    """Clear all caches"""
    file_info_cache.clear()
    image_cache.clear()


def get_cache_stats():
    """Get statistics for all caches"""
    return {
        'file_info': file_info_cache.get_stats(),
        'image_cache': {
            'size': len(image_cache.cache),
            'max_size': image_cache.max_size
        }
    }


if __name__ == "__main__":
    print("CacheManager - Performance Caching System")
    print("=" * 60)
    print("✓ File info cache initialized")
    print("✓ Image cache initialized")
    print("=" * 60)