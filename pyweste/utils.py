"""Internal utilities for PyWeste."""

import ctypes
import sys
import os
import win32com.client
import pythoncom
from pathlib import Path


def is_admin() -> bool:
    """Check if running with administrator privileges."""
    return ctypes.windll.shell32.IsUserAnAdmin() != 0


def request_admin(script_path: str = None, params: str = "") -> bool:
    """Request administrator privileges via UAC."""
    if is_admin():
        return True
    try:
        script_path = script_path or __file__
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, 
            f'"{script_path}" {params}', None, 1
        )
        return True
    except Exception as e:
        print(f"ERROR: Failed to elevate privileges: {e}")
        return False


def browse_for_folder(title: str = "Select folder", default_path: str = None) -> str:
    """
    Open a folder browser dialog.
    
    Args:
        title: Dialog title
        default_path: Default folder to start browsing from
        
    Returns:
        str: Selected folder path, or None if cancelled
    """
    pythoncom.CoInitialize()
    try:
        shell = win32com.client.Dispatch("Shell.Application")
        folder = shell.BrowseForFolder(0, title, 0, default_path or 0)
        if folder:
            return folder.Self.Path
        return None
    finally:
        pythoncom.CoUninitialize()


def get_program_files_path() -> str:
    """Get the Program Files directory path."""
    return os.environ.get('PROGRAMFILES', 'C:/Program Files')


def get_user_profile_path() -> str:
    """Get the user profile directory path."""
    return str(Path.home())


def get_app_data_path() -> str:
    """Get the AppData/Roaming directory path."""
    return os.environ.get('APPDATA', str(Path.home() / 'AppData' / 'Roaming'))


def validate_app_name(app_name: str) -> bool:
    """
    Validate application name for Windows compatibility.
    
    Args:
        app_name: Application name to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not app_name or not app_name.strip():
        return False
    
    # Windows forbidden characters for filenames/folders
    forbidden_chars = ['<', '>', ':', '"', '|', '?', '*']
    for char in forbidden_chars:
        if char in app_name:
            return False
    
    # Reserved names in Windows
    reserved_names = [
        'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5',
        'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 'LPT3', 'LPT4',
        'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    ]
    if app_name.upper() in reserved_names:
        return False
    
    return True


def log_info(message: str):
    """Log info message."""
    print(f"INFO: {message}")


def log_warning(message: str):
    """Log warning message."""
    print(f"WARNING: {message}")


def log_error(message: str):
    """Log error message."""
    print(f"ERROR: {message}")