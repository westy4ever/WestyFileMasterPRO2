#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division, unicode_literals

import os
import sys
import time
import re
from datetime import datetime

# Import our plugin's compatibility functions
try:
    from . import (
        _,
        debug_print,
        ensure_str,
        ensure_unicode,
        PLUGIN_NAME,
        PLUGIN_VERSION
    )
    debug_print(f"UnitConversions: Imported plugin utilities v{PLUGIN_VERSION}")
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


class EnhancedUnitScaler:
    """Enhanced unit conversion with formatting options - v2.1.0"""
    
    # Multiple unit systems
    UNITS = {
        'SI': {
            'scale': 1000,
            'prefixes': ['', 'k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y'],
            'suffix': ''
        },
        'IEC': {
            'scale': 1024,
            'prefixes': ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi', 'Yi'],
            'suffix': 'iB'
        },
        'JEDEC': {
            'scale': 1024,
            'prefixes': ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y'],
            'suffix': 'B'
        },
        'METRIC': {
            'scale': 1000,
            'prefixes': ['', 'k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y'],
            'suffix': ''
        }
    }
    
    def __init__(self, unit_system='IEC', max_digits=4, decimal_places=1, 
                 show_full_units=False, compact=False):
        """
        Args:
            unit_system: 'SI', 'IEC', 'JEDEC', or 'METRIC'
            max_digits: Maximum number of digits before decimal
            decimal_places: Number of decimal places to show
            show_full_units: Show full unit names (Bytes vs B)
            compact: Use compact format (1K vs 1.0 KB)
        """
        self.unit_system = unit_system.upper()
        self.config = self.UNITS.get(self.unit_system, self.UNITS['IEC'])
        self.max_digits = max_digits
        self.decimal_places = decimal_places
        self.show_full_units = show_full_units
        self.compact = compact
        
        debug_print(f"UnitScaler: Initialized with system={self.unit_system}, "
                   f"decimals={decimal_places}, compact={compact}")
    
    def format(self, value, unit_type='bytes', custom_suffix=None):
        """
        Format a value with appropriate units
        
        Args:
            value: Numeric value to format
            unit_type: 'bytes', 'bits', 'seconds', 'percent', or custom
            custom_suffix: Override the default suffix
        
        Returns:
            Formatted string
        """
        try:
            if value is None:
                return "N/A"
            
            # Handle special unit types
            if unit_type == 'percent':
                return "{:.{}f}%".format(value, self.decimal_places)
            
            if unit_type == 'seconds':
                return self.formatTime(value)
            
            # Determine suffix based on unit type
            suffix_map = {
                'bytes': 'B' if not self.show_full_units else 'Bytes',
                'bits': 'b' if not self.show_full_units else 'Bits',
            }
            base_suffix = suffix_map.get(unit_type, custom_suffix or '')
            full_suffix = self.config['suffix'] + base_suffix
            
            # Special handling for very small values
            if abs(value) < 1 and unit_type == 'bytes':
                if value == 0:
                    return "0 {}".format(full_suffix)
                # Use smaller prefixes for tiny values
                return self.formatSmallValue(value, full_suffix)
            
            # Scale the value
            scaled_value = float(value)
            scale = self.config['scale']
            prefix_index = 0
            
            while (abs(scaled_value) >= scale and 
                   prefix_index < len(self.config['prefixes']) - 1 and
                   len(str(int(scaled_value))) > self.max_digits):
                scaled_value /= scale
                prefix_index += 1
            
            # Handle very large values
            if prefix_index >= len(self.config['prefixes']):
                prefix_index = len(self.config['prefixes']) - 1
                scaled_value = value / (scale ** prefix_index)
            
            prefix = self.config['prefixes'][prefix_index]
            
            # Format based on compact setting
            if self.compact and scaled_value.is_integer():
                formatted = "{}{}{}".format(int(scaled_value), prefix, full_suffix)
            else:
                formatted = "{:.{}f} {}{}".format(scaled_value, self.decimal_places, prefix, full_suffix)
            
            return formatted.strip()
        
        except Exception as e:
            debug_print(f"UnitScaler.format error: {e}, value={value}, type={unit_type}")
            return str(value)
    
    def formatSmallValue(self, value, suffix):
        """Format very small values (less than 1)"""
        try:
            if value >= 1:
                return self.format(value, custom_suffix=suffix)
            
            # Use SI small prefixes
            small_prefixes = ['', 'm', 'μ', 'n', 'p', 'f', 'a', 'z', 'y']
            scale = 1000
            scaled_value = float(value)
            prefix_index = 0
            
            while abs(scaled_value) < 1 and prefix_index < len(small_prefixes) - 1:
                scaled_value *= scale
                prefix_index += 1
            
            prefix = small_prefixes[prefix_index]
            
            if self.compact and scaled_value.is_integer():
                return "{}{}{}".format(int(scaled_value), prefix, suffix)
            else:
                return "{:.{}f} {}{}".format(scaled_value, self.decimal_places, prefix, suffix)
        
        except Exception as e:
            debug_print(f"UnitScaler.formatSmallValue error: {e}")
            return str(value)
    
    def formatTime(self, seconds):
        """Format time duration"""
        try:
            if seconds < 0:
                return "N/A"
            
            if seconds < 1:
                # Milliseconds
                ms = seconds * 1000
                return "{:.0f} ms".format(ms) if ms >= 10 else "{:.1f} ms".format(ms)
            
            if seconds < 60:
                # Seconds
                return "{:.1f} s".format(seconds)
            
            minutes = seconds / 60
            if minutes < 60:
                # Minutes
                return "{:.1f} min".format(minutes)
            
            hours = minutes / 60
            if hours < 24:
                # Hours
                return "{:.1f} h".format(hours)
            
            days = hours / 24
            if days < 7:
                # Days
                return "{:.1f} days".format(days)
            
            weeks = days / 7
            return "{:.1f} weeks".format(weeks)
        
        except Exception as e:
            debug_print(f"UnitScaler.formatTime error: {e}")
            return str(seconds)
    
    def format_speed(self, bytes_per_sec, include_suffix=True):
        """Format data transfer speed (convenience method)"""
        formatted = self.format(bytes_per_sec, 'bytes')
        if include_suffix and '/s' not in formatted:
            return f"{formatted}/s"
        return formatted
    
    def format_eta(self, seconds):
        """Format estimated time arrival (v2.1.0 enhancement)"""
        try:
            if seconds is None or seconds < 0:
                return _("Estimating...")
            
            if seconds < 60:
                return _("{:.0f} seconds").format(seconds)
            elif seconds < 3600:
                minutes = seconds / 60
                if minutes < 10:
                    return _("{:.1f} minutes").format(minutes)
                else:
                    return _("{:.0f} minutes").format(minutes)
            elif seconds < 86400:
                hours = seconds / 3600
                if hours < 10:
                    return _("{:.1f} hours").format(hours)
                else:
                    return _("{:.0f} hours").format(hours)
            else:
                days = seconds / 86400
                return _("{:.1f} days").format(days)
        
        except Exception as e:
            debug_print(f"UnitScaler.format_eta error: {e}")
            return _("Calculating...")
    
    def format_selection_summary(self, file_count, total_size, dir_count=0):
        """Format selection summary for UI display (v2.1.0 enhancement)"""
        try:
            size_str = self.format(total_size, 'bytes')
            
            if dir_count == 0:
                return _("{} files ({})").format(file_count, size_str)
            elif file_count == 0:
                return _("{} directories ({})").format(dir_count, size_str)
            else:
                total_items = file_count + dir_count
                return _("{} items ({} files, {} dirs) ({})").format(
                    total_items, file_count, dir_count, size_str
                )
        
        except Exception as e:
            debug_print(f"UnitScaler.format_selection_summary error: {e}")
            return _("{} items").format(file_count + dir_count)
    
    def parse(self, text):
        """Parse formatted text back to number"""
        try:
            # Remove spaces and parse
            text = ensure_str(text).strip().replace(' ', '')
            
            # Match pattern: number + optional prefix + unit
            pattern = r'^([-+]?\d*\.?\d+)([kMGTPEZY]?i?)([Bb]?)$'
            match = re.match(pattern, text, re.IGNORECASE)
            
            if not match:
                return None
            
            number, prefix, unit = match.groups()
            
            try:
                value = float(number)
            except ValueError:
                return None
            
            # Apply prefix multiplier
            prefix_multipliers = {
                '': 1,
                'K': self.config['scale'] ** 1,
                'M': self.config['scale'] ** 2,
                'G': self.config['scale'] ** 3,
                'T': self.config['scale'] ** 4,
                'P': self.config['scale'] ** 5,
                'E': self.config['scale'] ** 6,
                'Z': self.config['scale'] ** 7,
                'Y': self.config['scale'] ** 8,
            }
            
            prefix_upper = prefix.upper().replace('I', '')
            if prefix_upper in prefix_multipliers:
                value *= prefix_multipliers[prefix_upper]
            
            return value
        
        except Exception as e:
            debug_print(f"UnitScaler.parse error: {e}, text={text}")
            return None
    
    @classmethod
    def humanReadable(cls, value, unit_type='bytes', **kwargs):
        """Quick human-readable formatting"""
        try:
            return cls(**kwargs).format(value, unit_type)
        except Exception as e:
            debug_print(f"humanReadable error: {e}")
            return str(value)
    
    @classmethod
    def getAvailableSystems(cls):
        """Get list of available unit systems"""
        return list(cls.UNITS.keys())
    
    @classmethod
    def get_default_scaler(cls):
        """Get default scaler instance (v2.1.0 enhancement)"""
        return cls(unit_system='IEC', decimal_places=1, compact=True)


class DataRateCalculator:
    """Calculate and format data rates - v2.1.0 enhanced"""
    
    def __init__(self, window_size=10):
        """
        Args:
            window_size: Number of samples to keep for averaging
        """
        self.window_size = window_size
        self.samples = []
        self.last_time = None
        self.last_bytes = 0
        self.start_time = time.time()
        self.scaler = EnhancedUnitScaler()
        
        debug_print(f"DataRateCalculator: Initialized with window={window_size}")
    
    def addSample(self, bytes_transferred):
        """Add a sample and calculate current rate"""
        try:
            current_time = time.time()
            
            if self.last_time is not None:
                time_delta = current_time - self.last_time
                if time_delta > 0:
                    current_rate = (bytes_transferred - self.last_bytes) / time_delta
                    self.samples.append(current_rate)
                    
                    # Keep only window_size samples
                    if len(self.samples) > self.window_size:
                        self.samples.pop(0)
            
            self.last_time = current_time
            self.last_bytes = bytes_transferred
            
            return self.getCurrentRate()
        
        except Exception as e:
            debug_print(f"DataRateCalculator.addSample error: {e}")
            return 0
    
    def getCurrentRate(self):
        """Get current transfer rate"""
        try:
            if not self.samples:
                return 0
            
            # Use weighted average (more recent samples have higher weight)
            weights = list(range(1, len(self.samples) + 1))
            weighted_sum = sum(s * w for s, w in zip(self.samples, weights))
            total_weight = sum(weights)
            
            return weighted_sum / total_weight
        
        except Exception as e:
            debug_print(f"DataRateCalculator.getCurrentRate error: {e}")
            return 0
    
    def getAverageRate(self):
        """Get simple average rate"""
        try:
            if not self.samples:
                return 0
            return sum(self.samples) / len(self.samples)
        
        except Exception as e:
            debug_print(f"DataRateCalculator.getAverageRate error: {e}")
            return 0
    
    def formatRate(self, rate, unit_system='IEC'):
        """Format rate with appropriate units"""
        try:
            scaler = EnhancedUnitScaler(unit_system=unit_system)
            return scaler.format(rate, 'bytes') + '/s'
        
        except Exception as e:
            debug_print(f"DataRateCalculator.formatRate error: {e}")
            return f"{rate:.0f} B/s"
    
    def formatCurrentRate(self):
        """Format current rate using default scaler"""
        rate = self.getCurrentRate()
        return self.scaler.format_speed(rate)
    
    def estimateTimeRemaining(self, total_bytes, transferred_bytes):
        """Estimate time remaining for transfer"""
        try:
            current_rate = self.getCurrentRate()
            
            if current_rate <= 0:
                return None
            
            remaining_bytes = total_bytes - transferred_bytes
            return remaining_bytes / current_rate
        
        except Exception as e:
            debug_print(f"DataRateCalculator.estimateTimeRemaining error: {e}")
            return None
    
    def formatTimeRemaining(self, total_bytes, transferred_bytes):
        """Format time remaining as string (v2.1.0 enhancement)"""
        try:
            seconds = self.estimateTimeRemaining(total_bytes, transferred_bytes)
            if seconds is None:
                return _("Estimating...")
            
            return self.scaler.format_eta(seconds)
        
        except Exception as e:
            debug_print(f"DataRateCalculator.formatTimeRemaining error: {e}")
            return _("Calculating...")
    
    def getProgressPercentage(self, total_bytes, transferred_bytes):
        """Get progress percentage"""
        try:
            if total_bytes <= 0:
                return 0
            return min(100, (transferred_bytes / total_bytes) * 100)
        
        except Exception as e:
            debug_print(f"DataRateCalculator.getProgressPercentage error: {e}")
            return 0
    
    def reset(self):
        """Reset calculator"""
        self.samples = []
        self.last_time = None
        self.last_bytes = 0
        self.start_time = time.time()
        debug_print("DataRateCalculator: Reset")


# Legacy compatibility
class UnitScaler(EnhancedUnitScaler):
    """Backward compatibility class"""
    pass


class UnitMultipliers:
    """Backward compatibility constants"""
    Si = EnhancedUnitScaler.UNITS['SI']['prefixes']
    Iec = EnhancedUnitScaler.UNITS['IEC']['prefixes']
    Jedec = EnhancedUnitScaler.UNITS['JEDEC']['prefixes']
    Default = EnhancedUnitScaler.UNITS['IEC']['prefixes']


# Global instance for easy access (v2.1.0 enhancement)
_default_scaler = EnhancedUnitScaler.get_default_scaler()

def format_size(size_bytes, unit_system='IEC', decimal_places=1):
    """Format file size (convenience function)"""
    return EnhancedUnitScaler(
        unit_system=unit_system, 
        decimal_places=decimal_places
    ).format(size_bytes, 'bytes')

def format_speed(bytes_per_sec, unit_system='IEC', decimal_places=1):
    """Format transfer speed (convenience function)"""
    formatted = EnhancedUnitScaler(
        unit_system=unit_system,
        decimal_places=decimal_places
    ).format(bytes_per_sec, 'bytes')
    return f"{formatted}/s"

def format_time_remaining(seconds):
    """Format time remaining (convenience function)"""
    return _default_scaler.format_eta(seconds)

def format_selection_summary(file_count, total_size, dir_count=0):
    """Format selection summary (convenience function)"""
    return _default_scaler.format_selection_summary(file_count, total_size, dir_count)


# Example usage and test
if __name__ == "__main__":
    print(f"{PLUGIN_NAME} Unit Conversions v{PLUGIN_VERSION}")
    print("=" * 60)
    
    # Test EnhancedUnitScaler
    scaler = EnhancedUnitScaler(unit_system='IEC', decimal_places=2)
    
    test_values = [1024, 1024**2, 1024**3, 1024**4, 123456789]
    
    print("Enhanced Unit Conversion Examples:")
    print("-" * 50)
    
    for value in test_values:
        formatted = scaler.format(value, 'bytes')
        parsed = scaler.parse(formatted.replace(' ', ''))
        
        print("Original: {}".format(value))
        print("Formatted: {}".format(formatted))
        if parsed is not None:
            print("Parsed back: {}".format(parsed))
            print("Difference: {}".format(abs(value - parsed)))
        else:
            print("Parsed back: None")
        print("-" * 30)
    
    # Test v2.1.0 enhancements
    print("\nv2.1.0 Enhancements:")
    print("-" * 50)
    
    # Test selection summary
    summary = scaler.format_selection_summary(
        file_count=5,
        total_size=1024**3 + 512*1024**2,  # 1.5GB
        dir_count=2
    )
    print(f"Selection summary: {summary}")
    
    # Test ETA formatting
    eta_tests = [30, 300, 3600, 7200, 86400]
    for seconds in eta_tests:
        formatted = scaler.format_eta(seconds)
        print(f"ETA {seconds}s: {formatted}")
    
    # Test DataRateCalculator
    calculator = DataRateCalculator()
    print("\nData Rate Calculation Test:")
    
    # Simulate some transfers
    bytes_transferred = 0
    for i in range(10):
        bytes_transferred += 1024 * 1024  # 1MB each iteration
        time.sleep(0.1)  # Simulate time passing
        rate = calculator.addSample(bytes_transferred)
        formatted_rate = scaler.format_speed(rate)
        print(f"Iteration {i+1}: {formatted_rate}")
    
    # Test convenience functions
    print("\nConvenience Functions:")
    print(f"format_size(123456789): {format_size(123456789)}")
    print(f"format_speed(1234567): {format_speed(1234567)}")
    print(f"format_time_remaining(3661): {format_time_remaining(3661)}")
    
    print("\n" + "=" * 60)
    print("UnitConversions module ready for v2.1.0 integration")