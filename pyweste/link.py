"""
Shortcut creation and management for pyweste installer
"""

import os
from pathlib import Path
import win32com.client
import pythoncom


def create_desktop_shortcut(target_path: str, shortcut_name: str, icon_path: str = None, 
                          description: str = "", working_dir: str = None):
    """Create a desktop shortcut."""
    try:
        pythoncom.CoInitialize()
        
        desktop = Path(os.path.expanduser("~")) / "Desktop"
        shortcut_path = desktop / f"{shortcut_name}.lnk"
        
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(str(shortcut_path))
        shortcut.TargetPath = target_path
        shortcut.WorkingDirectory = working_dir or str(Path(target_path).parent)
        shortcut.Description = description
        
        if icon_path and os.path.exists(icon_path):
            shortcut.IconLocation = f"{icon_path},0"
        
        shortcut.save()
        print(f"Desktop shortcut created: {shortcut_path}")
        return True
        
    except Exception as e:
        print(f"Failed to create desktop shortcut: {e}")
        return False
    finally:
        try:
            pythoncom.CoUninitialize()
        except:
            pass


def create_startmenu_shortcut(target_path: str, shortcut_name: str, icon_path: str = None, 
                            description: str = "", working_dir: str = None, folder: str = None):
    """Create a start menu shortcut."""
    try:
        pythoncom.CoInitialize()
        
        # Use user's personal start menu
        start_menu = Path(os.path.expandvars("%APPDATA%")) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
        
        # Create subfolder if specified
        if folder:
            start_menu = start_menu / folder
            start_menu.mkdir(parents=True, exist_ok=True)
            
        shortcut_path = start_menu / f"{shortcut_name}.lnk"
        
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(str(shortcut_path))
        shortcut.TargetPath = target_path
        shortcut.WorkingDirectory = working_dir or str(Path(target_path).parent)
        shortcut.Description = description
        
        if icon_path and os.path.exists(icon_path):
            shortcut.IconLocation = f"{icon_path},0"
        
        shortcut.save()
        print(f"Start menu shortcut created: {shortcut_path}")
        return True
        
    except Exception as e:
        print(f"Failed to create start menu shortcut: {e}")
        return False
    finally:
        try:
            pythoncom.CoUninitialize()
        except:
            pass


def create_shortcut_batch(target_path: str, shortcut_name: str, icon_path: str = None,
                         description: str = "", working_dir: str = None):
    """Create a batch file shortcut (alternative to .lnk files)."""
    try:
        desktop = Path(os.path.expanduser("~")) / "Desktop"
        batch_path = desktop / f"{shortcut_name}.bat"
        
        working_dir = working_dir or str(Path(target_path).parent)
        
        batch_content = f"""@echo off
cd /d "{working_dir}"
start "" "{target_path}"
"""
        
        with open(batch_path, 'w') as f:
            f.write(batch_content)
        
        print(f"Batch shortcut created: {batch_path}")
        return True
        
    except Exception as e:
        print(f"Failed to create batch shortcut: {e}")
        return False


def remove_desktop_shortcut(shortcut_name: str):
    """Remove desktop shortcut."""
    try:
        desktop = Path(os.path.expanduser("~")) / "Desktop"
        shortcut_path = desktop / f"{shortcut_name}.lnk"
        
        if shortcut_path.exists():
            shortcut_path.unlink()
            print(f"Desktop shortcut removed: {shortcut_path}")
            return True
        
        # Also check for batch file
        batch_path = desktop / f"{shortcut_name}.bat"
        if batch_path.exists():
            batch_path.unlink()
            print(f"Desktop batch shortcut removed: {batch_path}")
            return True
            
        return False
        
    except Exception as e:
        print(f"Failed to remove desktop shortcut: {e}")
        return False


def remove_startmenu_shortcut(shortcut_name: str, folder: str = None):
    """Remove start menu shortcut."""
    try:
        start_menu = Path(os.path.expandvars("%APPDATA%")) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
        
        if folder:
            start_menu = start_menu / folder
            
        shortcut_path = start_menu / f"{shortcut_name}.lnk"
        
        if shortcut_path.exists():
            shortcut_path.unlink()
            print(f"Start menu shortcut removed: {shortcut_path}")
            
            # Remove empty folder if it exists
            if folder and start_menu.exists() and not any(start_menu.iterdir()):
                start_menu.rmdir()
                print(f"Empty start menu folder removed: {start_menu}")
            
            return True
            
        return False
        
    except Exception as e:
        print(f"Failed to remove start menu shortcut: {e}")
        return False


def create_url_shortcut(url: str, shortcut_name: str, location: str = "desktop"):
    """Create a URL shortcut (.url file)."""
    try:
        if location.lower() == "desktop":
            base_path = Path(os.path.expanduser("~")) / "Desktop"
        elif location.lower() == "startmenu":
            base_path = Path(os.path.expandvars("%APPDATA%")) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
        else:
            base_path = Path(location)
            
        shortcut_path = base_path / f"{shortcut_name}.url"
        
        url_content = f"""[InternetShortcut]
URL={url}
"""
        
        with open(shortcut_path, 'w') as f:
            f.write(url_content)
        
        print(f"URL shortcut created: {shortcut_path}")
        return True
        
    except Exception as e:
        print(f"Failed to create URL shortcut: {e}")
        return False


def get_shortcut_target(shortcut_path: str):
    """Get the target path of an existing shortcut."""
    try:
        pythoncom.CoInitialize()
        
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        return shortcut.TargetPath
        
    except Exception as e:
        print(f"Failed to get shortcut target: {e}")
        return None
    finally:
        try:
            pythoncom.CoUninitialize()
        except:
            pass


def list_desktop_shortcuts():
    """List all shortcuts on desktop."""
    try:
        desktop = Path(os.path.expanduser("~")) / "Desktop"
        shortcuts = []
        
        for item in desktop.iterdir():
            if item.suffix.lower() in ['.lnk', '.url', '.bat']:
                shortcuts.append(str(item))
                
        return shortcuts
        
    except Exception as e:
        print(f"Failed to list desktop shortcuts: {e}")
        return []


def create_shortcuts_for_app(app_name: str, target_path: str, icon_path: str = None,
                           desktop: bool = True, startmenu: bool = True, 
                           startmenu_folder: str = None):
    """
    Create shortcuts for an application in multiple locations.
    
    Args:
        app_name: Name of the application
        target_path: Path to the executable
        icon_path: Path to icon file
        desktop: Create desktop shortcut
        startmenu: Create start menu shortcut
        startmenu_folder: Subfolder in start menu (optional)
    
    Returns:
        dict: Results of shortcut creation attempts
    """
    results = {}
    
    if desktop:
        results['desktop'] = create_desktop_shortcut(
            target_path, app_name, icon_path, f"{app_name} Application"
        )
    
    if startmenu:
        results['startmenu'] = create_startmenu_shortcut(
            target_path, app_name, icon_path, f"{app_name} Application", 
            folder=startmenu_folder
        )
    
    return results


def remove_shortcuts_for_app(app_name: str, startmenu_folder: str = None):
    """
    Remove shortcuts for an application from multiple locations.
    
    Args:
        app_name: Name of the application
        startmenu_folder: Subfolder in start menu (optional)
    
    Returns:
        dict: Results of shortcut removal attempts
    """
    results = {}
    
    results['desktop'] = remove_desktop_shortcut(app_name)
    results['startmenu'] = remove_startmenu_shortcut(app_name, startmenu_folder)
    
    return results