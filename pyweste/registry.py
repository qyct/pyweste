import winreg
import os
from pathlib import Path
from .utils import is_admin, log_error, log_info

def add_to_programs(app_name: str, install_path: str, uninstall_command: str, 
                   version: str = "1.0.0", publisher: str = "", icon_path: str = "",
                   use_current_user: bool = None) -> bool:
    """Add application to Add/Remove Programs."""
    if use_current_user is None:
        use_current_user = not is_admin()
    
    try:
        hive = winreg.HKEY_CURRENT_USER if use_current_user else winreg.HKEY_LOCAL_MACHINE
        scope = "Current User" if use_current_user else "All Users"
        log_info(f"Adding to Programs and Features ({scope})")
        
        key_path = f"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{app_name}"
        
        with winreg.CreateKeyEx(hive, key_path) as key:
            winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, app_name)
            winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, uninstall_command)
            winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, install_path)
            winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, version)
            winreg.SetValueEx(key, "NoModify", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, "NoRepair", 0, winreg.REG_DWORD, 1)
            
            if publisher:
                winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, publisher)
            if icon_path and os.path.exists(icon_path):
                winreg.SetValueEx(key, "DisplayIcon", 0, winreg.REG_SZ, icon_path)
            
            try:
                size = sum(f.stat().st_size for f in Path(install_path).rglob('*') if f.is_file())
                size_kb = size // 1024
                winreg.SetValueEx(key, "EstimatedSize", 0, winreg.REG_DWORD, size_kb)
            except:
                pass
                
        log_info(f"Added '{app_name}' to Programs and Features")
        return True
        
    except Exception as e:
        log_error(f"Failed to add to Programs and Features: {e}")
        return False

def remove_from_programs(app_name: str, use_current_user: bool = None) -> bool:
    """Remove application from Programs and Features."""
    if use_current_user is None:
        use_current_user = not is_admin()
    
    try:
        hive = winreg.HKEY_CURRENT_USER if use_current_user else winreg.HKEY_LOCAL_MACHINE
        scope = "Current User" if use_current_user else "All Users"
        log_info(f"Removing from Programs and Features ({scope})")
        
        key_path = f"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{app_name}"
        winreg.DeleteKey(hive, key_path)
        log_info(f"Removed '{app_name}' from Programs and Features")
        return True
        
    except Exception as e:
        log_error(f"Failed to remove from Programs and Features: {e}")
        return False

def add_to_startup(app_name: str, executable_path: str, use_current_user: bool = True) -> bool:
    """Add application to Windows startup."""
    try:
        hive = winreg.HKEY_CURRENT_USER if use_current_user else winreg.HKEY_LOCAL_MACHINE
        key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
        scope = "Current User" if use_current_user else "All Users"
        log_info(f"Adding to startup ({scope})")
        
        with winreg.OpenKey(hive, key_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, executable_path)
        
        log_info(f"Added '{app_name}' to startup")
        return True
        
    except Exception as e:
        log_error(f"Failed to add to startup: {e}")
        return False

def remove_from_startup(app_name: str, use_current_user: bool = True) -> bool:
    """Remove application from Windows startup."""
    try:
        hive = winreg.HKEY_CURRENT_USER if use_current_user else winreg.HKEY_LOCAL_MACHINE
        key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
        scope = "Current User" if use_current_user else "All Users"
        log_info(f"Removing from startup ({scope})")
        
        with winreg.OpenKey(hive, key_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, app_name)
        
        log_info(f"Removed '{app_name}' from startup")
        return True
        
    except Exception as e:
        log_error(f"Failed to remove from startup: {e}")
        return False

def create_file_association(extension: str, app_name: str, executable_path: str, 
                          icon_path: str = None, description: str = None) -> bool:
    """Create file type association for the application."""
    try:
        if not extension.startswith('.'):
            extension = '.' + extension
            
        prog_id = f"{app_name}.Document"
        
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, f"SOFTWARE\\Classes\\{extension}") as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, prog_id)
        
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, f"SOFTWARE\\Classes\\{prog_id}") as key:
            if description:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, description)
        
        if icon_path and os.path.exists(icon_path):
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, f"SOFTWARE\\Classes\\{prog_id}\\DefaultIcon") as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, f"{icon_path},0")
        
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, f"SOFTWARE\\Classes\\{prog_id}\\shell\\open\\command") as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, f'"{executable_path}" "%1"')
        
        log_info(f"Created file association for {extension} -> {app_name}")
        return True
        
    except Exception as e:
        log_error(f"Failed to create file association: {e}")
        return False

def add_to_path(directory: str, use_current_user: bool = True) -> bool:
    """Add directory to system PATH environment variable."""
    try:
        hive = winreg.HKEY_CURRENT_USER if use_current_user else winreg.HKEY_LOCAL_MACHINE
        key_path = "Environment" if use_current_user else r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
        scope = "Current User" if use_current_user else "System"
        log_info(f"Adding to PATH ({scope})")
        
        with winreg.OpenKey(hive, key_path, 0, winreg.KEY_READ | winreg.KEY_WRITE) as key:
            try:
                current_path, _ = winreg.QueryValueEx(key, "PATH")
            except FileNotFoundError:
                current_path = ""
            
            if directory.lower() in current_path.lower():
                log_info(f"Directory already in PATH: {directory}")
                return True
            
            if current_path and not current_path.endswith(';'):
                current_path += ';'
            new_path = current_path + directory
            
            winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
        
        log_info(f"Added to PATH: {directory}")
        return True
        
    except Exception as e:
        log_error(f"Failed to add to PATH: {e}")
        return False