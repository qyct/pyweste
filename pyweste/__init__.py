"""
PyWeste - Python Windows Installation Tools

Provides core functions for Windows application installation:
- copy_program: Copy files to installation directory
- desktop_shortcut: Create desktop shortcuts
- startmenu_shortcut: Create start menu shortcuts  
- uninstall_script: Create uninstaller with admin elevation
"""

from .lib import (
    copy_program,
    desktop_shortcut,
    startmenu_shortcut,
    uninstall_script
)

__all__ = [
    "copy_program",
    "desktop_shortcut", 
    "startmenu_shortcut",
    "uninstall_script"
]