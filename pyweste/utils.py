import ctypes
import sys
import os
import win32com.client
import pythoncom
from pathlib import Path


def browse_for_folder(title: str = "Select folder", default_path: str = None) -> str:
    pythoncom.CoInitialize()
    try:
        shell = win32com.client.Dispatch("Shell.Application")
        folder = shell.BrowseForFolder(0, title, 0, default_path or 0)
        if folder:
            return folder.Self.Path
        return None
    finally:
        pythoncom.CoUninitialize()


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