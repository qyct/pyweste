"""
PyWeste - Python Windows Installation Tools

Provides core functions for Windows application installation:
- copy: Copy files with admin privileges
- desktop: Create desktop shortcuts
- startmenu: Create start menu shortcuts  
- uninstall: Create uninstaller with admin elevation
"""

from .lib import (
    copy,
    desktop,
    startmenu,
    uninstall
)

__version__ = "1.0.0"

__all__ = [
    "copy",
    "desktop", 
    "startmenu",
    "uninstall"
]