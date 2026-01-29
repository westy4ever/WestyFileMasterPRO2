# media_utils.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division, unicode_literals

import os
import sys
import time
from datetime import datetime

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
    debug_print(f"MediaUtils: Imported plugin utilities v{PLUGIN_VERSION}")
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


# Common media utilities
class MediaUtils:
    """Common utilities for media modules"""
    
    SUPPORTED_AUDIO_EXTS = ('.mp3', '.flac', '.ogg', '.wav', '.aac', '.m4a', '.wma', '.opus')
    SUPPORTED_VIDEO_EXTS = ('.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.m4v', '.mpg', '.mpeg')
    SUPPORTED_PLAYLIST_EXTS = ('.m3u', '.m3u8', '.pls', '.xspf')
    
    @staticmethod
    def is_audio_file(filename):
        """Check if file is audio"""
        ext = os.path.splitext(filename)[1].lower()
        return ext in MediaUtils.SUPPORTED_AUDIO_EXTS
    
    @staticmethod
    def is_video_file(filename):
        """Check if file is video"""
        ext = os.path.splitext(filename)[1].lower()
        return ext in MediaUtils.SUPPORTED_VIDEO_EXTS
    
    @staticmethod
    def is_media_file(filename):
        """Check if file is audio or video"""
        return MediaUtils.is_audio_file(filename) or MediaUtils.is_video_file(filename)
    
    @staticmethod
    def is_playlist_file(filename):
        """Check if file is a playlist"""
        ext = os.path.splitext(filename)[1].lower()
        return ext in MediaUtils.SUPPORTED_PLAYLIST_EXTS
    
    @staticmethod
    def parse_m3u_playlist(filepath):
        """Parse M3U playlist file"""
        try:
            if not os.path.exists(filepath):
                debug_print(f"Playlist file not found: {filepath}")
                return []
            
            playlist = []
            base_dir = os.path.dirname(filepath)
            
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Handle paths
                        if os.path.isabs(line):
                            if os.path.exists(line):
                                playlist.append(line)
                            else:
                                debug_print(f"Absolute path not found: {line}")
                        else:
                            # Try relative to playlist directory
                            rel_path = os.path.join(base_dir, line)
                            if os.path.exists(rel_path):
                                playlist.append(rel_path)
                            else:
                                # Keep original for reference
                                playlist.append(line)
            
            debug_print(f"Loaded playlist with {len(playlist)} tracks")
            return playlist
            
        except Exception as e:
            debug_print(f"Error parsing playlist {filepath}: {e}")
            return []
    
    @staticmethod
    def save_m3u_playlist(filepath, playlist):
        """Save playlist to M3U file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("#EXTM3U\n")
                f.write(f"# Created by {PLUGIN_NAME} v{PLUGIN_VERSION}\n")
                f.write(f"# Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                for track in playlist:
                    f.write(f"{track}\n")
            
            debug_print(f"Playlist saved: {filepath} ({len(playlist)} tracks)")
            return True
        except Exception as e:
            debug_print(f"Error saving playlist: {e}")
            return False
    
    @staticmethod
    def get_media_duration(filepath):
        """Get media file duration in seconds"""
        try:
            # Try mutagen for audio files
            if MediaUtils.is_audio_file(filepath):
                return MediaUtils._get_audio_duration(filepath)
            
            # For video files, would need video parsing library
            # For now, return 0
            return 0
            
        except Exception as e:
            debug_print(f"Error getting duration for {filepath}: {e}")
            return 0
    
    @staticmethod
    def _get_audio_duration(filepath):
        """Get audio file duration using mutagen"""
        try:
            from mutagen import File as MutagenFile
            audio = MutagenFile(filepath)
            if audio and hasattr(audio, 'info'):
                return audio.info.length
        except ImportError:
            debug_print("Mutagen not available for duration detection")
        except Exception as e:
            debug_print(f"Mutagen error: {e}")
        
        return 0
    
    @staticmethod
    def format_duration(seconds):
        """Format seconds to human readable time"""
        if seconds < 0:
            return "00:00"
        
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"
    
    @staticmethod
    def sanitize_filename(filename):
        """Sanitize filename for display"""
        if not filename:
            return _("Unknown Track")
        
        # Remove extension
        name = os.path.splitext(filename)[0]
        
        # Clean up common patterns
        name = name.replace('_', ' ').replace('-', ' - ')
        
        # Remove track numbers at beginning
        import re
        name = re.sub(r'^\d{1,3}\s*[.-]\s*', '', name)
        
        # Trim and limit length
        name = name.strip()
        if len(name) > 50:
            name = name[:47] + "..."
        
        return name
    
    @staticmethod
    def get_media_info(filepath):
        """Get basic media file information"""
        info = {
            'filename': os.path.basename(filepath),
            'path': filepath,
            'size': 0,
            'modified': '',
            'duration': 0,
            'type': 'unknown'
        }
        
        try:
            # File size
            if os.path.exists(filepath):
                stat = os.stat(filepath)
                info['size'] = stat.st_size
                info['modified'] = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            
            # File type
            if MediaUtils.is_audio_file(filepath):
                info['type'] = 'audio'
            elif MediaUtils.is_video_file(filepath):
                info['type'] = 'video'
            
            # Duration
            info['duration'] = MediaUtils.get_media_duration(filepath)
            
        except Exception as e:
            debug_print(f"Error getting media info for {filepath}: {e}")
        
        return info


# Configuration management for media modules
class MediaConfig:
    """Media configuration management"""
    
    def __init__(self):
        self.config = {}
        self._load_defaults()
    
    def _load_defaults(self):
        """Load default configuration"""
        # Media player defaults
        self.config['mediaplayer'] = {
            'auto_resume': True,
            'subtitles': True,
            'aspect_ratio': 'auto',
            'deinterlace': True,
            'cache_size': 'medium',
            'repeat_mode': 'none',  # none, one, all
            'shuffle': False,
            'volume': 80,
            'brightness': 50,
            'contrast': 50,
            'saturation': 50,
        }
        
        # Audio player defaults
        self.config['audioplayer'] = {
            'auto_play': True,
            'crossfade': False,
            'replaygain': True,
            'visualization': True,
            'gapless': True,
            'repeat_mode': 'none',
            'shuffle': False,
            'equalizer_preset': 'normal',
            'volume': 80,
        }
        
        # Audio settings defaults
        self.config['audiosettings'] = {
            'audio_output': 'stereo',
            'volume': 80,
            'balance': 50,
            'bass_boost': False,
            'surround': False,
        }
    
    def get_config(self, module):
        """Get configuration for module"""
        return self.config.get(module, {})
    
    def set_config(self, module, key, value):
        """Set configuration value"""
        if module in self.config:
            self.config[module][key] = value
            return True
        return False
    
    def save_to_file(self, filepath):
        """Save configuration to file"""
        try:
            import json
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
            debug_print(f"Media config saved to {filepath}")
            return True
        except Exception as e:
            debug_print(f"Error saving media config: {e}")
            return False
    
    def load_from_file(self, filepath):
        """Load configuration from file"""
        try:
            import json
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Merge with defaults
                    for module, config in loaded.items():
                        if module in self.config:
                            self.config[module].update(config)
                        else:
                            self.config[module] = config
                debug_print(f"Media config loaded from {filepath}")
                return True
        except Exception as e:
            debug_print(f"Error loading media config: {e}")
        
        return False


# Global instance
media_config = MediaConfig()
media_utils = MediaUtils()