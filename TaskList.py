#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division, unicode_literals

import os
import sys
import time
from datetime import datetime

# ============================================================================
# IMPORT PLUGIN UTILITIES FIRST - BEFORE ANYTHING ELSE!
# This must come FIRST so debug_print is available for all exception handlers
# ============================================================================
try:
    # First add current directory to Python path
    PLUGIN_PATH = os.path.dirname(os.path.abspath(__file__))
    if PLUGIN_PATH not in sys.path:
        sys.path.insert(0, PLUGIN_PATH)

    # Import from __init__.py directly
    import __init__ as plugin_init

    # Extract what we need
    _ = plugin_init._
    debug_print = plugin_init.debug_print
    ensure_str = plugin_init.ensure_str
    ensure_unicode = plugin_init.ensure_unicode
    PLUGIN_NAME = plugin_init.PLUGIN_NAME
    PLUGIN_VERSION = plugin_init.PLUGIN_VERSION

    debug_print(f"TaskList: Imported plugin utilities v{PLUGIN_VERSION}")
except ImportError as e:
    # Fallback for testing - define debug_print FIRST
    def debug_print(*args, **kwargs):
        if args:
            print(*args)
    
    # Now define other utilities
    def _(text):
        return text

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
    
    debug_print(f"TaskList: Import fallback: {e}")

# ============================================================================
# TRY TO IMPORT COMMON DEPENDENCIES
# Now debug_print is available for error messages
# ============================================================================
try:
    from Screens.Screen import Screen
    from Components.ActionMap import ActionMap
    from Components.Label import Label
    from Components.Sources.StaticText import StaticText
    import six
    debug_print(f"tasklist: Imported core components")
except ImportError as e:
    debug_print(f"tasklist: Import error: {e}")
    # Fallback imports for testing
    class Screen:
        def __init__(self, session):
            self.session = session
        
        def close(self):
            pass
        
        def onLayoutFinish(self, callback):
            callback()
    
    class ActionMap:
        def __init__(self, contexts, actions, prio=-1):
            pass
    
    class Label:
        def __init__(self, text=""):
            self.text = text
            self._text = text
        
        def setText(self, text):
            pass
    
    class StaticText:
        def __init__(self, text=""):
            self.text = text

# Try to import List and MultiContent with fallbacks
try:
    from Components.Sources.List import List
    from Components.MultiContent import MultiContentEntryText, MultiContentEntryProgress
    MULTICONTENT_AVAILABLE = True
    debug_print("tasklist: MultiContent components available")
except ImportError:
    MULTICONTENT_AVAILABLE = False
    debug_print("tasklist: MultiContent components not available, using fallbacks")
    
    class List:
        def __init__(self, list=None):
            self.list = list or []
            self.index = 0
        
        def getCurrent(self):
            if self.list and 0 <= self.index < len(self.list):
                return self.list[self.index]
            return None
        
        def getIndex(self):
            return self.index
        
        def setIndex(self, index):
            if 0 <= index < len(self.list):
                self.index = index
        
        def selectPrevious(self):
            if self.index > 0:
                self.index -= 1
        
        def selectNext(self):
            if self.index < len(self.list) - 1:
                self.index += 1
        
        def pageUp(self):
            self.index = max(0, self.index - 10)
        
        def pageDown(self):
            self.index = min(len(self.list) - 1, self.index + 10)
        
        def setList(self, lst):
            self.list = lst
            self.index = min(self.index, len(lst) - 1)
    
    class MultiContentEntryText:
        def __init__(self, pos=None, size=None, font=None, flags=None, text=None):
            self.pos = pos
            self.size = size
            self.font = font
            self.flags = flags
            self.text = text
    
    class MultiContentEntryProgress:
        def __init__(self, pos=None, size=None, percent=None):
            self.pos = pos
            self.size = size
            self.percent = percent

# Try to import Components.Task
try:
    from Components.Task import job_manager, Job
    TASK_AVAILABLE = True
    debug_print("tasklist: Components.Task available")
except ImportError:
    TASK_AVAILABLE = False
    debug_print("tasklist: Components.Task not available, using mock")
    
    class job_manager:
        @staticmethod
        def getPendingJobs():
            debug_print("tasklist: getPendingJobs called (mock)")
            return []
    
    class Job:
        IN_PROGRESS = 1
        NOT_STARTED = 0
        FINISHED = 2
        FAILED = 3
        
        def __init__(self, name="Mock Job", priority='normal'):
            self.status = self.NOT_STARTED
            self.name = name
            self.progress = 0
            self.priority = priority
            self.start_time = time.time()
            self.end_time = None
            self.error_message = None
        
        def getStatustext(self):
            status_map = {
                self.NOT_STARTED: "Pending",
                self.IN_PROGRESS: "In Progress",
                self.FINISHED: "Completed",
                self.FAILED: "Failed"
            }
            return status_map.get(self.status, "Unknown")
        
        def getProgress(self):
            return self.progress
        
        def getError(self):
            return self.error_message
        
        def cancel(self):
            self.status = self.FINISHED
            debug_print(f"tasklist: Mock job '{self.name}' cancelled")
        
        def start(self):
            self.status = self.IN_PROGRESS
            debug_print(f"tasklist: Mock job '{self.name}' started")
        
        def finish(self):
            self.status = self.FINISHED
            self.progress = 100
            self.end_time = time.time()
            debug_print(f"tasklist: Mock job '{self.name}' finished")
        
        def fail(self, message="Mock error"):
            self.status = self.FAILED
            self.error_message = message
            self.end_time = time.time()
            debug_print(f"tasklist: Mock job '{self.name}' failed: {message}")

# Try to import enigma modules
try:
    from enigma import gFont, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER, eTimer, getDesktop
    ENIGMA_AVAILABLE = True
    debug_print("tasklist: Enigma imports available")
except ImportError:
    ENIGMA_AVAILABLE = False
    debug_print("tasklist: Enigma imports not available")
    
    class gFont:
        pass
    
    RT_HALIGN_LEFT = 0
    RT_HALIGN_RIGHT = 1
    RT_HALIGN_CENTER = 2
    
    class eTimer:
        def __init__(self):
            self.callbacks = []
            self.active = False
        
        def start(self, interval, singleShot=False):
            self.active = True
            self.interval = interval
            debug_print(f"tasklist: Timer started with interval {interval}ms")
        
        def stop(self):
            self.active = False
            debug_print("tasklist: Timer stopped")
        
        def isActive(self):
            return self.active
        
        def timeout(self):
            class Timeout:
                def __init__(self):
                    self.callbacks = []
                
                def get(self):
                    return self
                
                def append(self, func):
                    self.callbacks.append(func)
            return Timeout()
    
    def getDesktop(screen_id=0):
        class Desktop:
            size = (1280, 720)
        return Desktop()

# Try to import TaskView for details screen
try:
    from Screens.TaskView import JobView
    TASKVIEW_AVAILABLE = True
    debug_print("tasklist: Screens.TaskView available")
except ImportError:
    TASKVIEW_AVAILABLE = False
    debug_print("tasklist: Screens.TaskView not available")
    
    class JobView:
        def __init__(self, session, job):
            self.session = session
            self.job = job
            debug_print(f"tasklist: Mock JobView created for '{job.name}'")
        
        def close(self, result=None):
            debug_print("tasklist: Mock JobView closed")
        
        def open(self):
            debug_print("tasklist: Mock JobView opened")

# Try to import other screens
try:
    from Screens.ChoiceBox import ChoiceBox
    from Screens.MessageBox import MessageBox
    SCREENS_AVAILABLE = True
    debug_print("tasklist: Screens available")
except ImportError:
    SCREENS_AVAILABLE = False
    debug_print("tasklist: Screens not available")
    
    class ChoiceBox:
        def __init__(self, session, title="", list=None):
            self.session = session
            self.title = title
            self.list = list or []
            debug_print(f"tasklist: Mock ChoiceBox created: {title}")
        
        def close(self, result=None):
            debug_print(f"tasklist: Mock ChoiceBox closed: {result}")
    
    class MessageBox:
        TYPE_INFO = 0
        TYPE_ERROR = 1
        TYPE_YESNO = 2
        TYPE_WARNING = 3
        
        def __init__(self, session, text, type=TYPE_INFO, timeout=None):
            self.session = session
            self.text = text
            self.type = type
            self.timeout = timeout
            debug_print(f"tasklist: Mock MessageBox created: {text}")
        
        def close(self, result=None):
            debug_print(f"tasklist: Mock MessageBox closed: {result}")


class WestyTaskListScreen(Screen):
    """Enhanced task list with filtering and management - v2.1.0"""
    
    # Dynamic skin based on screen size
    @staticmethod
    def get_skin():
        """Generate skin based on desktop size"""
        try:
            desktop = getDesktop(0)
            screen_width, screen_height = desktop.size().width(), desktop.size().height()
        except:
            screen_width, screen_height = 1280, 720
        
        return """
        <screen name="WestyTaskListScreen" position="center,center" size="{width},{height}" title="Westy Task Manager v2.1.0" flags="wfNoBorder">
            <widget name="filter_label" position="50,30" size="200,30" font="Regular;22" valign="center"/>
            <widget name="stats_label" position="300,30" size="400,30" font="Regular;22" valign="center"/>
            <widget source="tasklist" render="Listbox" position="50,70" size="{list_width},{list_height}" scrollbarMode="showOnDemand" enableWrapAround="1">
                <convert type="TemplatedMultiContent">
                    {{"template": [
                        MultiContentEntryText(pos=(10, 5), size=(300, 30), font=0, flags=RT_HALIGN_LEFT, text=1),  # Task name
                        MultiContentEntryText(pos=(320, 5), size=(150, 30), font=0, flags=RT_HALIGN_LEFT, text=2),  # Status
                        MultiContentEntryProgress(pos=(480, 10), size=(400, 20), percent=3),  # Progress bar
                        MultiContentEntryText(pos=(890, 5), size=(100, 30), font=0, flags=RT_HALIGN_RIGHT, text=4),  # Percentage
                        MultiContentEntryText(pos=(1000, 5), size=(150, 30), font=1, flags=RT_HALIGN_LEFT, text=5),  # Time elapsed
                        MultiContentEntryText(pos=(1150, 5), size=(80, 30), font=1, flags=RT_HALIGN_CENTER, text=6),  # Priority
                    ],
                    "fonts": [gFont("Regular", 24), gFont("Regular", 20)],
                    "itemHeight": 40}}
                </convert>
            </widget>
            <widget source="key_red" render="Label" position="50,{key_y}" size="280,40" font="Regular;24" backgroundColor="red" halign="center" valign="center"/>
            <widget source="key_green" render="Label" position="350,{key_y}" size="280,40" font="Regular;24" backgroundColor="green" halign="center" valign="center"/>
            <widget source="key_yellow" render="Label" position="650,{key_y}" size="280,40" font="Regular;24" backgroundColor="yellow" halign="center" valign="center"/>
            <widget source="key_blue" render="Label" position="950,{key_y}" size="280,40" font="Regular;24" backgroundColor="blue" halign="center" valign="center"/>
            <ePixmap position="50,{key_y}" size="280,40" pixmap="skin_default/buttons/red.png" transparent="1"/>
            <ePixmap position="350,{key_y}" size="280,40" pixmap="skin_default/buttons/green.png" transparent="1"/>
            <ePixmap position="650,{key_y}" size="280,40" pixmap="skin_default/buttons/yellow.png" transparent="1"/>
            <ePixmap position="950,{key_y}" size="280,40" pixmap="skin_default/buttons/blue.png" transparent="1"/>
        </screen>
        """.format(
            width=screen_width,
            height=screen_height,
            list_width=screen_width-100,
            list_height=screen_height-150,
            key_y=screen_height-80
        )
    
    skin = get_skin()
    
    def __init__(self, session):
        try:
            Screen.__init__(self, session)
            self.session = session
            
            self.tasklist = []
            self.filter_active = False
            self.filtered_tasks = []
            self.sort_order = 'time'  # time, name, progress, priority
            self.sort_reverse = False
            
            # CRITICAL FIX: Initialize widgets FIRST before using dictionary access
            # Define all widgets that will be accessed via self["widget_name"]
            self["filter_label"] = Label(_("All Tasks"))
            self["stats_label"] = Label("")
            self["key_red"] = StaticText(_("Close"))
            self["key_green"] = StaticText(_("Details"))
            self["key_yellow"] = StaticText(_("Filter"))
            self["key_blue"] = StaticText(_("Manage"))
            
            # Initialize the tasklist widget - FIXED VERSION
            # Use try-except for compatibility with testing environments
            try:
                # In Enigma2 environment, use proper widget assignment
                if hasattr(self, '_screen__widgets'):
                    # Standard Enigma2 Screen approach
                    self["tasklist"] = List(self.tasklist)
                else:
                    # Testing environment fallback
                    self._tasklist_widget = List(self.tasklist)
            except Exception as e:
                debug_print(f"TaskList widget initialization fallback: {e}")
                self._tasklist_widget = List(self.tasklist)
            
            self["actions"] = ActionMap(["WestyTaskListActions", "ColorActions", "DirectionActions"],
            {
                "cancel": self.close,
                "red": self.close,
                "green": self.showDetails,
                "yellow": self.toggleFilter,
                "blue": self.manageTask,
                "up": self.up,
                "down": self.down,
                "left": self.left,
                "right": self.right,
                "menu": self.showMenu,
                "info": self.showInfo,
                "channelUp": self.pageUp,
                "channelDown": self.pageDown,
            }, -1)
            
            # Initialize update timer
            self.update_timer = eTimer()
            try:
                self.update_timer.timeout.get().append(self.updateTaskList)
            except:
                # Fallback for mock timer
                if hasattr(self.update_timer, 'callback'):
                    self.update_timer.callback().append(self.updateTaskList)
                else:
                    self.update_timer.append(self.updateTaskList)
            self.update_timer.start(1000, True)  # Update every second, single shot
            
            self.task_start_times = {}
            self.task_memory = {}  # Store task history
            
            # Initialize with mock data if no real tasks
            if not TASK_AVAILABLE or not job_manager.getPendingJobs():
                self._create_sample_tasks()
            
            self.onLayoutFinish.append(self.updateTaskList)
            
            debug_print(f"WestyTaskListScreen v{PLUGIN_VERSION}: Initialized")
            
        except Exception as e:
            debug_print(f"WestyTaskListScreen init error: {e}")
            import traceback
            traceback.print_exc()
    
    def _get_tasklist_widget(self):
        """Get tasklist widget with fallback support"""
        try:
            # Try to get from Screen widgets first
            return self["tasklist"]
        except (KeyError, TypeError):
            # Fallback to internal attribute
            return getattr(self, '_tasklist_widget', None)
    
    def _set_tasklist_widget(self, value):
        """Set tasklist widget with fallback support"""
        try:
            self["tasklist"] = value
        except (TypeError, KeyError):
            # Fallback to internal attribute
            self._tasklist_widget = value
    
    def _create_sample_tasks(self):
        """Create sample tasks for demo/testing"""
        debug_print("Creating sample tasks for demo")
        
        if not TASK_AVAILABLE:
            # Create mock tasks
            self.mock_tasks = []
            for i in range(5):
                job = Job(f"Sample Task {i+1}", priority='high' if i % 3 == 0 else 'normal')
                job.status = Job.IN_PROGRESS if i < 3 else Job.NOT_STARTED
                job.progress = (i + 1) * 20
                self.mock_tasks.append(job)
            
            # Add to job manager mock
            global job_manager
            job_manager.mock_jobs = self.mock_tasks
            job_manager.getPendingJobs = lambda: self.mock_tasks
    
    def updateTaskList(self):
        """Update task list with current jobs"""
        try:
            # Get tasklist widget with fallback
            tasklist_widget = self._get_tasklist_widget()
            if not tasklist_widget:
                debug_print("updateTaskList: No tasklist widget available")
                return
            
            old_selection = tasklist_widget.getCurrent()
            old_selection_index = None
            if old_selection:
                # Find index of old selection
                for i, task in enumerate(self.tasklist):
                    if task[0] == old_selection[0]:
                        old_selection_index = i
                        break
            
            self.tasklist = []
            active_count = 0
            pending_count = 0
            completed_count = 0
            failed_count = 0
            
            jobs = []
            if TASK_AVAILABLE:
                try:
                    jobs = job_manager.getPendingJobs()
                except:
                    jobs = []
            
            for job in jobs:
                # Track start time
                if job not in self.task_start_times:
                    self.task_start_times[job] = time.time()
                    debug_print(f"Task '{job.name}' started at {self.task_start_times[job]}")
                
                # Store task in memory for history
                if job not in self.task_memory:
                    self.task_memory[job] = {
                        'name': job.name,
                        'start_time': self.task_start_times[job],
                        'status_history': []
                    }
                
                # Update history
                self.task_memory[job]['status_history'].append({
                    'time': time.time(),
                    'status': job.status,
                    'progress': job.getProgress()
                })
                
                # Calculate elapsed time
                elapsed = time.time() - self.task_start_times.get(job, time.time())
                elapsed_str = self.formatElapsedTime(elapsed)
                
                # Get job status and progress
                try:
                    status_text = job.getStatustext()
                except:
                    status_text = "Unknown"
                
                try:
                    progress = job.getProgress()
                except:
                    progress = 0
                
                # Count by status
                if job.status == job.IN_PROGRESS:
                    active_count += 1
                    status_display = _("In Progress")
                elif job.status == job.NOT_STARTED:
                    pending_count += 1
                    status_display = _("Pending")
                elif job.status == job.FINISHED:
                    completed_count += 1
                    status_display = _("Completed")
                elif hasattr(job, 'FAILED') and job.status == job.FAILED:
                    failed_count += 1
                    status_display = _("Failed")
                else:
                    status_display = status_text
                
                # Priority indicator
                priority = "\u2b06" if hasattr(job, 'priority') and job.priority == 'high' else "\u2b07"
                
                # Truncate name if too long
                name = ensure_str(job.name)
                if len(name) > 40:
                    name = name[:37] + "..."
                
                self.tasklist.append((
                    job,  # 0 - Job object
                    name,  # 1 - Task name
                    status_display,  # 2 - Status
                    progress,  # 3 - Progress for bar
                    "{:d}%".format(int(progress)),  # 4 - Percentage text
                    elapsed_str,  # 5 - Time elapsed
                    priority  # 6 - Priority indicator
                ))
            
            # Apply sorting
            self._apply_sorting()
            
            # Update stats
            total = len(self.tasklist)
            stats_text = _("Active: {active} | Pending: {pending} | Total: {total}").format(
                active=active_count,
                pending=pending_count,
                total=total
            )
            
            if completed_count > 0:
                stats_text += " | " + _("Completed: {completed}").format(completed=completed_count)
            
            if failed_count > 0:
                stats_text += " | " + _("Failed: {failed}").format(failed=failed_count)
            
            self["stats_label"].setText(stats_text)
            
            # Apply filter if active
            display_list = self.filtered_tasks if self.filter_active else self.tasklist
            
            # Set the list on the widget
            tasklist_widget.setList(display_list)
            
            # Restore selection if possible
            if old_selection_index is not None:
                # Try to find the same job
                for i, task in enumerate(display_list):
                    if task[0] == old_selection[0]:
                        tasklist_widget.setIndex(i)
                        break
                else:
                    # If not found, keep similar position if possible
                    if 0 <= old_selection_index < len(display_list):
                        tasklist_widget.setIndex(old_selection_index)
                    elif display_list:
                        tasklist_widget.setIndex(0)
            
            # Restart timer
            self.update_timer.start(1000, True)
            
        except Exception as e:
            debug_print(f"updateTaskList error: {e}")
            import traceback
            traceback.print_exc()
            # Try to restart timer anyway
            try:
                self.update_timer.start(1000, True)
            except:
                pass
    
    def _apply_sorting(self):
        """Apply current sorting to tasklist"""
        if self.sort_order == 'name':
            self.tasklist.sort(key=lambda x: x[1].lower(), reverse=self.sort_reverse)
        elif self.sort_order == 'progress':
            self.tasklist.sort(key=lambda x: x[3], reverse=not self.sort_reverse)
        elif self.sort_order == 'priority':
            # Sort by priority indicator
            self.tasklist.sort(key=lambda x: x[6] == "\u2b06", reverse=self.sort_reverse)
        elif self.sort_order == 'time':
            # Sort by start time
            self.tasklist.sort(key=lambda x: self.task_start_times.get(x[0], 0), 
                             reverse=self.sort_reverse)
        elif self.sort_order == 'status':
            # Sort by status (In Progress -> Pending -> Completed -> Failed)
            status_order = {
                _("In Progress"): 0,
                _("Pending"): 1,
                _("Completed"): 2,
                _("Failed"): 3
            }
            self.tasklist.sort(key=lambda x: status_order.get(x[2], 4), reverse=self.sort_reverse)
    
    def formatElapsedTime(self, seconds):
        """Format elapsed time in human readable format"""
        try:
            if seconds < 60:
                return "{:d}s".format(int(seconds))
            elif seconds < 3600:
                return "{:d}m {:02d}s".format(int(seconds//60), int(seconds%60))
            else:
                hours = int(seconds // 3600)
                minutes = int((seconds % 3600) // 60)
                return "{:d}h {:02d}m".format(hours, minutes)
        except:
            return "0s"
    
    def showDetails(self):
        """Show detailed task information"""
        try:
            tasklist_widget = self._get_tasklist_widget()
            if not tasklist_widget:
                return
                
            current = tasklist_widget.getCurrent()
            if current:
                job = current[0]
                
                if TASKVIEW_AVAILABLE and SCREENS_AVAILABLE:
                    self.session.openWithCallback(self.jobViewCallback, JobView, job)
                else:
                    # Show custom details popup
                    self._show_custom_details(job)
        except Exception as e:
            debug_print(f"showDetails error: {e}")
            self.session.open(
                MessageBox,
                _("Error showing details: {}").format(str(e)),
                MessageBox.TYPE_ERROR
            )
    
    def _show_custom_details(self, job):
        """Show custom task details when JobView is not available"""
        try:
            def create_info_screen(session, title, text, width=600, height=400):
                """Create a simple info screen"""
            try:
                from Screens.MessageBox import MessageBox
                session.open(MessageBox, text, MessageBox.TYPE_INFO)
            except:
                debug_print(f"Could not create info screen: {title}")
                import textwrap
            
            # Collect job information
            info_lines = []
            info_lines.append("[Task Details]")
            info_lines.append("=" * 40)
            info_lines.append(f"Name: {job.name}")
            info_lines.append(f"Status: {job.getStatustext()}")
            info_lines.append(f"Progress: {job.getProgress()}%")
            
            if job in self.task_start_times:
                elapsed = time.time() - self.task_start_times[job]
                info_lines.append(f"Elapsed: {self.formatElapsedTime(elapsed)}")
            
            if hasattr(job, 'priority'):
                info_lines.append(f"Priority: {job.priority}")
            
            if hasattr(job, 'getError') and job.status == job.FAILED:
                error = job.getError()
                if error:
                    info_lines.append(f"Error: {error}")
            
            # Add memory history
            if job in self.task_memory:
                mem = self.task_memory[job]
                info_lines.append("")
                info_lines.append("[History]")
                info_lines.append(f"Started: {datetime.fromtimestamp(mem['start_time']).strftime('%Y-%m-%d %H:%M:%S')}")
                info_lines.append(f"Status changes: {len(mem['status_history'])}")
            
            info_text = "\n".join(info_lines)
            
            # Create and show info screen
            create_info_screen(
                self.session,
                _("Task Details"),
                info_text,
                width=600,
                height=400
            )
            
        except Exception as e:
            debug_print(f"_show_custom_details error: {e}")
            self.session.open(
                MessageBox,
                _("Task: {}\nStatus: {}\nProgress: {}%").format(
                    job.name, job.getStatustext(), job.getProgress()
                ),
                MessageBox.TYPE_INFO
            )
    
    def jobViewCallback(self, result):
        """Callback from job view"""
        debug_print(f"jobViewCallback result: {result}")
        self.updateTaskList()
    
    def toggleFilter(self):
        """Toggle between showing all tasks and active tasks only"""
        try:
            tasklist_widget = self._get_tasklist_widget()
            if not tasklist_widget:
                return
                
            self.filter_active = not self.filter_active
            
            if self.filter_active:
                # Show only active tasks
                self.filtered_tasks = [
                    task for task in self.tasklist 
                    if task[0].status == task[0].IN_PROGRESS
                ]
                self["filter_label"].setText(_("Active Tasks"))
            else:
                self["filter_label"].setText(_("All Tasks"))
            
            display_list = self.filtered_tasks if self.filter_active else self.tasklist
            tasklist_widget.setList(display_list)
            
            if display_list:
                tasklist_widget.setIndex(0)
            
        except Exception as e:
            debug_print(f"toggleFilter error: {e}")
            self["filter_label"].setText(_("Error"))
    
    def manageTask(self):
        """Manage selected task (pause/resume/cancel)"""
        try:
            tasklist_widget = self._get_tasklist_widget()
            if not tasklist_widget:
                return
                
            current = tasklist_widget.getCurrent()
            if not current:
                self.session.open(
                    MessageBox,
                    _("No task selected"),
                    MessageBox.TYPE_INFO
                )
                return
            
            job = current[0]
            
            if not SCREENS_AVAILABLE:
                self._simple_task_management(job)
                return
            
            from Screens.ChoiceBox import ChoiceBox
            
            menu = []
            
            # Create action functions with proper context
            if job.status == job.IN_PROGRESS:
                menu.append((_("Pause Task"), lambda: self.pauseTask(job)))
                menu.append((_("Cancel Task"), lambda: self.cancelTask(job)))
                menu.append((_("Increase Priority"), lambda: self.setPriority(job, 'high')))
                menu.append((_("Decrease Priority"), lambda: self.setPriority(job, 'normal')))
            elif job.status == job.NOT_STARTED:
                menu.append((_("Start Task"), lambda: self.startTask(job)))
                menu.append((_("Remove Task"), lambda: self.removeTask(job)))
                menu.append((_("Set High Priority"), lambda: self.setPriority(job, 'high')))
                menu.append((_("Set Normal Priority"), lambda: self.setPriority(job, 'normal')))
            elif job.status == job.FINISHED or job.status == job.FAILED:
                menu.append((_("View Log"), lambda: self.viewTaskLog(job)))
                menu.append((_("Remove Task"), lambda: self.removeTask(job)))
                menu.append((_("Restart Task"), lambda: self.restartTask(job)))
            
            if menu:
                self.session.openWithCallback(
                    self.menuCallback,
                    ChoiceBox,
                    title=_("Manage Task: {}").format(job.name[:30]),
                    list=menu
                )
            else:
                self.session.open(
                    MessageBox,
                    _("No actions available for this task"),
                    MessageBox.TYPE_INFO
                )
                
        except Exception as e:
            debug_print(f"manageTask error: {e}")
            self.session.open(
                MessageBox,
                _("Error managing task: {}").format(str(e)),
                MessageBox.TYPE_ERROR
            )
    
    def _simple_task_management(self, job):
        """Simple task management without ChoiceBox"""
        actions = []
        
        if job.status == job.IN_PROGRESS:
            actions = ["Cancel Task", "Change Priority"]
        elif job.status == job.NOT_STARTED:
            actions = ["Start Task", "Remove Task"]
        
        if actions:
            # Create simple text menu
            menu_text = _("Manage Task: {}\n\n").format(job.name[:30])
            for i, action in enumerate(actions, 1):
                menu_text += f"{i}. {action}\n"
            
            self.session.open(
                MessageBox,
                menu_text,
                MessageBox.TYPE_INFO
            )
        else:
            self.session.open(
                MessageBox,
                _("No actions available"),
                MessageBox.TYPE_INFO
            )
    
    def menuCallback(self, choice):
        """Handle menu choice callback"""
        try:
            if choice:
                debug_print(f"menuCallback: Executing {choice[0]}")
                choice[1]()
            else:
                debug_print("menuCallback: No choice made")
        except Exception as e:
            debug_print(f"menuCallback execution error: {e}")
            self.session.open(
                MessageBox,
                _("Error executing action: {}").format(str(e)),
                MessageBox.TYPE_ERROR
            )
    
    def pauseTask(self, job):
        """Pause a running task"""
        try:
            # This requires Task modifications - placeholder for now
            if hasattr(job, 'pause'):
                job.pause()
                self.updateTaskList()
                self.session.open(
                    MessageBox,
                    _("Task paused: {}").format(job.name),
                    MessageBox.TYPE_INFO
                )
            else:
                self.session.open(
                    MessageBox,
                    _("Task pausing not supported in this version"),
                    MessageBox.TYPE_INFO
                )
        except Exception as e:
            debug_print(f"pauseTask error: {e}")
    
    def cancelTask(self, job):
        """Cancel a task"""
        try:
            if hasattr(job, 'cancel'):
                job.cancel()
                self.updateTaskList()
                self.session.open(
                    MessageBox,
                    _("Task cancelled: {}").format(job.name),
                    MessageBox.TYPE_INFO,
                    timeout=3
                )
            else:
                # Fallback: change status
                job.status = Job.FINISHED
                self.updateTaskList()
        except Exception as e:
            debug_print(f"cancelTask error: {e}")
    
    def startTask(self, job):
        """Start a pending task"""
        try:
            if hasattr(job, 'start'):
                job.start()
                self.updateTaskList()
                self.session.open(
                    MessageBox,
                    _("Task started: {}").format(job.name),
                    MessageBox.TYPE_INFO,
                    timeout=3
                )
            else:
                job.status = Job.IN_PROGRESS
                self.updateTaskList()
        except Exception as e:
            debug_print(f"startTask error: {e}")
    
    def setPriority(self, job, priority):
        """Set task priority"""
        try:
            job.priority = priority
            self.updateTaskList()
            self.session.open(
                MessageBox,
                _("Priority set to {} for: {}").format(priority, job.name),
                MessageBox.TYPE_INFO,
                timeout=2
            )
        except Exception as e:
            debug_print(f"setPriority error: {e}")
    
    def removeTask(self, job):
        """Remove a task from the list"""
        try:
            # Note: This doesn't actually remove from job_manager
            # Just removes from our display
            if hasattr(job, 'remove'):
                job.remove()
            
            # Clean up our tracking
            if job in self.task_start_times:
                del self.task_start_times[job]
            
            if job in self.task_memory:
                del self.task_memory[job]
            
            self.updateTaskList()
            
            self.session.open(
                MessageBox,
                _("Task removed: {}").format(job.name),
                MessageBox.TYPE_INFO,
                timeout=3
            )
            
        except Exception as e:
            debug_print(f"removeTask error: {e}")
    
    def viewTaskLog(self, job):
        """View task log/history"""
        try:
            if job in self.task_memory:
                mem = self.task_memory[job]
                log_text = _("Task Log: {}\n").format(job.name)
                log_text += "=" * 40 + "\n"
                log_text += _("Started: {}\n").format(
                    datetime.fromtimestamp(mem['start_time']).strftime('%Y-%m-%d %H:%M:%S')
                )
                
                if hasattr(job, 'end_time') and job.end_time:
                    log_text += _("Ended: {}\n").format(
                        datetime.fromtimestamp(job.end_time).strftime('%Y-%m-%d %H:%M:%S')
                    )
                    duration = job.end_time - mem['start_time']
                    log_text += _("Duration: {}\n").format(self.formatElapsedTime(duration))
                
                log_text += "\n" + _("Status History:") + "\n"
                for entry in mem['status_history'][-10:]:  # Last 10 entries
                    log_text += "  {}: {} ({}%)\n".format(
                        datetime.fromtimestamp(entry['time']).strftime('%H:%M:%S'),
                        entry['status'],
                        entry['progress']
                    )
                
                self.session.open(
                    MessageBox,
                    log_text,
                    MessageBox.TYPE_INFO,
                    timeout=10
                )
        except Exception as e:
            debug_print(f"viewTaskLog error: {e}")
    
    def restartTask(self, job):
        """Restart a completed/failed task"""
        try:
            # Reset job state
            job.status = Job.NOT_STARTED
            job.progress = 0
            self.task_start_times[job] = time.time()
            self.updateTaskList()
            
            self.session.open(
                MessageBox,
                _("Task restarted: {}").format(job.name),
                MessageBox.TYPE_INFO,
                timeout=3
            )
        except Exception as e:
            debug_print(f"restartTask error: {e}")
    
    def showMenu(self):
        """Show task management menu"""
        try:
            if not SCREENS_AVAILABLE:
                self._simple_menu()
                return
            
            from Screens.ChoiceBox import ChoiceBox
            
            # Create action functions
            def refresh_action():
                self.updateTaskList()
                self.session.open(
                    MessageBox,
                    _("Task list refreshed"),
                    MessageBox.TYPE_INFO,
                    timeout=2
                )
            
            def clear_action():
                self.clearCompleted()
            
            def sort_name_action():
                self.sortTasks('name')
            
            def sort_progress_action():
                self.sortTasks('progress')
            
            def sort_time_action():
                self.sortTasks('time')
            
            def sort_priority_action():
                self.sortTasks('priority')
            
            def sort_status_action():
                self.sortTasks('status')
            
            def toggle_sort_action():
                self.sort_reverse = not self.sort_reverse
                self._apply_sorting()
                display_list = self.filtered_tasks if self.filter_active else self.tasklist
                tasklist_widget = self._get_tasklist_widget()
                if tasklist_widget:
                    tasklist_widget.setList(display_list)
                direction = _("descending") if self.sort_reverse else _("ascending")
                self.session.open(
                    MessageBox,
                    _("Sort order: {}").format(direction),
                    MessageBox.TYPE_INFO,
                    timeout=2
                )
            
            def export_action():
                self.exportTaskList()
            
            def settings_action():
                self.openSettings()
            
            def about_action():
                self.showAbout()
            
            menu = [
                (_("Refresh List"), refresh_action),
                (_("Clear Completed Tasks"), clear_action),
                ("", None),  # Separator
                (_("Sort by Name"), sort_name_action),
                (_("Sort by Progress"), sort_progress_action),
                (_("Sort by Time"), sort_time_action),
                (_("Sort by Priority"), sort_priority_action),
                (_("Sort by Status"), sort_status_action),
                (_("Toggle Sort Direction"), toggle_sort_action),
                ("", None),  # Separator
                (_("Export Task List"), export_action),
                (_("Settings"), settings_action),
                ("", None),  # Separator
                (_("About Task Manager"), about_action),
            ]
            
            self.session.openWithCallback(
                self.menuCallback,
                ChoiceBox,
                title=_("Task Manager Menu"),
                list=menu
            )
            
        except Exception as e:
            debug_print(f"showMenu error: {e}")
            self._simple_menu()
    
    def _simple_menu(self):
        """Simple menu without ChoiceBox"""
        menu_text = _("Task Manager Menu\n\n")
        menu_text += "1. Refresh List\n"
        menu_text += "2. Clear Completed\n"
        menu_text += "3. Sort by Name\n"
        menu_text += "4. Sort by Progress\n"
        menu_text += "5. Export List\n"
        
        self.session.open(
            MessageBox,
            menu_text,
            MessageBox.TYPE_INFO
        )
    
    def sortTasks(self, key):
        """Sort tasks by given key"""
        try:
            tasklist_widget = self._get_tasklist_widget()
            if not tasklist_widget:
                return
                
            old_key = self.sort_order
            self.sort_order = key
            
            if old_key == key:
                self.sort_reverse = not self.sort_reverse
            else:
                self.sort_reverse = False
            
            self._apply_sorting()
            
            display_list = self.filtered_tasks if self.filter_active else self.tasklist
            tasklist_widget.setList(display_list)
            
            # Show sort indicator
            direction = _("descending") if self.sort_reverse else _("ascending")
            self["filter_label"].setText(_("Sorted by {} ({})").format(key, direction))
            
        except Exception as e:
            debug_print(f"sortTasks error: {e}")
    
    def clearCompleted(self):
        """Clear completed tasks from display"""
        try:
            # This is just for display - real cleanup needs job_manager support
            removed_count = 0
            
            new_tasklist = []
            for task in self.tasklist:
                job = task[0]
                if job.status != job.FINISHED and job.status != job.FAILED:
                    new_tasklist.append(task)
                else:
                    # Clean up tracking
                    if job in self.task_start_times:
                        del self.task_start_times[job]
                    removed_count += 1
            
            self.tasklist = new_tasklist
            
            display_list = self.filtered_tasks if self.filter_active else self.tasklist
            tasklist_widget = self._get_tasklist_widget()
            if tasklist_widget:
                tasklist_widget.setList(display_list)
            
            self.session.open(
                MessageBox,
                _("Removed {} completed/failed tasks").format(removed_count),
                MessageBox.TYPE_INFO,
                timeout=3
            )
            
        except Exception as e:
            debug_print(f"clearCompleted error: {e}")
    
    def exportTaskList(self):
        """Export task list to file"""
        try:
            from datetime import datetime
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = "/tmp/westy_tasks_{}.txt".format(timestamp)
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("{} - Task List v{}\n".format(PLUGIN_NAME, PLUGIN_VERSION))
                f.write("Generated: {}\n".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                f.write("=" * 60 + "\n\n")
                
                for task in self.tasklist:
                    job, name, status, progress, percent, elapsed, priority = task
                    
                    f.write("Task: {}\n".format(name))
                    f.write("Status: {}\n".format(status))
                    f.write("Progress: {}%\n".format(progress))
                    f.write("Elapsed: {}\n".format(elapsed))
                    f.write("Priority: {}\n".format(priority))
                    
                    if job in self.task_start_times:
                        start_time = self.task_start_times[job]
                        f.write("Started: {}\n".format(
                            datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')
                        ))
                    
                    f.write("-" * 40 + "\n")
                
                f.write("\nTotal tasks: {}\n".format(len(self.tasklist)))
            
            message = _("Task list exported to: {}").format(filename)
            debug_print(message)
            
            self.session.open(
                MessageBox,
                message,
                MessageBox.TYPE_INFO,
                timeout=5
            )
            
        except Exception as e:
            debug_print(f"exportTaskList error: {e}")
            self.session.open(
                MessageBox,
                _("Error exporting task list: {}").format(str(e)),
                MessageBox.TYPE_ERROR
            )
    
    def openSettings(self):
        """Open task manager settings"""
        try:
            from .settings import WestySettingsScreen
            
            self.session.openWithCallback(
                self.settingsCallback,
                WestySettingsScreen,
                initial_tab="tasks"
            )
        except ImportError:
            # Settings screen not available
            self.session.open(
                MessageBox,
                _("Task manager settings will be implemented in future version"),
                MessageBox.TYPE_INFO
            )
        except Exception as e:
            debug_print(f"openSettings error: {e}")
            self.session.open(
                MessageBox,
                _("Error opening settings: {}").format(str(e)),
                MessageBox.TYPE_ERROR
            )
    
    def settingsCallback(self, result):
        """Callback from settings screen"""
        debug_print(f"settingsCallback result: {result}")
        self.updateTaskList()
    
    def showAbout(self):
        """Show about information"""
        try:
            about_text = _("""Westy Task Manager v{version}

A comprehensive task management system for {plugin_name}.

Features:
• Real-time task monitoring
• Task filtering and sorting
• Priority management
• Task history tracking
• Export capabilities

© 2023 Westy FileMaster PRO Team""").format(version=PLUGIN_VERSION, plugin_name=PLUGIN_NAME)
            
            self.session.open(
                MessageBox,
                about_text,
                MessageBox.TYPE_INFO
            )
        except Exception as e:
            debug_print(f"showAbout error: {e}")
    
    def showInfo(self):
        """Show info about current task"""
        tasklist_widget = self._get_tasklist_widget()
        if tasklist_widget:
            current = tasklist_widget.getCurrent()
            if current:
                self.showDetails()
            else:
                self.showAbout()
    
    def up(self):
        try:
            tasklist_widget = self._get_tasklist_widget()
            if tasklist_widget:
                tasklist_widget.selectPrevious()
        except:
            pass
    
    def down(self):
        try:
            tasklist_widget = self._get_tasklist_widget()
            if tasklist_widget:
                tasklist_widget.selectNext()
        except:
            pass
    
    def left(self):
        try:
            tasklist_widget = self._get_tasklist_widget()
            if tasklist_widget:
                tasklist_widget.pageUp()
        except:
            pass
    
    def right(self):
        try:
            tasklist_widget = self._get_tasklist_widget()
            if tasklist_widget:
                tasklist_widget.pageDown()
        except:
            pass
    
    def pageUp(self):
        self.left()
    
    def pageDown(self):
        self.right()
    
    def close(self):
        """Clean up and close"""
        try:
            debug_print("WestyTaskListScreen: Closing")
            self.update_timer.stop()
            Screen.close(self)
        except Exception as e:
            debug_print(f"close error: {e}")
            Screen.close(self)


class QuickTaskMonitor:
    """Quick task monitor for status bar display - v2.1.0"""
    
    @staticmethod
    def getTaskSummary():
        """Get quick summary of active tasks"""
        try:
            if not TASK_AVAILABLE:
                return _("No task system available")
            
            tasks = list(job_manager.getPendingJobs())
            
            if not tasks:
                return _("No active tasks")
            
            active = sum(1 for t in tasks if t.status == t.IN_PROGRESS)
            pending = sum(1 for t in tasks if t.status == t.NOT_STARTED)
            completed = sum(1 for t in tasks if t.status == t.FINISHED)
            failed = 0
            if hasattr(tasks[0], 'FAILED'):
                failed = sum(1 for t in tasks if t.status == t.FAILED)
            
            if active == 0 and pending == 0:
                if completed > 0 and failed == 0:
                    return _("{} completed").format(completed)
                elif failed > 0:
                    return _("{} failed").format(failed)
                else:
                    return _("{} tasks").format(completed + failed)
            elif pending == 0:
                return _("{} active").format(active)
            elif active == 0:
                return _("{} pending").format(pending)
            else:
                return _("{} active, {} pending").format(active, pending)
                
        except Exception as e:
            debug_print(f"getTaskSummary error: {e}")
            return _("Error")
    
    @staticmethod
    def getActiveTaskNames(limit=3):
        """Get names of active tasks"""
        try:
            if not TASK_AVAILABLE:
                return []
            
            names = []
            for job in job_manager.getPendingJobs():
                if job.status == job.IN_PROGRESS:
                    names.append(job.name)
                    if len(names) >= limit:
                        break
            
            return names
        except Exception as e:
            debug_print(f"getActiveTaskNames error: {e}")
            return []
    
    @staticmethod
    def getTaskCounts():
        """Get detailed task counts"""
        try:
            if not TASK_AVAILABLE:
                return {'active': 0, 'pending': 0, 'completed': 0, 'failed': 0, 'total': 0}
            
            tasks = list(job_manager.getPendingJobs())
            
            active = sum(1 for t in tasks if t.status == t.IN_PROGRESS)
            pending = sum(1 for t in tasks if t.status == t.NOT_STARTED)
            completed = sum(1 for t in tasks if t.status == t.FINISHED)
            failed = 0
            if tasks and hasattr(tasks[0], 'FAILED'):
                failed = sum(1 for t in tasks if t.status == t.FAILED)
            
            return {
                'active': active,
                'pending': pending,
                'completed': completed,
                'failed': failed,
                'total': len(tasks)
            }
        except Exception as e:
            debug_print(f"getTaskCounts error: {e}")
            return {'active': 0, 'pending': 0, 'completed': 0, 'failed': 0, 'total': 0}
    
    @staticmethod
    def hasActiveTasks():
        """Check if any tasks are active"""
        try:
            if not TASK_AVAILABLE:
                return False
            
            for job in job_manager.getPendingJobs():
                if job.status == job.IN_PROGRESS:
                    return True
            return False
        except Exception as e:
            debug_print(f"hasActiveTasks error: {e}")
            return False
    
    @staticmethod
    def getProgressSummary():
        """Get progress summary for all active tasks"""
        try:
            if not TASK_AVAILABLE:
                return "0%"
            
            tasks = [t for t in job_manager.getPendingJobs() if t.status == t.IN_PROGRESS]
            
            if not tasks:
                return "0%"
            
            total_progress = sum(t.getProgress() for t in tasks)
            avg_progress = total_progress // len(tasks)
            
            return "{:d}%".format(avg_progress)
        except Exception as e:
            debug_print(f"getProgressSummary error: {e}")
            return "0%"


# Test function
def test_tasklist():
    """Test task list functionality"""
    print(f"Testing {PLUGIN_NAME} TaskList v{PLUGIN_VERSION}")
    print("=" * 60)
    
    # Test QuickTaskMonitor
    print("QuickTaskMonitor tests:")
    print(f"  Summary: {QuickTaskMonitor.getTaskSummary()}")
    print(f"  Active names: {QuickTaskMonitor.getActiveTaskNames()}")
    print(f"  Task counts: {QuickTaskMonitor.getTaskCounts()}")
    print(f"  Has active tasks: {QuickTaskMonitor.hasActiveTasks()}")
    print(f"  Progress summary: {QuickTaskMonitor.getProgressSummary()}")
    
    # Create mock session for testing
    class MockSession:
        def open(self, screen, *args, **kwargs):
            print(f"  Would open screen: {screen.__name__}")
            return screen(self, *args, **kwargs)
        
        def openWithCallback(self, callback, screen, *args, **kwargs):
            print(f"  Would open screen with callback: {screen.__name__}")
            result = screen(self, *args, **kwargs)
            callback(result)
            return result
    
    # Test screen creation
    try:
        session = MockSession()
        screen = WestyTaskListScreen(session)
        print("\nScreen created successfully")
        print(f"  Filter active: {screen.filter_active}")
        print(f"  Sort order: {screen.sort_order}")
    except Exception as e:
        print(f"\nError creating screen: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("TaskList module ready for v2.1.0 integration")


if __name__ == "__main__":
    test_tasklist()