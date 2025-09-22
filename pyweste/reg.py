"""
Windows Registry operations for pyweste installer
"""

import winreg
import os
from pathlib import Path
from .copy import is_admin


def add_to_programs_and_features(app_name: str, install_path: str, uninstall_command: str, 
                                version: str = "1.0.0", publisher: str = "", icon_path: str = "",
                                use_current_user: bool = False):
    """
    Add application to Add/Remove Programs (Programs and Features).
    
    Args:
        app_name: Display name of the application
        install_path: Installation directory path  
        uninstall_command: Command to uninstall the application
        version: Application version
        publisher: Publisher/company name
        icon_path: Path to application icon
        use_current_user: Use HKEY_CURRENT_USER instead of HKEY_LOCAL_MACHINE
    """
    try:
        # Choose registry hive based on admin privileges and preference
        if use_current_user or not is_admin():
            hive = winreg.HKEY_CURRENT_USER
            print("Adding to Programs and Features (Current User)")
        else:
            hive = winreg.HKEY_LOCAL_MACHINE
            print("Adding to Programs and Features (All Users)")
            
        # Registry key for uninstall information
        key_path = f"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{app_name}"
        
        with winreg.CreateKeyEx(hive, key_path) as key:
            # Required values
            winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, app_name)
            winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, uninstall_command)
            winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, install_path)
            winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, version)
            
            # Optional values
            if publisher:
                winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, publisher)
            if icon_path and os.path.exists(icon_path):
                winreg.SetValueEx(key, "DisplayIcon", 0, winreg.REG_SZ, icon_path)
                
            # Additional useful values
            winreg.SetValueEx(key, "NoModify", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, "NoRepair", 0, winreg.REG_DWORD, 1)
            
            # Try to get installation size
            try:
                size = sum(f.stat().st_size for f in Path(install_path).rglob('*') if f.is_file())
                size_kb = size // 1024
                winreg.SetValueEx(key, "EstimatedSize", 0, winreg.REG_DWORD, size_kb)
            except:
                pass
                
        print(f"Added '{app_name}' to Programs and Features")
        return True
        
    except Exception as e:
        print(f"Failed to add to Programs and Features: {e}")
        return False


def remove_from_programs_and_features(app_name: str, use_current_user: bool = False):
    """
    Remove application from Programs and Features.
    
    Args:
        app_name: Name of the application to remove
        use_current_user: Remove from HKEY_CURRENT_USER instead of HKEY_LOCAL_MACHINE
    """
    try:
        # Choose registry hive
        if use_current_user or not is_admin():
            hive = winreg.HKEY_CURRENT_USER
            print("Removing from Programs and Features (Current User)")
        else:
            hive = winreg.HKEY_LOCAL_MACHINE  
            print("Removing from Programs and Features (All Users)")
            
        key_path = f"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{app_name}"
        winreg.DeleteKey(hive, key_path)
        print(f"Removed '{app_name}' from Programs and Features")
        return True
        
    except Exception as e:
        print(f"Failed to remove from Programs and Features: {e}")
        return False


def add_to_startup(app_name: str, executable_path: str, use_current_user: bool = True):
    """
    Add application to Windows startup.
    
    Args:
        app_name: Name for the startup entry
        executable_path: Path to the executable
        use_current_user: Add to current user's startup (recommended)
    """
    try:
        if use_current_user:
            hive = winreg.HKEY_CURRENT_USER
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
            print("Adding to startup (Current User)")
        else:
            hive = winreg.HKEY_LOCAL_MACHINE
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
            print("Adding to startup (All Users)")
        
        with winreg.OpenKey(hive, key_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, executable_path)
        
        print(f"Added '{app_name}' to startup")
        return True
        
    except Exception as e:
        print(f"Failed to add to startup: {e}")
        return False


def remove_from_startup(app_name: str, use_current_user: bool = True):
    """
    Remove application from Windows startup.
    
    Args:
        app_name: Name of the startup entry
        use_current_user: Remove from current user's startup
    """
    try:
        if use_current_user:
            hive = winreg.HKEY_CURRENT_USER
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
            print("Removing from startup (Current User)")
        else:
            hive = winreg.HKEY_LOCAL_MACHINE
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
            print("Removing from startup (All Users)")
        
        with winreg.OpenKey(hive, key_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, app_name)
        
        print(f"Removed '{app_name}' from startup")
        return True
        
    except Exception as e:
        print(f"Failed to remove from startup: {e}")
        return False


def create_file_association(extension: str, app_name: str, executable_path: str, 
                          icon_path: str = None, description: str = None):
    """
    Create file type association for the application.
    
    Args:
        extension: File extension (e.g., '.myapp')
        app_name: Application identifier
        executable_path: Path to executable that handles the files
        icon_path: Path to icon for the file type
        description: Description of the file type
    """
    try:
        # Ensure extension starts with dot
        if not extension.startswith('.'):
            extension = '.' + extension
            
        prog_id = f"{app_name}.Document"
        
        # Create extension key
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, f"SOFTWARE\\Classes\\{extension}") as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, prog_id)
        
        # Create ProgID key
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, f"SOFTWARE\\Classes\\{prog_id}") as key:
            if description:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, description)
        
        # Create DefaultIcon key
        if icon_path and os.path.exists(icon_path):
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, f"SOFTWARE\\Classes\\{prog_id}\\DefaultIcon") as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, f"{icon_path},0")
        
        # Create shell\open\command key
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, f"SOFTWARE\\Classes\\{prog_id}\\shell\\open\\command") as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, f'"{executable_path}" "%1"')
        
        print(f"Created file association for {extension} -> {app_name}")
        return True
        
    except Exception as e:
        print(f"Failed to create file association: {e}")
        return False


def remove_file_association(extension: str, app_name: str):
    """
    Remove file type association.
    
    Args:
        extension: File extension to remove
        app_name: Application identifier
    """
    try:
        # Ensure extension starts with dot
        if not extension.startswith('.'):
            extension = '.' + extension
            
        prog_id = f"{app_name}.Document"
        
        # Remove extension key
        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, f"SOFTWARE\\Classes\\{extension}")
        except:
            pass
            
        # Remove ProgID and its subkeys
        try:
            # Delete subkeys first
            for subkey in ["shell\\open\\command", "shell\\open", "shell", "DefaultIcon"]:
                try:
                    winreg.DeleteKey(winreg.HKEY_CURRENT_USER, f"SOFTWARE\\Classes\\{prog_id}\\{subkey}")
                except:
                    pass
            
            # Delete main ProgID key
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, f"SOFTWARE\\Classes\\{prog_id}")
        except:
            pass
        
        print(f"Removed file association for {extension}")
        return True
        
    except Exception as e:
        print(f"Failed to remove file association: {e}")
        return False


def add_to_path(directory: str, use_current_user: bool = True):
    """
    Add directory to system PATH environment variable.
    
    Args:
        directory: Directory to add to PATH
        use_current_user: Add to current user's PATH instead of system PATH
    """
    try:
        if use_current_user:
            hive = winreg.HKEY_CURRENT_USER
            key_path = "Environment"
            print("Adding to PATH (Current User)")
        else:
            hive = winreg.HKEY_LOCAL_MACHINE
            key_path = r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
            print("Adding to PATH (System)")
        
        with winreg.OpenKey(hive, key_path, 0, winreg.KEY_READ | winreg.KEY_WRITE) as key:
            try:
                current_path, _ = winreg.QueryValueEx(key, "PATH")
            except FileNotFoundError:
                current_path = ""
            
            # Check if directory is already in PATH
            if directory.lower() in current_path.lower():
                print(f"Directory already in PATH: {directory}")
                return True
            
            # Add directory to PATH
            if current_path and not current_path.endswith(';'):
                current_path += ';'
            new_path = current_path + directory
            
            winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
        
        print(f"Added to PATH: {directory}")
        return True
        
    except Exception as e:
        print(f"Failed to add to PATH: {e}")
        return False


def remove_from_path(directory: str, use_current_user: bool = True):
    """
    Remove directory from system PATH environment variable.
    
    Args:
        directory: Directory to remove from PATH
        use_current_user: Remove from current user's PATH instead of system PATH
    """
    try:
        if use_current_user:
            hive = winreg.HKEY_CURRENT_USER
            key_path = "Environment"
            print("Removing from PATH (Current User)")
        else:
            hive = winreg.HKEY_LOCAL_MACHINE
            key_path = r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
            print("Removing from PATH (System)")
        
        with winreg.OpenKey(hive, key_path, 0, winreg.KEY_READ | winreg.KEY_WRITE) as key:
            try:
                current_path, _ = winreg.QueryValueEx(key, "PATH")
            except FileNotFoundError:
                print("PATH variable not found")
                return False
            
            # Remove directory from PATH
            path_parts = current_path.split(';')
            new_parts = [part for part in path_parts if part.lower() != directory.lower()]
            new_path = ';'.join(new_parts)
            
            winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
        
        print(f"Removed from PATH: {directory}")
        return True
        
    except Exception as e:
        print(f"Failed to remove from PATH: {e}")
        return False


def get_registry_value(hive, key_path: str, value_name: str):
    """Get a registry value."""
    try:
        with winreg.OpenKey(hive, key_path, 0, winreg.KEY_READ) as key:
            value, reg_type = winreg.QueryValueEx(key, value_name)
            return value
    except Exception as e:
        print(f"Failed to get registry value: {e}")
        return None


def set_registry_value(hive, key_path: str, value_name: str, value, reg_type=winreg.REG_SZ):
    """Set a registry value."""
    try:
        with winreg.CreateKey(hive, key_path) as key:
            winreg.SetValueEx(key, value_name, 0, reg_type, value)
        return True
    except Exception as e:
        print(f"Failed to set registry value: {e}")
        return False