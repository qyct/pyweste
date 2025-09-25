import os
import win32com.client
import pythoncom
from pathlib import Path


def browse_for_folder(title: str = "Select folder", default_path: str = None) -> str:
    """Browse for a folder using Windows dialog."""
    pythoncom.CoInitialize()
    try:
        shell = win32com.client.Dispatch("Shell.Application")
        folder = shell.BrowseForFolder(0, title, 0, default_path or 0)
        if folder:
            return folder.Self.Path
        return None
    finally:
        pythoncom.CoUninitialize()


def create_shortcut(target_path: str, shortcut_path: str, icon_path: str = None) -> bool:
    """Create a Windows shortcut."""
    try:
        pythoncom.CoInitialize()
        
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.TargetPath = target_path
        shortcut.WorkingDirectory = str(Path(target_path).parent)
        
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


def calculate_directory_size(directory_path: str) -> int:
    """Calculate the total size of a directory in bytes."""
    try:
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(directory_path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                try:
                    if os.path.exists(file_path):
                        total_size += os.path.getsize(file_path)
                except (OSError, IOError):
                    pass
        return total_size
    except Exception:
        return 0