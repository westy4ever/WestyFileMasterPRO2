#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Westy Image Viewer - Minimal Enigma2 Version"""

from __future__ import print_function, absolute_import, division, unicode_literals

import os
import sys
import time

# Import plugin utilities - simple version
try:
    from . import (
        _,
        debug_print,
        ensure_str,
        PLUGIN_NAME,
        PLUGIN_VERSION
    )
except ImportError:
    # Simple fallback
    def _(text): return text
    def debug_print(*args, **kwargs):
        if args: print(*args)
    ensure_str = str
    PLUGIN_NAME = "Westy FileMaster PRO"
    PLUGIN_VERSION = "2.1.0"

# Enigma2 imports - only what's needed
try:
    from Screens.Screen import Screen
    from Screens.MessageBox import MessageBox
    from Components.ActionMap import ActionMap
    from Components.Label import Label
    from Components.Sources.StaticText import StaticText
    from Components.Pixmap import Pixmap
    from enigma import eTimer, ePicLoad, getDesktop
    ENIGMA2_AVAILABLE = True
    debug_print("ImageViewer: Enigma2 components available")
except ImportError as e:
    ENIGMA2_AVAILABLE = False
    debug_print(f"ImageViewer: Enigma2 components not available: {e}")
    
    # Minimal mocks
    class Screen:
        def __init__(self, session): self.session = session
        def close(self): pass
    
    class MessageBox:
        def __init__(self, session, message, type=None):
            self.session = session
            self.message = message
    
    class ActionMap:
        def __init__(self, contexts, actions): pass
    
    class Label:
        def __init__(self, text=""): self.text = text
        def setText(self, text): self.text = text
    
    class StaticText:
        def __init__(self, text=""): self.text = text
    
    class Pixmap:
        def __init__(self): pass
        def instance(self):
            class Instance:
                def setPixmap(self, pixmap): pass
            return Instance()
    
    class eTimer:
        def __init__(self): pass
        def start(self, interval): pass
        def stop(self): pass
        def timeout(self):
            class Timeout:
                def get(self): return self
                def append(self, func): pass
            return Timeout()
    
    class ePicLoad:
        def __init__(self): pass
        def setPara(self, *args): pass
        def startDecode(self, path): pass
        def getData(self): return None
    
    def getDesktop(screen):
        class Desktop:
            def size(self):
                class Size:
                    def width(self): return 1280
                    def height(self): return 720
                return Size()
        return Desktop()

# Supported image formats for Enigma2
SUPPORTED_FORMATS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']

class WestyImageViewer(Screen):
    """Minimal Image Viewer for Enigma2 with slideshow support"""
    
    # Simple skin that works in Enigma2 - FIXED: No f-strings
    if ENIGMA2_AVAILABLE:
        try:
            desktop = getDesktop(0)
            width = desktop.size().width()
            height = desktop.size().height()
        except:
            width, height = 1280, 720
    else:
        width, height = 1280, 720
    
    # Fixed skin using % formatting instead of f-strings
    skin = """
<screen position="center,center" size="%d,%d" title="Image Viewer">
    <widget name="image_display" position="0,0" size="%d,%d" alphatest="blend"/>
    <widget name="status" position="20,20" size="%d,40" font="Regular;28" foregroundColor="#ffffff" backgroundColor="#00000080"/>
    <widget name="counter" position="%d,%d" size="200,30" font="Regular;24" foregroundColor="#ffff00" halign="right"/>
    <widget source="key_red" render="Label" position="20,%d" size="200,30" font="Regular;24" backgroundColor="#ff0000" halign="center"/>
    <widget source="key_green" render="Label" position="240,%d" size="200,30" font="Regular;24" backgroundColor="#00ff00" halign="center"/>
    <widget source="key_yellow" render="Label" position="460,%d" size="200,30" font="Regular;24" backgroundColor="#ffff00" halign="center"/>
    <widget source="key_blue" render="Label" position="680,%d" size="200,30" font="Regular;24" backgroundColor="#0000ff" halign="center"/>
</screen>""" % (
    width, height,           # screen size
    width, height,           # image_display size
    width-40,                # status width
    width-220, height-50,    # counter position
    height-40,               # key_red vertical position
    height-40,               # key_green vertical position  
    height-40,               # key_yellow vertical position
    height-40                # key_blue vertical position
)
    
    def __init__(self, session, image_file=None):
        Screen.__init__(self, session)
        debug_print("WestyImageViewer: Initializing...")
        
        self.session = session
        self.image_file = image_file
        self.image_list = []
        self.current_index = 0
        
        # Slideshow state
        self.slideshow_active = False
        self.slideshow_timer = eTimer()
        self.slideshow_delay = 5  # seconds
        
        # Load images
        if image_file:
            if os.path.isdir(image_file):
                # Load all images from directory
                self.image_list = self.get_images_from_directory(image_file)
                if self.image_list:
                    self.image_file = self.image_list[0]
                    self.current_index = 0
                    debug_print(f"Found {len(self.image_list)} images in directory")
            elif os.path.isfile(image_file):
                # Single image, but check directory for more
                directory = os.path.dirname(image_file)
                self.image_list = self.get_images_from_directory(directory)
                if self.image_list and image_file in self.image_list:
                    self.current_index = self.image_list.index(image_file)
                elif self.image_list:
                    # Image not in list but directory has images
                    self.image_list.insert(0, image_file)
                    self.current_index = 0
                else:
                    # Only this image
                    self.image_list = [image_file]
                    self.current_index = 0
        
        # Setup widgets
        self["image_display"] = Pixmap()
        self["status"] = Label("")
        self["counter"] = Label("")
        
        # Key labels
        self["key_red"] = StaticText(_("Exit"))
        self["key_green"] = StaticText(_("Slideshow"))
        self["key_yellow"] = StaticText(_("Prev"))
        self["key_blue"] = StaticText(_("Next"))
        
        # Setup actions
        self.setupActions()
        
        # Load first image
        if self.image_file and os.path.exists(self.image_file):
            self.loadImage(self.image_file)
        else:
            self["status"].setText(_("No image found"))
        
        # Connect slideshow timer
        try:
            self.slideshow_timer.timeout.get().append(self.nextSlide)
        except:
            pass
        
        debug_print("WestyImageViewer: Initialized")
    
    def get_images_from_directory(self, directory):
        """Get all images from a directory"""
        images = []
        try:
            if not os.path.isdir(directory):
                return images
            
            for filename in os.listdir(directory):
                if filename.startswith('.'):
                    continue
                
                ext = os.path.splitext(filename)[1].lower()
                if ext in SUPPORTED_FORMATS:
                    full_path = os.path.join(directory, filename)
                    if os.path.isfile(full_path):
                        images.append(full_path)
            
            # Sort by filename
            images.sort()
            
        except Exception as e:
            debug_print(f"Error reading directory: {e}")
        
        return images
    
    def setupActions(self):
        """Setup action map - minimal but functional"""
        self["actions"] = ActionMap(["WizardActions", "DirectionActions", "ColorActions"],
        {
            "cancel": self.exitViewer,
            "red": self.exitViewer,
            "green": self.toggleSlideshow,
            "yellow": self.prevImage,
            "blue": self.nextImage,
            "left": self.prevImage,
            "right": self.nextImage,
            "up": self.showInfo,
            "down": self.hideInfo,
            "ok": self.toggleFullscreen,
        }, -1)
    
    def loadImage(self, image_path):
        """Load and display image using ePicLoad"""
        if not image_path or not os.path.exists(image_path):
            self["status"].setText(_("File not found"))
            return
        
        try:
            # Update status
            filename = os.path.basename(image_path)
            self["status"].setText(_("Loading: {}").format(filename))
            
            # Update counter
            if len(self.image_list) > 1:
                self["counter"].setText(f"{self.current_index + 1}/{len(self.image_list)}")
            else:
                self["counter"].setText("")
            
            if ENIGMA2_AVAILABLE:
                # Use ePicLoad for image display
                self.picload = ePicLoad()
                
                # Get screen size
                try:
                    desktop = getDesktop(0)
                    width = desktop.size().width()
                    height = desktop.size().height()
                except:
                    width, height = 1280, 720
                
                # Configure ePicLoad
                # Parameters: [width, height, scaler, cache, resize, aspect, background, test]
                self.picload.setPara([
                    width,      # width
                    height,     # height
                    1,          # scaler (1=fast)
                    0,          # cache
                    1,          # resize (1=fit to screen)
                    1,          # aspect (1=keep aspect)
                    0x00000000, # background (black)
                    0,          # test
                ])
                
                # Start decoding
                self.picload.startDecode(image_path)
                
                # Get decoded data
                ptr = self.picload.getData()
                if ptr:
                    self["image_display"].instance.setPixmap(ptr)
                    self["status"].setText(filename)
                else:
                    self["status"].setText(_("Failed to load image"))
            
            else:
                # Mock for testing
                self["status"].setText(f"{filename} (Mock)")
            
            debug_print(f"Loaded image: {filename}")
            
        except Exception as e:
            debug_print(f"Error loading image: {e}")
            self["status"].setText(_("Error: {}").format(str(e)[:50]))
    
    def nextImage(self):
        """Show next image"""
        if not self.image_list or len(self.image_list) <= 1:
            self["status"].setText(_("No more images"))
            return
        
        self.current_index = (self.current_index + 1) % len(self.image_list)
        self.image_file = self.image_list[self.current_index]
        self.loadImage(self.image_file)
    
    def prevImage(self):
        """Show previous image"""
        if not self.image_list or len(self.image_list) <= 1:
            self["status"].setText(_("No more images"))
            return
        
        self.current_index = (self.current_index - 1) % len(self.image_list)
        self.image_file = self.image_list[self.current_index]
        self.loadImage(self.image_file)
    
    def toggleSlideshow(self):
        """Toggle slideshow mode"""
        if not self.image_list or len(self.image_list) <= 1:
            self["status"].setText(_("Need multiple images for slideshow"))
            return
        
        if self.slideshow_active:
            self.stopSlideshow()
        else:
            self.startSlideshow()
    
    def startSlideshow(self):
        """Start slideshow"""
        self.slideshow_active = True
        self.slideshow_timer.start(self.slideshow_delay * 1000)
        self["key_green"].setText(_("Stop"))
        self["status"].setText(_("Slideshow started ({}s)").format(self.slideshow_delay))
        debug_print("Slideshow started")
    
    def stopSlideshow(self):
        """Stop slideshow"""
        self.slideshow_active = False
        self.slideshow_timer.stop()
        self["key_green"].setText(_("Slideshow"))
        self["status"].setText(_("Slideshow stopped"))
        debug_print("Slideshow stopped")
    
    def nextSlide(self):
        """Called by slideshow timer to show next slide"""
        if self.slideshow_active:
            self.nextImage()
            # Restart timer
            self.slideshow_timer.start(self.slideshow_delay * 1000)
    
    def showInfo(self):
        """Show image info briefly"""
        if self.image_file:
            filename = os.path.basename(self.image_file)
            try:
                size = os.path.getsize(self.image_file)
                if size < 1024:
                    size_str = f"{size} B"
                elif size < 1024 * 1024:
                    size_str = f"{size/1024:.1f} KB"
                else:
                    size_str = f"{size/(1024*1024):.1f} MB"
                
                info = f"{filename} - {size_str}"
                self["status"].setText(info)
                
                # Auto-hide after 3 seconds
                self.hide_timer = eTimer()
                try:
                    self.hide_timer.timeout.get().append(self.hideInfo)
                except:
                    pass
                self.hide_timer.startLongTimer(3)
                
            except:
                self["status"].setText(filename)
    
    def hideInfo(self):
        """Hide status info"""
        if self.image_file:
            self["status"].setText("")
    
    def toggleFullscreen(self):
        """Simple fullscreen placeholder"""
        if self["status"].text:
            self["status"].setText("")
        else:
            self["status"].setText(os.path.basename(self.image_file))
    
    def exitViewer(self):
        """Exit the image viewer"""
        self.stopSlideshow()
        self.close()
        debug_print("Image viewer closed")
    
    def cleanup(self):
        """Cleanup resources"""
        if hasattr(self, 'slideshow_timer'):
            self.slideshow_timer.stop()
        if hasattr(self, 'hide_timer'):
            try:
                self.hide_timer.stop()
            except:
                pass

# Factory function
def viewImage(session, image_file):
    """Convenience function to view image"""
    try:
        debug_print(f"Opening image viewer for: {image_file}")
        
        if not image_file or not os.path.exists(image_file):
            session.open(MessageBox, 
                        _("Image file not found:\n{}").format(image_file), 
                        MessageBox.TYPE_ERROR)
            return None
        
        # Check if it's an image
        ext = os.path.splitext(image_file)[1].lower()
        if ext not in SUPPORTED_FORMATS:
            session.open(MessageBox,
                        _("Unsupported image format:\n{}").format(ext),
                        MessageBox.TYPE_WARNING)
            # Still try to open it
        
        viewer = WestyImageViewer(session, image_file)
        session.open(viewer)
        return viewer
        
    except Exception as e:
        debug_print(f"Error opening image viewer: {e}")
        session.open(MessageBox,
                    _("Cannot open image viewer:\n{}").format(str(e)),
                    MessageBox.TYPE_ERROR)
        return None

# Test - KEEP AS IS (good documentation)
if __name__ == "__main__":
    print("=" * 60)
    print("Westy Image Viewer - Minimal Enigma2 Version")
    print("=" * 60)
    print("\nFeatures:")
    print("  ✓ Basic image viewing with ePicLoad")
    print("  ✓ Simple navigation (left/right/prev/next)")
    print("  ✓ Slideshow with timer")
    print("  ✓ Multiple image detection in directory")
    print("  ✓ Image counter display")
    print("  ✓ Minimal resource usage")
    print("\nSupported formats:")
    for fmt in SUPPORTED_FORMATS:
        print(f"  • {fmt}")
    print("\nReady for Enigma2 integration")