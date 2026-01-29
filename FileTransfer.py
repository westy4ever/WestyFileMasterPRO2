#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division, unicode_literals

import os
import sys
import time
import threading
import shutil
import stat
import queue
from datetime import datetime

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
    debug_print(f"FileTransfer: Imported plugin utilities v{PLUGIN_VERSION}")
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
    
    PLUGIN_NAME = "Westy FileMaster PRO"
    PLUGIN_VERSION = "2.1.0"  # UPDATED to 2.1.0

# Import EnhancedUnitScaler for speed formatting
try:
    from .UnitConversions import EnhancedUnitScaler
    UNIT_CONV_AVAILABLE = True
    debug_print("FileTransfer: UnitConversions imported successfully")
except ImportError:
    UNIT_CONV_AVAILABLE = False
    debug_print("FileTransfer: UnitConversions module not available")
    
    class EnhancedUnitScaler:
        def __init__(self):
            pass
        
        def format(self, value, unit_type='bytes'):
            # Simple fallback formatting
            if value >= 1024**3:  # GB
                return f"{value/(1024**3):.1f} GB"
            elif value >= 1024**2:  # MB
                return f"{value/(1024**2):.1f} MB"
            elif value >= 1024:  # KB
                return f"{value/1024:.1f} KB"
            else:
                return f"{value:.0f} B"

# OpenATV/Enigma2 imports - ENHANCED with more modules
try:
    from Components.Task import Task, Job, job_manager
    from enigma import eTimer
    
    # Try to import additional useful modules
    try:
        from Components.Task import PythonTask
        PYTHONTASK_AVAILABLE = True
    except ImportError:
        PYTHONTASK_AVAILABLE = False
    
    ENIGMA2_AVAILABLE = True
    debug_print(f"FileTransfer: Enigma2 imports successful v{PLUGIN_VERSION}")
except ImportError as e:
    debug_print(f"FileTransfer: Error importing Enigma2 modules: {e}")
    ENIGMA2_AVAILABLE = False
    
    # Create dummy classes for testing
    class Job:
        def __init__(self, title):
            self.title = title
            self.callbacks = []
            self.tasks = []
        
        def addCallback(self, callback):
            self.callbacks.append(callback)
        
        def addTask(self, task):
            self.tasks.append(task)
            task.job = self
        
        def start(self):
            debug_print(f"Would start job: {self.title}")
    
    class Task:
        def __init__(self, job, name):
            self.job = job
            self.name = name
            self.progress = 0
        
        def setProgress(self, progress):
            self.progress = progress
            debug_print(f"Task progress: {progress}%")
        
        def setCmdline(self, cmdline):
            self.cmdline = cmdline
        
        def prepare(self):
            debug_print("Task prepare called")
        
        def afterRun(self):
            debug_print("Task afterRun called")
    
    class job_manager:
        @staticmethod
        def AddJob(job):
            debug_print(f"Would add job to manager: {job.title}")
            return job
        
        @staticmethod
        def active_jobs():
            return []
    
    class eTimer:
        def __init__(self):
            self.callbacks = []
        
        def start(self, interval):
            debug_print(f"Timer started with interval {interval}")
        
        def stop(self):
            debug_print("Timer stopped")
        
        def callback(self):
            return self.callbacks
        
        def append(self, func):
            self.callbacks.append(func)

# TRY IMPORTING v2.1.0 NEW MODULES FOR INTEGRATION
try:
    from .BatchOperations import BatchOperations
    BATCH_OPS_AVAILABLE = True
    debug_print("FileTransfer: BatchOperations imported successfully")
except ImportError:
    BATCH_OPS_AVAILABLE = False
    debug_print("FileTransfer: BatchOperations not available")
    
    class BatchOperations:
        def __init__(self):
            pass
        
        def batch_copy(self, source_paths, dest_dir, overwrite=False):
            return {'success': [], 'failed': []}
        
        def batch_move(self, source_paths, dest_dir, overwrite=False):
            return {'success': [], 'failed': []}

try:
    from .SelectionManager import SelectionManager
    SELECTION_MANAGER_AVAILABLE = True
    debug_print("FileTransfer: SelectionManager imported successfully")
except ImportError:
    SELECTION_MANAGER_AVAILABLE = False
    debug_print("FileTransfer: SelectionManager not available")
    
    class SelectionManager:
        def __init__(self):
            pass
        
        def get_selected_paths(self, pane_id=None):
            return []

class WestyFileTransferJob(Job):
    """Enhanced file transfer job with speed calculation and queue support"""
    
    def __init__(self, src_file=None, dst_file=None, src_isDir=False, do_copy=True, title="File Transfer",
                 show_speed=True, preserve_attributes=True, callback=None):
        """
        Initialize file transfer job with queue support
        
        Args:
            src_file: Source file path (optional for queue mode)
            dst_file: Destination file path (optional for queue mode)
            src_isDir: Whether source is a directory
            do_copy: True for copy, False for move
            title: Job title
            show_speed: Show transfer speed
            preserve_attributes: Preserve file attributes
            callback: Completion callback
        """
        Job.__init__(self, title)
        
        # Queue support
        self.transfer_queue = []  # List of transfer operations
        self.current_transfer = None
        self.queue_callback = None
        self.queue_progress_callback = None
        self.is_queue_mode = False
        self.queue_running = False
        
        # Single transfer mode
        self.src_file = ensure_str(src_file) if src_file else None
        self.dst_file = ensure_str(dst_file) if dst_file else None
        self.src_isDir = src_isDir
        self.do_copy = do_copy
        self.show_speed = show_speed
        self.preserve_attributes = preserve_attributes
        self.user_callback = callback
        
        debug_print(f"FileTransferJob created: {title}")
        debug_print(f"  src: {self.src_file}")
        debug_print(f"  dst: {self.dst_file}")
        debug_print(f"  is_dir: {src_isDir}, copy: {do_copy}")
        
        # Create task for single transfer if files provided
        if src_file and dst_file:
            self.task = WestyFileTransferTask(self, src_file, dst_file, src_isDir, do_copy,
                                            show_speed, preserve_attributes)
            self.is_queue_mode = False
        else:
            self.is_queue_mode = True
            self.task = None
    
    def addCallback(self, callback):
        """Add completion callback"""
        self.user_callback = callback
    
    # QUEUE SUPPORT METHODS
    
    def add_to_queue(self, src, dst, operation='copy', callback=None):
        """Add a file transfer to the queue"""
        src_str = ensure_str(src)
        dst_str = ensure_str(dst)
        
        queue_item = {
            'src': src_str,
            'dst': dst_str,
            'operation': operation,  # 'copy' or 'move'
            'callback': callback,
            'status': 'pending',
            'is_dir': os.path.isdir(src_str) if os.path.exists(src_str) else False
        }
        
        self.transfer_queue.append(queue_item)
        
        debug_print(f"Added to queue: {src_str} -> {dst_str} ({operation})")
        debug_print(f"Queue size: {len(self.transfer_queue)}")
        
        return len(self.transfer_queue)
    
    def start_queue(self, progress_callback=None, completion_callback=None):
        """Start processing the transfer queue"""
        if not self.transfer_queue:
            debug_print("Queue is empty")
            if completion_callback:
                completion_callback(True, "Queue is empty")
            return
        
        self.queue_callback = completion_callback
        self.queue_progress_callback = progress_callback
        self.queue_running = True
        self.is_queue_mode = True
        
        debug_print(f"Starting queue with {len(self.transfer_queue)} items")
        
        # Start processing first item
        self._process_next_in_queue()
    
    def _process_next_in_queue(self):
        """Process the next item in the queue"""
        if not self.transfer_queue or not self.queue_running:
            # Queue is empty or stopped
            self.queue_running = False
            if self.queue_callback:
                self.queue_callback(True, "All transfers completed")
            return
        
        # Get next item
        item = self.transfer_queue[0]  # Peek at first item, don't remove yet
        self.current_transfer = item
        
        debug_print(f"Processing: {item['src']} -> {item['dst']} ({item['operation']})")
        
        # Update progress for queue position
        if self.queue_progress_callback:
            total = len(self.transfer_queue)
            processed = 0  # Current item hasn't been processed yet
            progress_percent = (processed / total) * 100 if total > 0 else 0
            self.queue_progress_callback(progress_percent, processed, total,
                                       f"Starting {os.path.basename(item['src'])}")
        
        # Create and start task for this transfer
        if item['operation'] == 'copy':
            self.task = WestyFileTransferTask(
                self, item['src'], item['dst'], item['is_dir'], True,
                self.show_speed, self.preserve_attributes
            )
        elif item['operation'] == 'move':
            self.task = WestyFileTransferTask(
                self, item['src'], item['dst'], item['is_dir'], False,
                self.show_speed, self.preserve_attributes
            )
        
        # Add task to job and start it
        self.addTask(self.task)
        
        # Add callback to task's job
        if hasattr(self.task, 'job'):
            self.task.job.addCallback(self._on_single_transfer_complete)
    
    def _on_single_transfer_complete(self, success, message):
        """Called when a single transfer task completes"""
        self.on_transfer_complete(success, message)
    
    def on_transfer_complete(self, success, message):
        """Called when a single transfer completes"""
        if self.is_queue_mode and self.current_transfer:
            # Mark current item as completed/failed
            item = self.current_transfer
            item['status'] = 'completed' if success else 'failed'
            item['message'] = message
            
            debug_print(f"Queue item completed: {success}, {message}")
            
            # Remove from queue
            if self.transfer_queue and self.transfer_queue[0] == item:
                completed_item = self.transfer_queue.pop(0)
                
                # Call item's callback if provided
                if completed_item.get('callback'):
                    completed_item['callback'](success, message)
            
            # Update overall progress
            if self.queue_progress_callback:
                total = len(self.transfer_queue) + 1  # +1 for just completed item
                processed = 1  # We just processed one item
                progress = (processed / total) * 100 if total > 0 else 100
                self.queue_progress_callback(progress, processed, total,
                                           f"Completed {os.path.basename(item['src'])}")
            
            # Process next item in queue
            if self.queue_running:
                self._process_next_in_queue()
        else:
            # Single transfer mode
            debug_print(f"Single transfer completed: {success}, {message}")
            if self.user_callback:
                self.user_callback(success, message)
    
    def on_transfer_progress(self, percent, speed, bytes_transferred, total_bytes):
        """Called when transfer progress updates"""
        if self.is_queue_mode and self.current_transfer and self.queue_progress_callback:
            # Calculate overall progress including queue position
            total_items = len(self.transfer_queue) + 1  # +1 for current item
            current_item_progress = percent / 100.0
            processed_items = 0  # Current item is still processing
            overall_progress = ((processed_items + current_item_progress) / total_items) * 100
            
            filename = os.path.basename(self.current_transfer['src'])
            speed_str = EnhancedUnitScaler().format(speed, 'bytes') + "/s" if speed > 0 else "0 B/s"
            
            self.queue_progress_callback(overall_progress, bytes_transferred, total_bytes,
                                       f"{filename}: {percent}% ({speed_str})")
    
    def clear_queue(self):
        """Clear all items from the transfer queue"""
        self.transfer_queue.clear()
        self.current_transfer = None
        self.queue_running = False
        debug_print("Transfer queue cleared")
    
    def stop_queue(self):
        """Stop processing the queue"""
        self.queue_running = False
        debug_print("Queue processing stopped")
    
    def get_queue_status(self):
        """Get status of the transfer queue"""
        pending = len([item for item in self.transfer_queue if item.get('status') == 'pending'])
        completed = len([item for item in self.transfer_queue if item.get('status') == 'completed'])
        failed = len([item for item in self.transfer_queue if item.get('status') == 'failed'])
        
        return {
            'total': len(self.transfer_queue) + (1 if self.current_transfer else 0),
            'pending': pending,
            'completed': completed,
            'failed': failed,
            'current': self.current_transfer,
            'running': self.queue_running
        }
    
    def batch_copy_files(self, file_list, dest_dir, progress_callback=None, completion_callback=None):
        """Copy multiple files to a destination directory"""
        self.clear_queue()
        
        dest_dir_str = ensure_str(dest_dir)
        
        for src in file_list:
            src_str = ensure_str(src)
            if os.path.exists(src_str):
                # Build destination path
                src_name = os.path.basename(src_str)
                dst = os.path.join(dest_dir_str, src_name)
                
                # Add to queue
                self.add_to_queue(src_str, dst, 'copy')
        
        # Start processing the queue
        self.start_queue(progress_callback, completion_callback)
    
    def batch_move_files(self, file_list, dest_dir, progress_callback=None, completion_callback=None):
        """Move multiple files to a destination directory"""
        self.clear_queue()
        
        dest_dir_str = ensure_str(dest_dir)
        
        for src in file_list:
            src_str = ensure_str(src)
            if os.path.exists(src_str):
                # Build destination path
                src_name = os.path.basename(src_str)
                dst = os.path.join(dest_dir_str, src_name)
                
                # Add to queue
                self.add_to_queue(src_str, dst, 'move')
        
        # Start processing the queue
        self.start_queue(progress_callback, completion_callback)


class WestyFileTransferTask(Task):
    """Enhanced file transfer task with speed monitoring"""
    
    def __init__(self, job, src_file, dst_file, src_isDir, do_copy, 
                 show_speed, preserve_attributes):
        Task.__init__(self, job, "")
        
        self.src_file = ensure_str(src_file)
        self.dst_file = ensure_str(dst_file)
        self.src_isDir = src_isDir
        self.do_copy = do_copy
        self.show_speed = show_speed
        self.preserve_attributes = preserve_attributes
        
        # Speed calculation
        self.start_time = None
        self.last_update = None
        self.last_bytes = 0
        self.current_speed = 0
        self.avg_speed = 0
        self.speed_samples = []
        
        # Progress tracking
        self.progress_timer = eTimer()
        if hasattr(self.progress_timer, 'callback'):
            self.progress_timer.callback.append(self.updateProgress)
        else:
            self.progress_timer.append(self.updateProgress)
        self.update_interval = 1000  # Update every second
        
        # Thread for background transfer
        self.transfer_thread = None
        self.total_size = 0
        self.copied_size = 0
        self.error = None
        self.completed = False
        self.cancelled = False
        
        # Build command
        self.buildCommand()
        
        debug_print(f"FileTransferTask initialized: src={src_file}, dst={dst_file}")
    
    def buildCommand(self):
        """Build appropriate command for operation"""
        # We'll handle the transfer manually to track progress
        # This is a dummy command for the Task framework
        self.setCmdline("westyfiletransfer")
    
    def prepare(self):
        """Prepare for transfer"""
        try:
            debug_print(f"Preparing transfer: {self.src_file} -> {self.dst_file}")
            
            # Ensure destination directory exists
            dst_dir = os.path.dirname(self.dst_file)
            if dst_dir and not os.path.exists(dst_dir):
                os.makedirs(dst_dir, exist_ok=True)
                debug_print(f"Created destination directory: {dst_dir}")
            
            # Calculate total size
            if self.src_isDir:
                self.total_size = self.calculateDirectorySize(self.src_file)
                debug_print(f"Directory size: {self.total_size} bytes")
            else:
                if os.path.exists(self.src_file):
                    self.total_size = os.path.getsize(self.src_file)
                    debug_print(f"File size: {self.total_size} bytes")
                else:
                    raise FileNotFoundError(f"Source file not found: {self.src_file}")
            
            # Initialize timing
            self.start_time = time.time()
            self.last_update = self.start_time
            self.last_bytes = 0
            self.speed_samples = []
            
            # Start transfer in background thread
            self.transfer_thread = threading.Thread(target=self._performTransfer)
            self.transfer_thread.daemon = True
            self.transfer_thread.start()
            
            # Start progress updates
            self.progress_timer.start(self.update_interval)
            
            debug_print("Transfer preparation completed")
            
        except Exception as e:
            debug_print(f"Error in prepare: {e}")
            self.error = str(e)
            self.setProgress(100)
            raise
    
    def _performTransfer(self):
        """Perform the actual file transfer"""
        try:
            debug_print("Starting transfer thread")
            
            if self.cancelled:
                debug_print("Transfer cancelled before starting")
                return
            
            if self.src_isDir:
                self._transferDirectory()
            else:
                self._transferFile()
            
            self.completed = True
            debug_print("Transfer completed successfully")
            
        except Exception as e:
            debug_print(f"Error in transfer thread: {e}")
            self.error = str(e)
            self.completed = False
    
    def _transferFile(self):
        """Transfer single file with progress tracking"""
        debug_print(f"Transferring file: {self.src_file} -> {self.dst_file}")
        
        chunk_size = 64 * 1024  # 64KB chunks
        
        try:
            with open(self.src_file, 'rb') as src:
                with open(self.dst_file, 'wb') as dst:
                    while True:
                        if self.cancelled:
                            debug_print("File transfer cancelled")
                            return
                        
                        chunk = src.read(chunk_size)
                        if not chunk:
                            break
                        
                        dst.write(chunk)
                        self.copied_size += len(chunk)
                        
                        # Update speed calculation
                        now = time.time()
                        elapsed_since_last = now - self.last_update
                        if elapsed_since_last >= 1.0:  # Update speed every second
                            bytes_since_last = self.copied_size - self.last_bytes
                            if elapsed_since_last > 0:
                                self.current_speed = bytes_since_last / elapsed_since_last
                                self.speed_samples.append(self.current_speed)
                                if len(self.speed_samples) > 10:
                                    self.speed_samples.pop(0)
                                if self.speed_samples:
                                    self.avg_speed = sum(self.speed_samples) / len(self.speed_samples)
                            
                            self.last_update = now
                            self.last_bytes = self.copied_size
            
            # Preserve file attributes if requested
            if self.preserve_attributes and os.path.exists(self.dst_file):
                try:
                    src_stat = os.stat(self.src_file)
                    os.chmod(self.dst_file, src_stat.st_mode)
                    os.utime(self.dst_file, (src_stat.st_atime, src_stat.st_mtime))
                    debug_print("File attributes preserved")
                except Exception as e:
                    debug_print(f"Warning: Could not preserve attributes: {e}")
            
            debug_print(f"File transfer completed: {self.copied_size} bytes")
            
        except Exception as e:
            debug_print(f"Error in file transfer: {e}")
            # Clean up partial file
            if os.path.exists(self.dst_file):
                try:
                    os.remove(self.dst_file)
                except:
                    pass
            raise
    
    def _transferDirectory(self):
        """Transfer directory recursively"""
        debug_print(f"Transferring directory: {self.src_file} -> {self.dst_file}")
        
        if self.do_copy:
            # Copy directory
            shutil.copytree(self.src_file, self.dst_file, 
                          copy_function=self._copyFileWithProgress,
                          dirs_exist_ok=True)
        else:
            # Move directory
            shutil.move(self.src_file, self.dst_file)
        
        debug_print("Directory transfer completed")
    
    def _copyFileWithProgress(self, src, dst):
        """Custom copy function that updates progress"""
        if self.cancelled:
            raise InterruptedError("Transfer cancelled")
        
        # Get file size
        file_size = os.path.getsize(src)
        
        # Copy file
        with open(src, 'rb') as src_file:
            with open(dst, 'wb') as dst_file:
                chunk_size = 64 * 1024
                copied = 0
                
                while True:
                    chunk = src_file.read(chunk_size)
                    if not chunk:
                        break
                    
                    dst_file.write(chunk)
                    copied += len(chunk)
                    self.copied_size += len(chunk)
        
        # Update speed calculation
        now = time.time()
        bytes_since_last = self.copied_size - self.last_bytes
        elapsed_since_last = now - self.last_update
        
        if elapsed_since_last >= 1.0:
            if elapsed_since_last > 0:
                self.current_speed = bytes_since_last / elapsed_since_last
                self.speed_samples.append(self.current_speed)
                if len(self.speed_samples) > 10:
                    self.speed_samples.pop(0)
                if self.speed_samples:
                    self.avg_speed = sum(self.speed_samples) / len(self.speed_samples)
            
            self.last_update = now
            self.last_bytes = self.copied_size
        
        # Preserve attributes if requested
        if self.preserve_attributes:
            try:
                src_stat = os.stat(src)
                os.chmod(dst, src_stat.st_mode)
                os.utime(dst, (src_stat.st_atime, src_stat.st_mtime))
            except:
                pass
        
        return dst
    
    def updateProgress(self):
        """Update progress and speed display"""
        if self.cancelled:
            self.progress_timer.stop()
            return
        
        try:
            # Calculate progress
            if self.total_size > 0:
                progress = (self.copied_size / self.total_size) * 100
                self.setProgress(min(100, int(progress)))
                
                # Notify job of progress
                if hasattr(self.job, 'on_transfer_progress'):
                    self.job.on_transfer_progress(progress, self.current_speed, 
                                                 self.copied_size, self.total_size)
                
                # Update task description with speed
                if self.show_speed and not self.src_isDir:
                    now = time.time()
                    elapsed = now - self.start_time
                    
                    if elapsed > 0 and self.copied_size > 0:
                        current_speed = self.copied_size / elapsed
                        speed_str = self.formatSpeed(current_speed)
                        remaining = self.formatTimeRemaining(progress, elapsed)
                        
                        # Update task name
                        operation = _("Copying") if self.do_copy else _("Moving")
                        filename = os.path.basename(self.src_file)
                        self.name = f"{operation} {filename} - {speed_str} - {remaining}"
            
            # Check if transfer completed
            if self.completed:
                self.progress_timer.stop()
                self.setProgress(100)
                self._notifyCompletion()
                
        except Exception as e:
            debug_print(f"Error in updateProgress: {e}")
            self.progress_timer.stop()
    
    def _notifyCompletion(self):
        """Notify job completion"""
        if hasattr(self.job, 'on_transfer_complete'):
            try:
                success = self.verifyTransfer()
                message = "Transfer completed successfully" if success else self.error
                self.job.on_transfer_complete(success, message)
            except Exception as e:
                debug_print(f"Error in completion notification: {e}")
    
    def formatSpeed(self, bytes_per_sec):
        """Format speed in human readable format"""
        if bytes_per_sec >= 1024**3:  # GB/s
            return f"{bytes_per_sec/(1024**3):.1f} GB/s"
        elif bytes_per_sec >= 1024**2:  # MB/s
            return f"{bytes_per_sec/(1024**2):.1f} MB/s"
        elif bytes_per_sec >= 1024:  # KB/s
            return f"{bytes_per_sec/1024:.1f} KB/s"
        else:
            return f"{bytes_per_sec:.0f} B/s"
    
    def formatTimeRemaining(self, progress, elapsed):
        """Format estimated time remaining"""
        if progress <= 0:
            return _("Estimating...")
        
        try:
            total_time = (elapsed / progress) * 100
            remaining = total_time - elapsed
            
            if remaining > 3600:  # Hours
                hours = remaining / 3600
                return _("{:.1f}h").format(hours)
            elif remaining > 60:  # Minutes
                minutes = remaining / 60
                return _("{:.0f}m").format(minutes)
            else:
                return _("{:.0f}s").format(remaining)
        except:
            return _("Calculating...")
    
    def calculateDirectorySize(self, path):
        """Calculate total size of directory"""
        total = 0
        try:
            for dirpath, dirnames, filenames in os.walk(ensure_str(path)):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    try:
                        if os.path.exists(fp):
                            total += os.path.getsize(fp)
                    except:
                        continue
        except Exception as e:
            debug_print(f"Error calculating directory size: {e}")
        
        return total
    
    def verifyTransfer(self):
        """Verify transfer was successful"""
        try:
            if not os.path.exists(self.dst_file):
                debug_print(f"Verification failed: Destination not found: {self.dst_file}")
                return False
            
            if self.src_isDir:
                # For directories, check if destination exists
                debug_print(f"Directory verification: Destination exists")
                return True
            else:
                # For files, compare sizes
                if os.path.exists(self.src_file) and os.path.exists(self.dst_file):
                    src_size = os.path.getsize(self.src_file)
                    dst_size = os.path.getsize(self.dst_file)
                    
                    if src_size == dst_size:
                        debug_print(f"File verification passed: {src_size} bytes")
                        return True
                    else:
                        debug_print(f"File verification failed: {src_size} != {dst_size} bytes")
                        return False
                else:
                    debug_print(f"Verification failed: Source or destination missing")
                    return False
                    
        except Exception as e:
            debug_print(f"Error in verification: {e}")
            return False
    
    def afterRun(self):
        """Cleanup after transfer"""
        debug_print("afterRun called")
        self.progress_timer.stop()
        
        # Wait for transfer thread to complete
        if self.transfer_thread and self.transfer_thread.is_alive():
            debug_print("Waiting for transfer thread to complete...")
            self.transfer_thread.join(timeout=5.0)
        
        # Verify transfer
        if self.verifyTransfer():
            debug_print("Transfer verified successfully")
        else:
            debug_print("Transfer verification failed")
    
    def cancel(self):
        """Cancel the transfer"""
        debug_print("Cancelling transfer...")
        self.cancelled = True
        self.progress_timer.stop()
        
        # Wait for thread to finish
        if self.transfer_thread and self.transfer_thread.is_alive():
            self.transfer_thread.join(timeout=2.0)
        
        # Clean up partial file
        if os.path.exists(self.dst_file) and not self.completed:
            try:
                if self.src_isDir:
                    shutil.rmtree(self.dst_file, ignore_errors=True)
                else:
                    os.remove(self.dst_file)
                debug_print("Cancelled and cleaned up partial transfer")
            except Exception as e:
                debug_print(f"Error cleaning up partial transfer: {e}")


# Convenience functions for UI
def copy_file(src, dst, callback=None, progress_callback=None):
    """Convenience function to copy a file"""
    debug_print(f"copy_file: {src} -> {dst}")
    
    if not os.path.exists(src):
        if callback:
            callback(False, f"Source not found: {src}")
        return None
    
    src = ensure_str(src)
    dst = ensure_str(dst)
    
    # Create job
    job = WestyFileTransferJob(
        src_file=src,
        dst_file=dst,
        src_isDir=False,
        do_copy=True,
        title=_("Copying file"),
        show_speed=True,
        preserve_attributes=True,
        callback=callback
    )
    
    # Add to job manager
    try:
        job_manager.AddJob(job)
        return job
    except Exception as e:
        debug_print(f"Error adding copy job: {e}")
        if callback:
            callback(False, str(e))
        return None


def move_file(src, dst, callback=None):
    """Convenience function to move a file"""
    debug_print(f"move_file: {src} -> {dst}")
    
    if not os.path.exists(src):
        if callback:
            callback(False, f"Source not found: {src}")
        return None
    
    src = ensure_str(src)
    dst = ensure_str(dst)
    
    # Create job
    job = WestyFileTransferJob(
        src_file=src,
        dst_file=dst,
        src_isDir=False,
        do_copy=False,
        title=_("Moving file"),
        show_speed=True,
        preserve_attributes=True,
        callback=callback
    )
    
    # Add to job manager
    try:
        job_manager.AddJob(job)
        return job
    except Exception as e:
        debug_print(f"Error adding move job: {e}")
        if callback:
            callback(False, str(e))
        return None


# Test function
if __name__ == "__main__":
    print("Westy FileTransfer Test")
    print("=" * 60)
    
    # Test ensure_str
    test_path = "/tmp/test.txt"
    print(f"Testing with path: {test_path}")
    
    # Test job creation
    try:
        job = WestyFileTransferJob(
            src_file=test_path,
            dst_file=test_path + ".copy",
            src_isDir=False,
            do_copy=True,
            title="Test Transfer"
        )
        print(f"Job created: {job.title}")
        print(f"Task initialized: {job.task.src_file} -> {job.task.dst_file}")
        
        # Test queue
        print("\nTesting queue functionality:")
        job.add_to_queue("/tmp/file1.txt", "/tmp/file1_copy.txt", "copy")
        job.add_to_queue("/tmp/file2.txt", "/tmp/file2_copy.txt", "copy")
        print(f"Queue size: {len(job.transfer_queue)}")
        
        status = job.get_queue_status()
        print(f"Queue status: {status}")
        
    except Exception as e:
        print(f"Job creation test failed: {e}")
    
    print("=" * 60)