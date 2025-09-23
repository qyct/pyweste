"""
PyWeste shortcuts module.
Handles Windows shortcut creation for desktop and start menu.
"""

import os
import win32com.client
import pythoncom
from pathlib import Path


def do_desktop_shortcut(target_path: str, shortcut_name: str, icon_path: str = None) -> bool:
    """
    Create a desktop shortcut.
    
    Args:
        target_path: Path to the executable to launch
        shortcut_name: Name for the shortcut (without .lnk extension)
        icon_path: Optional path to icon file
        
    Returns:
        bool: True if shortcut created successfully, False otherwise
        
    Example:
        do_desktop_shortcut("C:/Program Files/MyApp/myapp.exe", "MyApp", "C:/Program Files/MyApp/icon.ico")
    """
    try:
        pythoncom.CoInitialize()
        
        desktop_path = str(Path.home() / "Desktop")
        shortcut_path = Path(desktop_path) / f"{shortcut_name}.lnk"
        
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(str(shortcut_path))
        shortcut.TargetPath = target_path
        shortcut.WorkingDirectory = str(Path(target_path).parent)
        shortcut.Description = f"{shortcut_name} Application"
        
        if icon_path and os.path.exists(icon_path):
            shortcut.IconLocation = f"{icon_path},0"
        
        shortcut.save()
        print(f"INFO: Desktop shortcut created: {shortcut_path}")
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to create desktop shortcut: {e}")
        return False
    finally:
        try:
            pythoncom.CoUninitialize()
        except:
            pass


def do_startmenu_shortcut(target_path: str, shortcut_name: str, icon_path: str = None, folder: str = None) -> bool:
    """
    Create a start menu shortcut.
    
    Args:
        target_path: Path to the executable to launch
        shortcut_name: Name for the shortcut (without .lnk extension)
        icon_path: Optional path to icon file
        folder: Optional subfolder in start menu (e.g., "My Company")
        
    Returns:
        bool: True if shortcut created successfully, False otherwise
        
    Example:
        do_startmenu_shortcut("C:/Program Files/MyApp/myapp.exe", "MyApp", folder="My Company")
    """
    try:
        pythoncom.CoInitialize()
        
        appdata = os.environ.get('APPDATA', str(Path.home() / 'AppData' / 'Roaming'))
        start_menu = Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
        
        if folder:
            start_menu = start_menu / folder
            start_menu.mkdir(parents=True, exist_ok=True)
        
        shortcut_path = start_menu / f"{shortcut_name}.lnk"
        
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(str(shortcut_path))
        shortcut.TargetPath = target_path
        shortcut.WorkingDirectory = str(Path(target_path).parent)
        shortcut.Description = f"{shortcut_name} Application"
        
        if icon_path and os.path.exists(icon_path):
            shortcut.IconLocation = f"{icon_path},0"
        
        shortcut.save()
        print(f"INFO: Start menu shortcut created: {shortcut_path}")
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to create start menu shortcut: {e}")
        return False
    finally:
        try:
            pythoncom.CoUninitialize()
        except:
            pass


def get_desktop_path() -> str:
    """Get the current user's desktop path."""
    return str(Path.home() / "Desktop")


def get_start_menu_path() -> str:
    """Get the current user's start menu programs path."""
    appdata = os.environ.get('APPDATA', str(Path.home() / 'AppData' / 'Roaming'))
    return str(Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs")


def create_shortcut(target_path: str, shortcut_path: str, icon_path: str = None, 
                   description: str = None) -> bool:
    """
    Generic shortcut creation function.
    
    Args:
        target_path: Path to the executable to launch
        shortcut_path: Full path where shortcut will be created
        icon_path: Optional path to icon file
        description: Optional shortcut description
        
    Returns:
        bool: True if shortcut created successfully, False otherwise
    """
    try:
        pythoncom.CoInitialize()
        
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.TargetPath = target_path
        shortcut.WorkingDirectory = str(Path(target_path).parent)
        
        if description:
            shortcut.Description = description
        
        if icon_path and os.path.exists(icon_path):
            shortcut.IconLocation = f"{icon_path},0"
        
        shortcut.save()
        print(f"INFO: Shortcut created: {shortcut_path}")
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to create shortcut: {e}")
        return False
    finally:
        try:
            pythoncom.CoUninitialize()
        except:
            pass