"""
PyWeste - Python Windows Installation Tools

Provides core functions for Windows application installation:
- do_copy_files: Copy files to installation directory
- do_desktop_shortcut: Create desktop shortcuts
- do_startmenu_shortcut: Create start menu shortcuts  
- add_to_registry: Add application to Windows registry with uninstaller
- start_gui_installer: Launch GUI installer and return user choices
"""

# Import functions directly from specialized modules
from .files import do_copy_files
from .shortcuts import do_desktop_shortcut, do_startmenu_shortcut
from .registry import add_to_registry
from .gui import start_gui_installer

__all__ = [
    "do_copy_files",
    "do_desktop_shortcut", 
    "do_startmenu_shortcut",
    "add_to_registry",
    "start_gui_installer"
]