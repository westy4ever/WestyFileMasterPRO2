#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division, unicode_literals

import os
import shutil
import stat
import time
import hashlib
import zipfile
import tarfile
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Union

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


class BatchOperations:
    """Enhanced batch file operations with progress tracking"""
    
    def __init__(self):
        self.progress_callback = None
        self.cancel_requested = False
    
    def set_progress_callback(self, callback):
        """Set callback for progress updates"""
        self.progress_callback = callback
    
    def request_cancel(self):
        """Request cancellation of current operation"""
        self.cancel_requested = True
    
    def reset_cancel(self):
        """Reset cancellation flag"""
        self.cancel_requested = False
    
    def _check_cancel(self):
        """Check if cancellation was requested"""
        if self.cancel_requested:
            raise OperationCancelled("Operation cancelled by user")
    
    def _update_progress(self, current, total, message=""):
        """Update progress if callback is set"""
        if self.progress_callback:
            percent = (current / total * 100) if total > 0 else 0
            self.progress_callback(percent, current, total, message)
    
    def batch_copy(self, source_paths: List[str], dest_dir: str, 
                   overwrite: bool = False, preserve_attrs: bool = True) -> Dict[str, Any]:
        """
        Copy multiple files/directories to destination
        
        Args:
            source_paths: List of source paths to copy
            dest_dir: Destination directory
            overwrite: Overwrite existing files
            preserve_attrs: Preserve file attributes
        
        Returns:
            Dictionary with operation results
        """
        self.reset_cancel()
        results = {
            'success': [],
            'failed': [],
            'skipped': [],
            'total': len(source_paths),
            'bytes_copied': 0
        }
        
        dest_dir_str = ensure_str(dest_dir)
        
        # Ensure destination exists
        if not os.path.exists(dest_dir_str):
            try:
                os.makedirs(dest_dir_str, exist_ok=True)
            except Exception as e:
                return {
                    'error': f"Cannot create destination directory: {str(e)}",
                    **results
                }
        
        for i, src_path in enumerate(source_paths):
            self._check_cancel()
            src_path_str = ensure_str(src_path)
            
            try:
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
                
                # Update progress
                self._update_progress(i + 1, len(source_paths), f"Copying {src_name}")
                
                # Copy file or directory
                if os.path.isdir(src_path_str):
                    # Copy directory
                    bytes_copied = self._copy_directory(src_path_str, dest_path, 
                                                       overwrite, preserve_attrs)
                    results['bytes_copied'] += bytes_copied
                else:
                    # Copy file
                    bytes_copied = self._copy_file(src_path_str, dest_path, 
                                                  overwrite, preserve_attrs)
                    results['bytes_copied'] += bytes_copied
                
                results['success'].append({
                    'path': src_path_str,
                    'dest': dest_path,
                    'bytes': bytes_copied
                })
                
            except Exception as e:
                results['failed'].append({
                    'path': src_path_str,
                    'error': str(e)
                })
        
        return results
    
    def _copy_file(self, src: str, dst: str, overwrite: bool, preserve_attrs: bool) -> int:
        """Copy single file with attributes"""
        chunk_size = 64 * 1024  # 64KB chunks
        bytes_copied = 0
        
        # Remove existing file if overwriting
        if os.path.exists(dst) and overwrite:
            os.remove(dst)
        
        # Ensure parent directory exists
        dst_dir = os.path.dirname(dst)
        if dst_dir and not os.path.exists(dst_dir):
            os.makedirs(dst_dir, exist_ok=True)
        
        # Copy file contents
        with open(src, 'rb') as fsrc:
            with open(dst, 'wb') as fdst:
                while True:
                    self._check_cancel()
                    chunk = fsrc.read(chunk_size)
                    if not chunk:
                        break
                    fdst.write(chunk)
                    bytes_copied += len(chunk)
        
        # Preserve attributes if requested
        if preserve_attrs:
            try:
                src_stat = os.stat(src)
                os.chmod(dst, src_stat.st_mode)
                os.utime(dst, (src_stat.st_atime, src_stat.st_mtime))
            except:
                pass  # Ignore errors preserving attributes
        
        return bytes_copied
    
    def _copy_directory(self, src: str, dst: str, overwrite: bool, preserve_attrs: bool) -> int:
        """Copy directory recursively"""
        bytes_copied = 0
        
        # Create destination directory
        os.makedirs(dst, exist_ok=True)
        
        # Copy contents
        for item in os.listdir(src):
            self._check_cancel()
            src_item = os.path.join(src, item)
            dst_item = os.path.join(dst, item)
            
            if os.path.isdir(src_item):
                bytes_copied += self._copy_directory(src_item, dst_item, overwrite, preserve_attrs)
            else:
                bytes_copied += self._copy_file(src_item, dst_item, overwrite, preserve_attrs)
        
        # Preserve directory attributes
        if preserve_attrs:
            try:
                src_stat = os.stat(src)
                os.chmod(dst, src_stat.st_mode)
                os.utime(dst, (src_stat.st_atime, src_stat.st_mtime))
            except:
                pass
        
        return bytes_copied
    
    def batch_move(self, source_paths: List[str], dest_dir: str, 
                   overwrite: bool = False) -> Dict[str, Any]:
        """
        Move multiple files/directories to destination
        
        Args:
            source_paths: List of source paths to move
            dest_dir: Destination directory
            overwrite: Overwrite existing files
        
        Returns:
            Dictionary with operation results
        """
        self.reset_cancel()
        results = {
            'success': [],
            'failed': [],
            'skipped': [],
            'total': len(source_paths)
        }
        
        dest_dir_str = ensure_str(dest_dir)
        
        # Ensure destination exists
        if not os.path.exists(dest_dir_str):
            try:
                os.makedirs(dest_dir_str, exist_ok=True)
            except Exception as e:
                return {
                    'error': f"Cannot create destination directory: {str(e)}",
                    **results
                }
        
        for i, src_path in enumerate(source_paths):
            self._check_cancel()
            src_path_str = ensure_str(src_path)
            
            try:
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
                
                # Update progress
                self._update_progress(i + 1, len(source_paths), f"Moving {src_name}")
                
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
    
    def batch_delete(self, paths: List[str], secure: bool = False, 
                     passes: int = 3) -> Dict[str, Any]:
        """
        Delete multiple files/directories
        
        Args:
            paths: List of paths to delete
            secure: Use secure deletion (overwrites files)
            passes: Number of overwrite passes for secure deletion
        
        Returns:
            Dictionary with operation results
        """
        self.reset_cancel()
        results = {
            'success': [],
            'failed': [],
            'total': len(paths),
            'bytes_freed': 0
        }
        
        for i, path in enumerate(paths):
            self._check_cancel()
            path_str = ensure_str(path)
            
            try:
                if not os.path.exists(path_str):
                    results['failed'].append({
                        'path': path_str,
                        'error': 'Path does not exist'
                    })
                    continue
                
                # Get file/directory size before deletion
                size = 0
                if os.path.isfile(path_str):
                    size = os.path.getsize(path_str)
                elif os.path.isdir(path_str):
                    size = self._get_directory_size(path_str)
                
                # Update progress
                self._update_progress(i + 1, len(paths), f"Deleting {os.path.basename(path_str)}")
                
                # Secure deletion for files
                if secure and os.path.isfile(path_str):
                    self._secure_delete_file(path_str, passes)
                else:
                    # Regular deletion
                    if os.path.isdir(path_str):
                        shutil.rmtree(path_str)
                    else:
                        os.remove(path_str)
                
                results['success'].append({
                    'path': path_str,
                    'bytes_freed': size
                })
                results['bytes_freed'] += size
                
            except Exception as e:
                results['failed'].append({
                    'path': path_str,
                    'error': str(e)
                })
        
        return results
    
    def _secure_delete_file(self, filepath: str, passes: int = 3):
        """Securely delete a file by overwriting it"""
        file_size = os.path.getsize(filepath)
        
        # Open file for binary writing
        with open(filepath, 'wb') as f:
            for pass_num in range(passes):
                self._check_cancel()
                
                # Generate random data for this pass
                import random
                f.seek(0)
                
                # Write random data in chunks
                chunk_size = 64 * 1024
                remaining = file_size
                
                while remaining > 0:
                    chunk = bytes([random.randint(0, 255) 
                                 for _ in range(min(chunk_size, remaining))])
                    f.write(chunk)
                    remaining -= len(chunk)
                
                f.flush()
        
        # Final deletion
        os.remove(filepath)
    
    def _get_directory_size(self, path: str) -> int:
        """Calculate total size of directory"""
        total = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if os.path.exists(fp):
                    total += os.path.getsize(fp)
        return total
    
    def batch_rename(self, rename_list: List[Dict[str, str]], 
                     pattern: Optional[str] = None) -> Dict[str, Any]:
        """
        Rename multiple files with pattern support
        
        Args:
            rename_list: List of dicts with 'old_path' and 'new_name'
            pattern: Optional pattern for batch renaming
                     e.g., "file_{n:03d}.txt" or "prefix_{name}"
        
        Returns:
            Dictionary with operation results
        """
        self.reset_cancel()
        results = {
            'success': [],
            'failed': [],
            'total': len(rename_list)
        }
        
        for i, item in enumerate(rename_list):
            self._check_cancel()
            old_path = item.get('old_path')
            new_name = item.get('new_name')
            
            if not old_path or not new_name:
                results['failed'].append({
                    'old_path': old_path,
                    'error': 'Missing old_path or new_name'
                })
                continue
            
            old_path_str = ensure_str(old_path)
            
            try:
                if not os.path.exists(old_path_str):
                    results['failed'].append({
                        'old_path': old_path_str,
                        'error': 'Source does not exist'
                    })
                    continue
                
                # Generate new name from pattern if provided
                if pattern:
                    new_name = self._apply_pattern(old_path_str, pattern, i)
                
                # Get directory and construct new path
                old_dir = os.path.dirname(old_path_str)
                new_path = os.path.join(old_dir, ensure_str(new_name))
                
                # Check if new name already exists
                if os.path.exists(new_path):
                    results['failed'].append({
                        'old_path': old_path_str,
                        'new_name': new_name,
                        'error': 'New name already exists'
                    })
                    continue
                
                # Update progress
                self._update_progress(i + 1, len(rename_list), 
                                    f"Renaming {os.path.basename(old_path_str)}")
                
                # Rename the file/directory
                os.rename(old_path_str, new_path)
                
                results['success'].append({
                    'old_path': old_path_str,
                    'new_path': new_path
                })
                
            except Exception as e:
                results['failed'].append({
                    'old_path': old_path_str,
                    'error': str(e)
                })
        
        return results
    
    def _apply_pattern(self, old_path: str, pattern: str, index: int) -> str:
        """Apply pattern to generate new filename"""
        old_name = os.path.basename(old_path)
        name_no_ext, ext = os.path.splitext(old_name)
        
        # Replace placeholders in pattern
        result = pattern
        result = result.replace('{name}', name_no_ext)
        result = result.replace('{ext}', ext[1:] if ext else '')
        result = result.replace('{fullname}', old_name)
        result = result.replace('{n}', str(index + 1))
        result = result.replace('{n:03d}', f"{index + 1:03d}")
        
        # Date placeholders
        from datetime import datetime
        result = result.replace('{date}', datetime.now().strftime('%Y%m%d'))
        result = result.replace('{time}', datetime.now().strftime('%H%M%S'))
        
        return result
    
    def batch_chmod(self, paths: List[str], mode: int, 
                    recursive: bool = False) -> Dict[str, Any]:
        """
        Change permissions for multiple files/directories
        
        Args:
            paths: List of paths to modify
            mode: Permission mode (e.g., 0o755)
            recursive: Apply recursively to directories
        
        Returns:
            Dictionary with operation results
        """
        self.reset_cancel()
        results = {
            'success': [],
            'failed': [],
            'total': len(paths)
        }
        
        for i, path in enumerate(paths):
            self._check_cancel()
            path_str = ensure_str(path)
            
            try:
                if not os.path.exists(path_str):
                    results['failed'].append({
                        'path': path_str,
                        'error': 'Path does not exist'
                    })
                    continue
                
                # Update progress
                self._update_progress(i + 1, len(paths), 
                                    f"Changing permissions for {os.path.basename(path_str)}")
                
                # Change permissions
                os.chmod(path_str, mode)
                results['success'].append({'path': path_str})
                
                # Apply recursively if requested and it's a directory
                if recursive and os.path.isdir(path_str):
                    self._chmod_recursive(path_str, mode)
                
            except Exception as e:
                results['failed'].append({
                    'path': path_str,
                    'error': str(e)
                })
        
        return results
    
    def _chmod_recursive(self, path: str, mode: int):
        """Change permissions recursively"""
        for root, dirs, files in os.walk(path):
            for item in dirs + files:
                item_path = os.path.join(root, item)
                try:
                    os.chmod(item_path, mode)
                except:
                    pass  # Ignore errors on individual items
    
    def batch_compress(self, source_paths: List[str], archive_path: str, 
                       format: str = 'zip', compression_level: int = 6) -> Dict[str, Any]:
        """
        Compress multiple files/directories into an archive
        
        Args:
            source_paths: List of paths to compress
            archive_path: Path for the output archive
            format: Archive format ('zip', 'tar', 'gztar', 'bztar', 'xztar')
            compression_level: Compression level (1-9)
        
        Returns:
            Dictionary with operation results
        """
        self.reset_cancel()
        results = {
            'success': False,
            'archive_path': archive_path,
            'format': format,
            'files_added': 0,
            'total_size': 0
        }
        
        try:
            archive_path_str = ensure_str(archive_path)
            
            # Update progress
            self._update_progress(0, 100, "Starting compression...")
            
            if format == 'zip':
                with zipfile.ZipFile(archive_path_str, 'w', 
                                   zipfile.ZIP_DEFLATED, compresslevel=compression_level) as zf:
                    for i, src_path in enumerate(source_paths):
                        self._check_cancel()
                        src_path_str = ensure_str(src_path)
                        
                        if not os.path.exists(src_path_str):
                            continue
                        
                        # Update progress
                        progress = (i / len(source_paths)) * 100
                        self._update_progress(progress, 100, 
                                            f"Adding {os.path.basename(src_path_str)}")
                        
                        if os.path.isdir(src_path_str):
                            # Add directory recursively
                            for root, dirs, files in os.walk(src_path_str):
                                for file in files:
                                    file_path = os.path.join(root, file)
                                    arcname = os.path.relpath(file_path, 
                                                            os.path.dirname(src_path_str))
                                    zf.write(file_path, arcname)
                                    results['files_added'] += 1
                                    results['total_size'] += os.path.getsize(file_path)
                        else:
                            # Add single file
                            arcname = os.path.basename(src_path_str)
                            zf.write(src_path_str, arcname)
                            results['files_added'] += 1
                            results['total_size'] += os.path.getsize(src_path_str)
            
            elif format in ['tar', 'gztar', 'bztar', 'xztar']:
                # Determine compression for tar
                mode_map = {
                    'tar': 'w',
                    'gztar': 'w:gz',
                    'bztar': 'w:bz2',
                    'xztar': 'w:xz'
                }
                mode = mode_map.get(format, 'w')
                
                with tarfile.open(archive_path_str, mode) as tf:
                    for i, src_path in enumerate(source_paths):
                        self._check_cancel()
                        src_path_str = ensure_str(src_path)
                        
                        if not os.path.exists(src_path_str):
                            continue
                        
                        # Update progress
                        progress = (i / len(source_paths)) * 100
                        self._update_progress(progress, 100, 
                                            f"Adding {os.path.basename(src_path_str)}")
                        
                        tf.add(src_path_str, 
                              arcname=os.path.basename(src_path_str))
                        results['files_added'] += 1
                        
                        if os.path.isfile(src_path_str):
                            results['total_size'] += os.path.getsize(src_path_str)
            
            results['success'] = True
            self._update_progress(100, 100, "Compression completed")
            
        except Exception as e:
            results['success'] = False
            results['error'] = str(e)
        
        return results
    
    def get_batch_summary(self, paths: List[str]) -> Dict[str, Any]:
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
                    dir_size = self._get_directory_size(path_str)
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
    
    def get_batch_summary_formatted(self, paths: List[str]) -> str:
        """Get formatted summary string for UI display"""
        summary = self.get_batch_summary(paths)
        
        lines = [
            f"Total: {summary['total_count']} items",
            f"Files: {summary['file_count']}",
            f"Directories: {summary['dir_count']}",
            f"Total size: {summary['formatted_size']}",
        ]
        
        if summary['largest_file']:
            lines.append(f"Largest: {os.path.basename(summary['largest_file'])} ({summary['formatted_largest']})")
        
        if summary.get('oldest_date'):
            lines.append(f"Oldest: {summary['oldest_date']}")
            lines.append(f"Newest: {summary['newest_date']}")
        
        return "\n".join(lines)
    
    def batch_operation_status(self, results: Dict[str, Any]) -> str:
        """Get status message from batch operation results"""
        success = len(results.get('success', []))
        failed = len(results.get('failed', []))
        skipped = len(results.get('skipped', []))
        total = results.get('total', 0)
        
        if total == 0:
            return "No files processed"
        
        if success == total:
            return f"Successfully processed {success} items"
        elif failed == total:
            return f"Failed to process {failed} items"
        else:
            msg = f"Processed {success} of {total} items"
            if failed > 0:
                msg += f", {failed} failed"
            if skipped > 0:
                msg += f", {skipped} skipped"
            return msg


class OperationCancelled(Exception):
    """Exception raised when operation is cancelled"""
    pass


# Test function
if __name__ == "__main__":
    print("BatchOperations Test")
    print("=" * 60)
    
    # Create batch operations instance
    ops = BatchOperations()
    
    # Test summary
    test_paths = ["./", __file__]
    summary = ops.get_batch_summary(test_paths)
    
    print("Batch Summary Test:")
    print(f"  Total items: {summary['total_count']}")
    print(f"  Files: {summary['file_count']}")
    print(f"  Directories: {summary['dir_count']}")
    print(f"  Total size: {summary['formatted_size']}")
    print(f"  Largest file: {summary['largest_file']}")
    print(f"  Largest size: {summary['formatted_largest']}")
    
    # Test rename pattern
    pattern_result = ops._apply_pattern("/tmp/test.txt", "new_{name}_{n:03d}{ext}", 5)
    print(f"Rename pattern test: {pattern_result}")
    
    # Test formatted summary
    formatted = ops.get_batch_summary_formatted(test_paths)
    print(f"Formatted summary:\n{formatted}")
    
    print("=" * 60)