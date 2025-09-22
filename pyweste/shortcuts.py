import os
from pathlib import Path
import win32com.client
import pythoncom
from .utils import log_info, log_error, get_desktop, get_startmenu

def create_shortcut(target_path: str, shortcut_path: str, icon_path: str = None, 
                   description: str = "", working_dir: str = None) -> bool:
    """Create a Windows shortcut (.lnk file)."""
    try:
        pythoncom.CoInitialize()
        
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.TargetPath = target_path
        shortcut.WorkingDirectory = working_dir or str(Path(target_path).parent)
        shortcut.Description = description
        
        if icon_path and os.path.exists(icon_path):
            shortcut.IconLocation = f"{icon_path},0"
        
        shortcut.save()
        log_info(f"Shortcut created: {shortcut_path}")
        return True
        
    except Exception as e:
        log_error(f"Failed to create shortcut: {e}")
        return False
    finally:
        try:
            pythoncom.CoUninitialize()
        except:
            pass

def remove_shortcut(shortcut_path: str) -> bool:
    """Remove a shortcut file."""
    try:
        path_obj = Path(shortcut_path)
        if path_obj.exists():
            path_obj.unlink()
            log_info(f"Shortcut removed: {shortcut_path}")
            return True
        return False
    except Exception as e:
        log_error(f"Failed to remove shortcut: {e}")
        return False

def create_desktop_shortcut(target_path: str, shortcut_name: str, icon_path: str = None, 
                          description: str = "", working_dir: str = None) -> bool:
    """Create a desktop shortcut."""
    desktop = Path(get_desktop())
    shortcut_path = desktop / f"{shortcut_name}.lnk"
    return create_shortcut(target_path, str(shortcut_path), icon_path, description, working_dir)

def create_startmenu_shortcut(target_path: str, shortcut_name: str, icon_path: str = None, 
                            description: str = "", working_dir: str = None, folder: str = None) -> bool:
    """Create a start menu shortcut."""
    start_menu = Path(get_startmenu())
    if folder:
        start_menu = start_menu / folder
        start_menu.mkdir(parents=True, exist_ok=True)
    
    shortcut_path = start_menu / f"{shortcut_name}.lnk"
    return create_shortcut(target_path, str(shortcut_path), icon_path, description, working_dir)

def create_all_shortcuts(app_name: str, target_path: str, icon_path: str = None,
                        desktop: bool = True, startmenu: bool = True, 
                        startmenu_folder: str = None) -> dict:
    """Create shortcuts for an application in multiple locations."""
    results = {}
    description = f"{app_name} Application"
    
    if desktop:
        results['desktop'] = create_desktop_shortcut(target_path, app_name, icon_path, description)
    
    if startmenu:
        results['startmenu'] = create_startmenu_shortcut(target_path, app_name, icon_path, description, folder=startmenu_folder)
    
    return results

def remove_all_shortcuts(app_name: str, startmenu_folder: str = None) -> dict:
    """Remove shortcuts for an application from multiple locations."""
    results = {}
    
    # Remove desktop shortcut
    desktop_path = Path(get_desktop()) / f"{app_name}.lnk"
    results['desktop'] = remove_shortcut(str(desktop_path))
    
    # Remove start menu shortcut
    start_menu = Path(get_startmenu())
    if startmenu_folder:
        start_menu = start_menu / startmenu_folder
    startmenu_path = start_menu / f"{app_name}.lnk"
    results['startmenu'] = remove_shortcut(str(startmenu_path))
    
    # Remove empty start menu folder if it exists
    if startmenu_folder and start_menu.exists() and not any(start_menu.iterdir()):
        try:
            start_menu.rmdir()
            log_info(f"Empty start menu folder removed: {start_menu}")
        except:
            pass
    
    return results