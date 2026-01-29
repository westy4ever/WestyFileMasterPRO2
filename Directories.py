#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division, unicode_literals

import os
import sys
import shutil
import stat
import time
import hashlib
import zipfile
import tarfile
import json
import glob
from datetime import datetime
from fnmatch import fnmatch
from pathlib import Path

# Import our plugin's compatibility functions
try:
    from . import (
        _,
        debug_print,
        ensure_str,
        ensure_unicode,
        bytes_to_str,
        str_to_bytes,
        PLUGIN_NAME,          # NEW: Add plugin metadata
        PLUGIN_VERSION        # NEW: Add version info
    )
except ImportError:
    # Fallback for testing
    def _(text):
        return text
    
    def debug_print(*args, **kwargs):
        if args:
            print(*args)  # CHANGED: Actually print for debugging
    
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
    
    def bytes_to_str(b, encoding='utf-8'):
        if isinstance(b, bytes):
            try:
                return b.decode(encoding)
            except UnicodeDecodeError:
                return b.decode(encoding, 'ignore')
        return str(b)
    
    def str_to_bytes(s, encoding='utf-8'):
        if isinstance(s, str):
            return s.encode(encoding)
        return bytes(s, encoding)
    
    PLUGIN_NAME = "Westy FileMaster PRO"      # NEW
    PLUGIN_VERSION = "2.1.0"                   # NEW

# OpenATV/Enigma2 imports - ENHANCED with full try/except
try:
    from enigma import eEnv
    from Tools.Directories import fileExists, pathExists, isMount
    
    # Try to import additional useful Enigma2 modules
    try:
        from Components.Harddisk import harddiskmanager
        from Tools.Directories import SCOPE_PLUGINS, SCOPE_SKIN, SCOPE_CURRENT_SKIN
        ENIGMA2_FULL = True
    except ImportError:
        ENIGMA2_FULL = False
    
    ENIGMA2_AVAILABLE = True
    debug_print(f"Directories: Enigma2 imports successful v{PLUGIN_VERSION}")
except ImportError as e:
    debug_print(f"Directories: Could not import Enigma2 modules: {e}")
    ENIGMA2_AVAILABLE = False
    
    class eEnv:
        @staticmethod
        def resolve(path):
            # Simple path resolution for testing
            replacements = {
                "${libdir}/enigma2/python/Plugins/": "/usr/lib/enigma2/python/Plugins/",
                "${sysconfdir}/enigma2/": "/etc/enigma2/",
                "${datadir}/enigma2/": "/usr/share/enigma2/",
                "${bindir}": "/usr/bin",
                "${sbindir}": "/usr/sbin",
                "${libdir}": "/usr/lib",
                "${sysconfdir}": "/etc",
                "${localstatedir}": "/var",
                "${datadir}": "/usr/share",
            }
            
            for key, value in replacements.items():
                path = path.replace(key, value)
            
            return path
    
    # Fallback functions with better error handling
    def fileExists(path):
        try:
            return os.path.exists(ensure_str(path))
        except:
            return False
    
    def pathExists(path):
        try:
            return os.path.exists(ensure_str(path))
        except:
            return False
    
    def isMount(path):
        # Simple mount detection
        try:
            path_str = ensure_str(path)
            stat_info = os.stat(path_str)
            parent_stat = os.stat(os.path.dirname(path_str))
            return stat_info.st_dev != parent_stat.st_dev
        except:
            return False

# TRY IMPORTING OTHER PLUGIN MODULES FOR v2.1.0 INTEGRATION
try:
    from .UnitConversions import EnhancedUnitScaler
    UNIT_CONV_AVAILABLE = True
    debug_print("Directories: UnitConversions imported successfully")
except ImportError:
    debug_print("Directories: UnitConversions not available, using simple formatter")
    UNIT_CONV_AVAILABLE = False
    
    class EnhancedUnitScaler:
        def __init__(self):
            pass
        
        def format(self, value, unit_type='bytes'):
            """Simple size formatting"""
            if unit_type == 'bytes':
                for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                    if value < 1024.0:
                        if unit == 'B':
                            return f"{value:.0f} {unit}"
                        else:
                            return f"{value:.1f} {unit}"
                    value /= 1024.0
                return f"{value:.1f} PB"
            return str(value)

# TRY IMPORTING v2.1.0 NEW MODULES
try:
    from .SelectionManager import SelectionManager
    SELECTION_MANAGER_AVAILABLE = True
    debug_print("Directories: SelectionManager imported successfully")
except ImportError:
    debug_print("Directories: SelectionManager not available")
    SELECTION_MANAGER_AVAILABLE = False
    
    class SelectionManager:
        def __init__(self):
            pass
        
        def get_selected_paths(self, pane_id=None):
            return []
        
        def get_selection_count(self, pane_id=None):
            return 0

try:
    from .BatchOperations import BatchOperations
    BATCH_OPS_AVAILABLE = True
    debug_print("Directories: BatchOperations imported successfully")
except ImportError:
    debug_print("Directories: BatchOperations not available")
    BATCH_OPS_AVAILABLE = False
    
    class BatchOperations:
        def __init__(self):
            pass
        
        def batch_copy(self, source_paths, dest_dir, overwrite=False):
            return {'success': [], 'failed': []}
        
        def batch_move(self, source_paths, dest_dir, overwrite=False):
            return {'success': [], 'failed': []}

# Rest of your existing Directories.py code continues here...
# Your SmartDirectoryManager class should work as-is with these imports


class SmartDirectoryManager:
    """Enhanced directory operations with intelligent features"""
    
    # Extended scope definitions with Python 3 compatible paths
    SCOPES = {
        'PLUGINS': eEnv.resolve("${libdir}/enigma2/python/Plugins/"),
        'CONFIG': eEnv.resolve("${sysconfdir}/enigma2/"),
        'MEDIA': "/media/",
        'HDD': "/media/hdd/",
        'TIMESHIFT': "/media/hdd/timeshift/",
        'ROOT': "/home/root/",
        'TMP': "/tmp/",
        'USR': "/usr/",
        'VAR': "/var/",
        'ETC': "/etc/",
        'BIN': "/usr/bin/",
        'SBIN': "/usr/sbin/",
        'LIB': "/usr/lib/",
        'SHARE': "/usr/share/",
    }
    
    @staticmethod
    def getBestPath(scope, filename=""):
        """Get the best path for given scope, creating if needed"""
        path = SmartDirectoryManager.SCOPES.get(scope, "")
        if not path:
            debug_print(f"Unknown scope: {scope}")
            return None
        
        # Ensure path is string
        path = ensure_str(path)
        filename = ensure_str(filename) if filename else ""
        
        debug_print(f"getBestPath: scope={scope}, base_path={path}, filename={filename}")
        
        # Ensure directory exists
        if not os.path.exists(path):
            try:
                os.makedirs(path, exist_ok=True)
                debug_print(f"Created directory: {path}")
            except Exception as e:
                debug_print(f"Failed to create directory {path}: {e}")
                return None
        
        if filename:
            full_path = os.path.join(path, filename)
            debug_print(f"Returning full path: {full_path}")
            return full_path
        else:
            debug_print(f"Returning base path: {path}")
            return path
    
    @staticmethod
    def get_recommended_directory(purpose="source"):
        """Get recommended directory based on purpose"""
        debug_print(f"Getting recommended directory for: {purpose}")
        
        # Check common media locations first
        media_locations = [
            "/media/hdd/",
            "/media/usb/",
            "/media/sdb1/",
            "/media/sda1/",
            "/home/root/",
        ]
        
        for location in media_locations:
            if os.path.exists(location) and os.access(location, os.R_OK):
                debug_print(f"Found accessible location: {location}")
                return location
        
        # Fallback to home directory
        home = os.path.expanduser("~")
        if os.path.exists(home):
            debug_print(f"Using home directory: {home}")
            return home
        
        # Last resort
        debug_print("Using root directory as fallback")
        return "/"
    
    @staticmethod
    def shorten_path(path, max_length=50):
        """Shorten path for display"""
        if not path:
            return ""
        
        path_str = ensure_str(path)
        
        if len(path_str) <= max_length:
            return path_str
        
        # Try to keep the end of the path visible
        parts = path_str.split('/')
        if len(parts) > 3:
            return '.../' + '/'.join(parts[-3:])
        else:
            return path_str[:max_length-3] + '...'
    
    @staticmethod
    def smartCopy(src, dst, overwrite=False, preserve=True, 
                  progress_callback=None, verify=False):
        """
        Smart copy with progress tracking and verification
        
        Args:
            src: Source path
            dst: Destination path
            overwrite: Overwrite existing files
            preserve: Preserve file attributes
            progress_callback: Callback for progress updates
            verify: Verify copy with checksum
        """
        src_str = ensure_str(src)
        dst_str = ensure_str(dst)
        
        debug_print(f"smartCopy: {src_str} -> {dst_str}")
        
        if not os.path.exists(src_str):
            raise FileNotFoundError(f"Source not found: {src_str}")
        
        # Handle directory copy
        if os.path.isdir(src_str):
            return SmartDirectoryManager.copyDirectory(
                src_str, dst_str, overwrite, preserve, progress_callback, verify
            )
        else:
            return SmartDirectoryManager.copyFile(
                src_str, dst_str, overwrite, preserve, progress_callback, verify
            )
    
    @staticmethod
    def copyFile(src, dst, overwrite=False, preserve=True, 
                 progress_callback=None, verify=False):
        """Copy single file with enhanced features"""
        src_str = ensure_str(src)
        dst_str = ensure_str(dst)
        
        debug_print(f"copyFile: {src_str} -> {dst_str}")
        
        if os.path.exists(dst_str) and not overwrite:
            debug_print(f"Destination exists and overwrite=False: {dst_str}")
            return False
        
        # Calculate source checksum if verification requested
        src_checksum = None
        if verify:
            src_checksum = SmartDirectoryManager.calculateChecksum(src_str)
            debug_print(f"Source checksum: {src_checksum}")
        
        # Copy with chunking for progress tracking
        total_size = os.path.getsize(src_str)
        copied = 0
        chunk_size = 64 * 1024  # 64KB chunks
        
        debug_print(f"Copying {total_size} bytes in {chunk_size} byte chunks")
        
        try:
            # Ensure destination directory exists
            dst_dir = os.path.dirname(dst_str)
            if dst_dir and not os.path.exists(dst_dir):
                os.makedirs(dst_dir, exist_ok=True)
                debug_print(f"Created destination directory: {dst_dir}")
            
            with open(src_str, 'rb') as fsrc:
                with open(dst_str, 'wb') as fdst:
                    while True:
                        chunk = fsrc.read(chunk_size)
                        if not chunk:
                            break
                        fdst.write(chunk)
                        copied += len(chunk)
                        
                        # Update progress
                        if progress_callback and total_size > 0:
                            progress = (copied / total_size) * 100
                            progress_callback(progress, copied, total_size)
            
            debug_print(f"File copy completed: {copied} bytes")
            
            # Preserve attributes
            if preserve:
                try:
                    stat_src = os.stat(src_str)
                    os.chmod(dst_str, stat_src.st_mode)
                    os.utime(dst_str, (stat_src.st_atime, stat_src.st_mtime))
                    debug_print("File attributes preserved")
                except Exception as e:
                    debug_print(f"Warning: Could not preserve attributes: {e}")
            
            # Verify copy if requested
            if verify and src_checksum:
                dst_checksum = SmartDirectoryManager.calculateChecksum(dst_str)
                debug_print(f"Destination checksum: {dst_checksum}")
                if src_checksum != dst_checksum:
                    debug_print("Checksum verification failed")
                    os.remove(dst_str)  # Remove corrupted copy
                    raise ValueError("Checksum verification failed")
                else:
                    debug_print("Checksum verification passed")
            
            return True
            
        except Exception as e:
            debug_print(f"Error in copyFile: {e}")
            # Clean up partial copy
            if os.path.exists(dst_str):
                try:
                    os.remove(dst_str)
                    debug_print("Cleaned up partial file")
                except Exception as cleanup_error:
                    debug_print(f"Error cleaning up partial file: {cleanup_error}")
            raise e
    
    @staticmethod
    def copyDirectory(src, dst, overwrite=False, preserve=True, 
                      progress_callback=None, verify=False):
        """Copy entire directory tree"""
        src_str = ensure_str(src)
        dst_str = ensure_str(dst)
        
        debug_print(f"copyDirectory: {src_str} -> {dst_str}")
        
        if not os.path.exists(src_str):
            raise FileNotFoundError(f"Source directory not found: {src_str}")
        
        # Create destination directory
        os.makedirs(dst_str, exist_ok=True)
        debug_print(f"Created destination directory: {dst_str}")
        
        # Get total size for progress calculation
        total_size = SmartDirectoryManager.calculateDirectorySize(src_str)
        debug_print(f"Total directory size: {total_size} bytes")
        
        copied_size = 0
        
        # Walk through directory tree
        for root, dirs, files in os.walk(src_str):
            # Calculate relative path
            rel_path = os.path.relpath(root, src_str)
            dst_dir = os.path.join(dst_str, rel_path)
            
            # Create subdirectories
            os.makedirs(dst_dir, exist_ok=True)
            
            # Copy files
            for file in files:
                src_file = os.path.join(root, file)
                dst_file = os.path.join(dst_dir, file)
                
                # Skip if exists and not overwriting
                if os.path.exists(dst_file) and not overwrite:
                    debug_print(f"Skipping existing file: {dst_file}")
                    file_size = os.path.getsize(src_file)
                    copied_size += file_size  # Count as already copied
                    continue
                
                # Copy file
                debug_print(f"Copying: {src_file} -> {dst_file}")
                SmartDirectoryManager.copyFile(
                    src_file, dst_file, overwrite, preserve, None, verify
                )
                
                # Update progress
                file_size = os.path.getsize(src_file)
                copied_size += file_size
                if progress_callback and total_size > 0:
                    progress = (copied_size / total_size) * 100
                    progress_callback(progress, copied_size, total_size)
        
        debug_print("Directory copy completed")
        return True
    
    @staticmethod
    def smartMove(src, dst, overwrite=False, progress_callback=None):
        """
        Smart move with fallback to copy+delete
        """
        src_str = ensure_str(src)
        dst_str = ensure_str(dst)
        
        debug_print(f"smartMove: {src_str} -> {dst_str}")
        
        try:
            # Try direct rename first (fastest)
            debug_print("Attempting direct rename...")
            os.rename(src_str, dst_str)
            debug_print("Direct rename successful")
            return True
        except OSError as e:
            debug_print(f"Direct rename failed: {e}")
            # Different filesystem, use copy+delete
            try:
                debug_print("Attempting copy+delete...")
                SmartDirectoryManager.smartCopy(
                    src_str, dst_str, overwrite, True, progress_callback, True
                )
                
                # Verify copy before deleting source
                if SmartDirectoryManager.comparePaths(src_str, dst_str):
                    debug_print("Copy verified, deleting source...")
                    if os.path.isdir(src_str):
                        shutil.rmtree(src_str)
                    else:
                        os.remove(src_str)
                    debug_print("Source deleted, move completed")
                    return True
                else:
                    debug_print("Copy verification failed")
                    # Copy verification failed, clean up destination
                    if os.path.exists(dst_str):
                        if os.path.isdir(dst_str):
                            shutil.rmtree(dst_str)
                        else:
                            os.remove(dst_str)
                    return False
            except Exception as e:
                debug_print(f"Error in smartMove: {e}")
                raise e
    
    @staticmethod
    def calculateDirectorySize(path):
        """Calculate total size of directory"""
        path_str = ensure_str(path)
        total = 0
        
        debug_print(f"Calculating directory size: {path_str}")
        
        try:
            for dirpath, dirnames, filenames in os.walk(path_str):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    try:
                        if os.path.exists(fp):
                            size = os.path.getsize(fp)
                            total += size
                    except Exception as e:
                        debug_print(f"Error getting size of {fp}: {e}")
                        continue
        except Exception as e:
            debug_print(f"Error walking directory: {e}")
        
        debug_print(f"Directory size: {total} bytes")
        return total
    
    @staticmethod
    def calculateChecksum(filepath, algorithm='md5', chunk_size=8192):
        """Calculate file checksum"""
        filepath_str = ensure_str(filepath)
        
        if not os.path.exists(filepath_str):
            debug_print(f"File not found for checksum: {filepath_str}")
            return None
        
        debug_print(f"Calculating {algorithm} checksum for: {filepath_str}")
        
        try:
            hash_func = getattr(hashlib, algorithm)()
            
            with open(filepath_str, 'rb') as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    hash_func.update(chunk)
            
            checksum = hash_func.hexdigest()
            debug_print(f"Checksum: {checksum}")
            return checksum
            
        except Exception as e:
            debug_print(f"Error calculating checksum: {e}")
            return None
    
    @staticmethod
    def comparePaths(path1, path2, compare_content=True):
        """Compare two paths (files or directories)"""
        path1_str = ensure_str(path1)
        path2_str = ensure_str(path2)
        
        debug_print(f"Comparing paths: {path1_str} vs {path2_str}")
        
        if not (os.path.exists(path1_str) and os.path.exists(path2_str)):
            debug_print("One or both paths do not exist")
            return False
        
        # Check if both are files or both are directories
        if os.path.isfile(path1_str) != os.path.isfile(path2_str):
            debug_print("Path types differ (file vs directory)")
            return False
        
        if os.path.isfile(path1_str):
            # Compare file sizes first (fast)
            size1 = os.path.getsize(path1_str)
            size2 = os.path.getsize(path2_str)
            
            if size1 != size2:
                debug_print(f"File sizes differ: {size1} != {size2}")
                return False
            
            # Compare content if requested
            if compare_content:
                checksum1 = SmartDirectoryManager.calculateChecksum(path1_str)
                checksum2 = SmartDirectoryManager.calculateChecksum(path2_str)
                
                if checksum1 and checksum2 and checksum1 == checksum2:
                    debug_print("Files are identical")
                    return True
                else:
                    debug_print("Files differ (checksum mismatch)")
                    return False
            else:
                debug_print("Files have same size (content not compared)")
                return True
        else:
            # For directories, compare file lists and sizes
            files1 = SmartDirectoryManager.getFileList(path1_str)
            files2 = SmartDirectoryManager.getFileList(path2_str)
            
            debug_print(f"Directory 1 has {len(files1)} files")
            debug_print(f"Directory 2 has {len(files2)} files")
            
            if set(files1.keys()) != set(files2.keys()):
                debug_print("Directory file sets differ")
                return False
            
            # Compare file sizes
            for file in files1:
                if files1[file] != files2[file]:
                    debug_print(f"File size mismatch for {file}")
                    return False
            
            debug_print("Directories are identical")
            return True
    
    @staticmethod
    def getFileList(path, pattern="*"):
        """Get dictionary of files with their sizes"""
        path_str = ensure_str(path)
        file_dict = {}
        
        debug_print(f"Getting file list for: {path_str}, pattern: {pattern}")
        
        try:
            for root, dirs, files in os.walk(path_str):
                for file in files:
                    if fnmatch(file, pattern):
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, path_str)
                        try:
                            file_size = os.path.getsize(full_path)
                            file_dict[rel_path] = file_size
                        except Exception as e:
                            debug_print(f"Error getting size for {full_path}: {e}")
                            file_dict[rel_path] = 0
        except Exception as e:
            debug_print(f"Error walking directory {path_str}: {e}")
        
        debug_print(f"Found {len(file_dict)} files")
        return file_dict
    
    @staticmethod
    def findDuplicates(directory, algorithm='md5'):
        """Find duplicate files in directory"""
        directory_str = ensure_str(directory)
        hash_dict = {}
        duplicates = []
        
        debug_print(f"Finding duplicates in: {directory_str}")
        
        if not os.path.exists(directory_str):
            debug_print("Directory does not exist")
            return duplicates
        
        try:
            for root, dirs, files in os.walk(directory_str):
                for file in files:
                    filepath = os.path.join(root, file)
                    try:
                        file_hash = SmartDirectoryManager.calculateChecksum(
                            filepath, algorithm
                        )
                        
                        if file_hash:
                            if file_hash in hash_dict:
                                debug_print(f"Found duplicate: {filepath}")
                                duplicates.append((filepath, hash_dict[file_hash]))
                            else:
                                hash_dict[file_hash] = filepath
                    except Exception as e:
                        debug_print(f"Error processing {filepath}: {e}")
                        continue
        except Exception as e:
            debug_print(f"Error walking directory: {e}")
        
        debug_print(f"Found {len(duplicates)} duplicate pairs")
        return duplicates
    
    @staticmethod
    def getDiskSpace(path="/"):
        """Get disk space information"""
        path_str = ensure_str(path)
        
        debug_print(f"Getting disk space for: {path_str}")
        
        try:
            stat = os.statvfs(path_str)
            total = stat.f_blocks * stat.f_frsize
            free = stat.f_bavail * stat.f_frsize
            used = total - free
            percent_used = (used / total) * 100 if total > 0 else 0
            
            result = {
                'total': total,
                'used': used,
                'free': free,
                'percent_used': percent_used,
                'mountpoint': os.path.realpath(path_str)
            }
            
            debug_print(f"Disk space: {percent_used:.1f}% used")
            return result
            
        except Exception as e:
            debug_print(f"Error getting disk space: {e}")
            return None
    
    @staticmethod
    def getFileInfo(path):
        """Get detailed file information"""
        path_str = ensure_str(path)
        
        debug_print(f"Getting file info for: {path_str}")
        
        if not os.path.exists(path_str):
            debug_print("File does not exist")
            return None
        
        try:
            stat_info = os.stat(path_str)
            
            info = {
                'path': path_str,
                'name': os.path.basename(path_str),
                'size': stat_info.st_size,
                'is_dir': os.path.isdir(path_str),
                'is_file': os.path.isfile(path_str),
                'is_link': os.path.islink(path_str),
                'created': datetime.fromtimestamp(stat_info.st_ctime),
                'modified': datetime.fromtimestamp(stat_info.st_mtime),
                'accessed': datetime.fromtimestamp(stat_info.st_atime),
                'mode': oct(stat_info.st_mode),
                'owner': stat_info.st_uid,
                'group': stat_info.st_gid,
            }
            
            if os.path.islink(path_str):
                try:
                    info['target'] = os.readlink(path_str)
                except Exception as e:
                    info['target'] = f"Error: {e}"
            
            if os.path.isdir(path_str):
                try:
                    info['file_count'] = len(os.listdir(path_str))
                except Exception as e:
                    info['file_count'] = 0
                    info['access_error'] = str(e)
            
            debug_print(f"File info collected: {info['name']}, size: {info['size']}")
            return info
            
        except Exception as e:
            debug_print(f"Error getting file info: {e}")
            return None
    
    # BATCH OPERATIONS METHODS
    @staticmethod
    def batch_copy(source_paths, dest_dir, overwrite=False):
        """
        Copy multiple files/directories to destination
        
        Args:
            source_paths: List of source paths to copy
            dest_dir: Destination directory
            overwrite: Overwrite existing files
        
        Returns:
            Dictionary with operation results
        """
        results = {
            'success': [],
            'failed': [],
            'skipped': [],
            'total': len(source_paths)
        }
        
        dest_dir_str = ensure_str(dest_dir)
        
        if not os.path.exists(dest_dir_str):
            try:
                os.makedirs(dest_dir_str, exist_ok=True)
            except Exception as e:
                return {
                    'error': f"Cannot create destination directory: {str(e)}",
                    **results
                }
        
        for src_path in source_paths:
            try:
                src_path_str = ensure_str(src_path)
                if not os.path.exists(src_path_str):
                    results['failed'].append({
                        'path': src_path_str,
                        'error': 'Source does not exist'
                    })
                    continue
                
                # Get destination path
                src_name = os.path.basename(src_path_str)
                dest_path = os.path.join(dest_dir_str, src_name)
                
                # Check if destination exists
                if os.path.exists(dest_path) and not overwrite:
                    results['skipped'].append({
                        'path': src_path_str,
                        'reason': 'File already exists'
                    })
                    continue
                
                # Copy file or directory
                if os.path.isdir(src_path_str):
                    # Copy directory
                    if os.path.exists(dest_path):
                        shutil.rmtree(dest_path)
                    shutil.copytree(src_path_str, dest_path)
                else:
                    # Copy file
                    shutil.copy2(src_path_str, dest_path)
                
                results['success'].append({
                    'path': src_path_str,
                    'dest': dest_path
                })
                
            except Exception as e:
                results['failed'].append({
                    'path': src_path_str,
                    'error': str(e)
                })
        
        return results
    
    @staticmethod
    def batch_move(source_paths, dest_dir, overwrite=False):
        """
        Move multiple files/directories to destination
        
        Args:
            source_paths: List of source paths to move
            dest_dir: Destination directory
            overwrite: Overwrite existing files
        
        Returns:
            Dictionary with operation results
        """
        results = {
            'success': [],
            'failed': [],
            'skipped': [],
            'total': len(source_paths)
        }
        
        dest_dir_str = ensure_str(dest_dir)
        
        if not os.path.exists(dest_dir_str):
            try:
                os.makedirs(dest_dir_str, exist_ok=True)
            except Exception as e:
                return {
                    'error': f"Cannot create destination directory: {str(e)}",
                    **results
                }
        
        for src_path in source_paths:
            try:
                src_path_str = ensure_str(src_path)
                if not os.path.exists(src_path_str):
                    results['failed'].append({
                        'path': src_path_str,
                        'error': 'Source does not exist'
                    })
                    continue
                
                # Get destination path
                src_name = os.path.basename(src_path_str)
                dest_path = os.path.join(dest_dir_str, src_name)
                
                # Check if destination exists
                if os.path.exists(dest_path):
                    if overwrite:
                        # Remove existing file/directory
                        if os.path.isdir(dest_path):
                            shutil.rmtree(dest_path)
                        else:
                            os.remove(dest_path)
                    else:
                        results['skipped'].append({
                            'path': src_path_str,
                            'reason': 'File already exists'
                        })
                        continue
                
                # Move file or directory
                shutil.move(src_path_str, dest_path)
                
                results['success'].append({
                    'path': src_path_str,
                    'dest': dest_path
                })
                
            except Exception as e:
                results['failed'].append({
                    'path': src_path_str,
                    'error': str(e)
                })
        
        return results
    
    @staticmethod
    def batch_delete(paths, secure=False):
        """
        Delete multiple files/directories
        
        Args:
            paths: List of paths to delete
            secure: Use secure deletion (overwrites files before deleting)
        
        Returns:
            Dictionary with operation results
        """
        results = {
            'success': [],
            'failed': [],
            'total': len(paths)
        }
        
        for path in paths:
            try:
                path_str = ensure_str(path)
                if not os.path.exists(path_str):
                    results['failed'].append({
                        'path': path_str,
                        'error': 'Path does not exist'
                    })
                    continue
                
                # Secure deletion for files
                if secure and os.path.isfile(path_str):
                    # Overwrite file with random data before deleting
                    try:
                        file_size = os.path.getsize(path_str)
                        with open(path_str, 'wb') as f:
                            import random
                            # Write random data (3 passes)
                            for _ in range(3):
                                f.seek(0)
                                f.write(bytes([random.randint(0, 255) 
                                             for _ in range(file_size)]))
                                f.flush()
                    except:
                        pass  # If secure delete fails, try normal delete
                
                # Delete file or directory
                if os.path.isdir(path_str):
                    shutil.rmtree(path_str)
                else:
                    os.remove(path_str)
                
                results['success'].append({
                    'path': path_str
                })
                
            except Exception as e:
                results['failed'].append({
                    'path': path_str,
                    'error': str(e)
                })
        
        return results
    
    @staticmethod
    def batch_rename(rename_list):
        """
        Rename multiple files
        
        Args:
            rename_list: List of dictionaries with 'old_path' and 'new_name'
        
        Returns:
            Dictionary with operation results
        """
        results = {
            'success': [],
            'failed': [],
            'total': len(rename_list)
        }
        
        for item in rename_list:
            try:
                old_path = item.get('old_path')
                new_name = item.get('new_name')
                
                if not old_path or not new_name:
                    results['failed'].append({
                        'old_path': old_path,
                        'error': 'Missing old_path or new_name'
                    })
                    continue
                
                old_path_str = ensure_str(old_path)
                new_name_str = ensure_str(new_name)
                
                if not os.path.exists(old_path_str):
                    results['failed'].append({
                        'old_path': old_path_str,
                        'error': 'Source does not exist'
                    })
                    continue
                
                # Get directory and construct new path
                old_dir = os.path.dirname(old_path_str)
                new_path = os.path.join(old_dir, new_name_str)
                
                # Check if new name already exists
                if os.path.exists(new_path):
                    results['failed'].append({
                        'old_path': old_path_str,
                        'new_name': new_name_str,
                        'error': 'New name already exists'
                    })
                    continue
                
                # Rename the file/directory
                os.rename(old_path_str, new_path)
                
                results['success'].append({
                    'old_path': old_path_str,
                    'new_path': new_path
                })
                
            except Exception as e:
                results['failed'].append({
                    'old_path': item.get('old_path'),
                    'error': str(e)
                })
        
        return results
    
    @staticmethod
    def batch_chmod(paths, mode, recursive=False):
        """
        Change permissions for multiple files/directories
        
        Args:
            paths: List of paths to modify
            mode: Permission mode (e.g., 0o755)
            recursive: Apply recursively to directories
        
        Returns:
            Dictionary with operation results
        """
        results = {
            'success': [],
            'failed': [],
            'total': len(paths)
        }
        
        for path in paths:
            try:
                path_str = ensure_str(path)
                if not os.path.exists(path_str):
                    results['failed'].append({
                        'path': path_str,
                        'error': 'Path does not exist'
                    })
                    continue
                
                # Change permissions
                os.chmod(path_str, mode)
                results['success'].append({'path': path_str})
                
                # Apply recursively if requested and it's a directory
                if recursive and os.path.isdir(path_str):
                    for root, dirs, files in os.walk(path_str):
                        for item in dirs + files:
                            item_path = os.path.join(root, item)
                            try:
                                os.chmod(item_path, mode)
                            except Exception as e:
                                results['failed'].append({
                                    'path': item_path,
                                    'error': f"Recursive chmod failed: {str(e)}"
                                })
                
            except Exception as e:
                results['failed'].append({
                    'path': path_str,
                    'error': str(e)
                })
        
        return results
    
    @staticmethod
    def batch_compress(source_paths, archive_path, format='zip'):
        """
        Compress multiple files/directories into an archive
        
        Args:
            source_paths: List of paths to compress
            archive_path: Path for the output archive
            format: Archive format ('zip', 'tar', 'gztar', 'bztar', 'xztar')
        
        Returns:
            Dictionary with operation results
        """
        try:
            archive_path_str = ensure_str(archive_path)
            
            # Create the archive
            if len(source_paths) == 1:
                # Single file/directory
                root_dir = os.path.dirname(source_paths[0])
                base_dir = os.path.basename(source_paths[0])
                shutil.make_archive(
                    base_name=os.path.splitext(archive_path_str)[0],
                    format=format,
                    root_dir=root_dir,
                    base_dir=base_dir
                )
            else:
                # Multiple files - use custom logic
                if format == 'zip':
                    with zipfile.ZipFile(archive_path_str, 'w', zipfile.ZIP_DEFLATED) as zf:
                        for src_path in source_paths:
                            src_path_str = ensure_str(src_path)
                            if os.path.isdir(src_path_str):
                                # Add directory recursively
                                for root, dirs, files in os.walk(src_path_str):
                                    for file in files:
                                        file_path = os.path.join(root, file)
                                        arcname = os.path.relpath(file_path, 
                                                                os.path.dirname(src_path_str))
                                        zf.write(file_path, arcname)
                            else:
                                # Add single file
                                arcname = os.path.basename(src_path_str)
                                zf.write(src_path_str, arcname)
                else:
                    # For tar formats, use shutil with temporary directory
                    import tempfile
                    with tempfile.TemporaryDirectory() as tmpdir:
                        # Copy all files to temp directory
                        for src_path in source_paths:
                            src_path_str = ensure_str(src_path)
                            dest = os.path.join(tmpdir, os.path.basename(src_path_str))
                            if os.path.isdir(src_path_str):
                                shutil.copytree(src_path_str, dest)
                            else:
                                shutil.copy2(src_path_str, dest)
                        
                        # Create archive from temp directory
                        shutil.make_archive(
                            base_name=os.path.splitext(archive_path_str)[0],
                            format=format,
                            root_dir=tmpdir
                        )
            
            return {
                'success': True,
                'archive_path': archive_path_str,
                'format': format,
                'compressed_items': len(source_paths)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'archive_path': archive_path_str if 'archive_path_str' in locals() else archive_path
            }
    
    @staticmethod
    def get_batch_summary(paths):
        """
        Get summary information about multiple files
        
        Args:
            paths: List of paths to analyze
        
        Returns:
            Dictionary with summary information
        """
        summary = {
            'total_count': len(paths),
            'file_count': 0,
            'dir_count': 0,
            'total_size': 0,
            'oldest': None,
            'newest': None,
            'extensions': {},
            'largest_file': None,
            'largest_size': 0
        }
        
        for path in paths:
            try:
                path_str = ensure_str(path)
                if not os.path.exists(path_str):
                    continue
                
                if os.path.isdir(path_str):
                    summary['dir_count'] += 1
                    # Calculate directory size
                    dir_size = SmartDirectoryManager.calculateDirectorySize(path_str)
                    summary['total_size'] += dir_size
                else:
                    summary['file_count'] += 1
                    file_size = os.path.getsize(path_str)
                    summary['total_size'] += file_size
                    
                    # Track largest file
                    if file_size > summary['largest_size']:
                        summary['largest_size'] = file_size
                        summary['largest_file'] = path_str
                    
                    # Track file extension
                    _, ext = os.path.splitext(path_str)
                    if ext:
                        ext = ext.lower()
                        summary['extensions'][ext] = summary['extensions'].get(ext, 0) + 1
                
                # Track modification times
                stat_info = os.stat(path_str)
                mtime = stat_info.st_mtime
                
                if summary['oldest'] is None or mtime < summary['oldest']:
                    summary['oldest'] = mtime
                if summary['newest'] is None or mtime > summary['newest']:
                    summary['newest'] = mtime
                    
            except Exception:
                continue
        
        # Convert timestamps to readable format
        if summary['oldest']:
            from datetime import datetime
            summary['oldest_date'] = datetime.fromtimestamp(summary['oldest']).strftime('%Y-%m-%d %H:%M:%S')
            summary['newest_date'] = datetime.fromtimestamp(summary['newest']).strftime('%Y-%m-%d %H:%M:%S')
        
        # Format size
        size = summary['total_size']
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                summary['formatted_size'] = f"{size:.2f} {unit}"
                break
            size /= 1024.0
        
        # Format largest size
        largest = summary['largest_size']
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if largest < 1024.0:
                summary['formatted_largest'] = f"{largest:.2f} {unit}"
                break
            largest /= 1024.0
        
        return summary


# Backward compatibility functions
def resolveFilename(scope, base="", path_prefix=None):
    """Compatibility wrapper"""
    return SmartDirectoryManager.getBestPath(scope, base)

def copyfile(src, dst):
    """Simple file copy wrapper"""
    return SmartDirectoryManager.smartCopy(src, dst, False, True)

def copytree(src, dst, symlinks=False):
    """Directory copy wrapper"""
    return SmartDirectoryManager.copyDirectory(src, dst, False, True)

def moveFiles(fileList):
    """Move files wrapper"""
    results = []
    for src, dst in fileList:
        try:
            success = SmartDirectoryManager.smartMove(src, dst)
            results.append((src, dst, success))
        except Exception as e:
            results.append((src, dst, False, str(e)))
    return results


# Test function
if __name__ == "__main__":
    print("SmartDirectoryManager Test")
    print("=" * 60)
    
    # Test path functions
    print("Testing path functions:")
    test_path = SmartDirectoryManager.getBestPath("TMP", "test.txt")
    print(f"  getBestPath(TMP, test.txt): {test_path}")
    
    recommended = SmartDirectoryManager.get_recommended_directory()
    print(f"  get_recommended_directory(): {recommended}")
    
    shortened = SmartDirectoryManager.shorten_path("/very/long/path/to/some/file.txt", 30)
    print(f"  shorten_path(): {shortened}")
    
    # Test file info
    print("\nTesting file info (current directory):")
    file_info = SmartDirectoryManager.getFileInfo(".")
    if file_info:
        print(f"  Name: {file_info['name']}")
        print(f"  Size: {file_info['size']} bytes")
        print(f"  Is dir: {file_info['is_dir']}")
    
    # Test disk space
    print("\nTesting disk space:")
    disk_space = SmartDirectoryManager.getDiskSpace("/tmp")
    if disk_space:
        print(f"  Total: {disk_space['total']:,} bytes")
        print(f"  Used: {disk_space['used']:,} bytes")
        print(f"  Free: {disk_space['free']:,} bytes")
        print(f"  Used %: {disk_space['percent_used']:.1f}%")
    
    # Test batch operations
    print("\nTesting batch operations:")
    test_paths = ["."]
    summary = SmartDirectoryManager.get_batch_summary(test_paths)
    print(f"  Batch summary: {summary['total_count']} items, {summary['formatted_size']}")
    
    print("\nAll tests completed!")
    print("=" * 60)