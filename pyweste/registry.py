"""
PyWeste registry module.
Handles Windows registry operations and uninstaller creation.
"""

import os
import winreg
from pathlib import Path
from .files import calculate_directory_size


def create_uninstaller_script(app_name: str, install_path: str) -> str:
    """
    Create an uninstallation script that requests admin privileges.
    
    Args:
        app_name: Name of the application
        install_path: Installation directory path
        
    Returns:
        str: Path to the created uninstaller script
    """
    install_path = Path(install_path)
    uninstall_script_path = install_path / "uninstall.bat"
    
    uninstall_content = f'''@echo off
:: Check for admin privileges
net session >nul 2>&1
if %errorLevel% == 0 (
    goto :admin
) else (
    echo Requesting administrator privileges...
    powershell -Command "Start-Process cmd -ArgumentList '/c \"%~f0\"' -Verb RunAs"
    exit /b
)

:admin
echo Uninstalling {app_name}...

:: Remove desktop shortcut
echo Removing desktop shortcut...
del "%USERPROFILE%\\Desktop\\{app_name}.lnk" 2>nul

:: Remove start menu shortcuts
echo Removing start menu shortcuts...
del "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\{app_name}.lnk" 2>nul
for /d %%i in ("%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\*") do (
    del "%%i\\{app_name}.lnk" 2>nul
)

:: Remove from registry (Add/Remove Programs)
echo Removing registry entries...
reg delete "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{app_name}" /f 2>nul
reg delete "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{app_name}" /f 2>nul

:: Remove installation directory
echo Removing installation files...
cd /d "{install_path.parent}"
rmdir /s /q "{install_path.name}" 2>nul

echo.
echo {app_name} has been uninstalled successfully.
echo Press any key to close this window...
pause >nul
'''
    
    try:
        with open(uninstall_script_path, 'w') as f:
            f.write(uninstall_content)
        print(f"INFO: Uninstaller created: {uninstall_script_path}")
        return str(uninstall_script_path)
    except Exception as e:
        print(f"ERROR: Failed to create uninstaller: {e}")
        return None


def add_registry_entry_hkcu(app_name: str, install_path: str, uninstall_script_path: str,
                           publisher: str, icon_path: str = None, main_executable: str = None) -> bool:
    """Add registry entry to HKEY_CURRENT_USER (no admin required)."""
    try:
        # Calculate installation size
        total_size = calculate_directory_size(install_path)
        size_kb = total_size // 1024 if total_size > 0 else 1024
        
        registry_path = f"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{app_name}"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, registry_path) as key:
            winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, app_name)
            winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, publisher)
            winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, str(install_path))
            winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, str(uninstall_script_path))
            winreg.SetValueEx(key, "EstimatedSize", 0, winreg.REG_DWORD, size_kb)
            
            if icon_path and os.path.exists(icon_path):
                winreg.SetValueEx(key, "DisplayIcon", 0, winreg.REG_SZ, icon_path)
            elif main_executable:
                exe_path = Path(install_path) / main_executable
                if exe_path.exists():
                    winreg.SetValueEx(key, "DisplayIcon", 0, winreg.REG_SZ, str(exe_path))
            
            winreg.SetValueEx(key, "NoModify", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, "NoRepair", 0, winreg.REG_DWORD, 1)
        
        print(f"INFO: Registry entry created for {app_name} in HKCU")
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to add HKCU registry entry: {e}")
        return False


def add_registry_entry_hklm(app_name: str, install_path: str, uninstall_script_path: str,
                           publisher: str, icon_path: str = None, main_executable: str = None) -> bool:
    """Add registry entry to HKEY_LOCAL_MACHINE (requires admin)."""
    try:
        # Calculate installation size
        total_size = calculate_directory_size(install_path)
        size_kb = total_size // 1024 if total_size > 0 else 1024
        
        registry_path = f"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{app_name}"
        with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, registry_path) as key:
            winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, app_name)
            winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, publisher)
            winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, str(install_path))
            winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, str(uninstall_script_path))
            winreg.SetValueEx(key, "EstimatedSize", 0, winreg.REG_DWORD, size_kb)
            
            if icon_path and os.path.exists(icon_path):
                winreg.SetValueEx(key, "DisplayIcon", 0, winreg.REG_SZ, icon_path)
            elif main_executable:
                exe_path = Path(install_path) / main_executable
                if exe_path.exists():
                    winreg.SetValueEx(key, "DisplayIcon", 0, winreg.REG_SZ, str(exe_path))
            
            winreg.SetValueEx(key, "NoModify", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, "NoRepair", 0, winreg.REG_DWORD, 1)
        
        print(f"INFO: Registry entry created for {app_name} in HKLM")
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to add HKLM registry entry: {e}")
        return False


def add_to_registry(app_name: str, install_path: str, main_executable: str = None, 
                   icon_path: str = None, publisher: str = "Unknown") -> bool:
    """
    Add application to Windows registry (Add/Remove Programs) and create uninstaller.
    
    Args:
        app_name: Name of the application
        install_path: Installation directory path
        main_executable: Optional main executable path
        icon_path: Optional path to icon file
        publisher: Application publisher
        
    Returns:
        bool: True if registry entry created successfully, False otherwise
        
    Example:
        add_to_registry("MyApp", "C:/Program Files/MyApp", "myapp.exe", publisher="My Company")
    """
    # Create uninstaller script first
    uninstall_script_path = create_uninstaller_script(app_name, install_path)
    if not uninstall_script_path:
        return False
    
    # Try to add to HKEY_CURRENT_USER first (no admin required)
    if add_registry_entry_hkcu(app_name, install_path, uninstall_script_path, 
                              publisher, icon_path, main_executable):
        return True
    
    print("WARNING: Failed to add to HKCU registry, trying HKLM...")
    
    # Try HKEY_LOCAL_MACHINE (requires admin)
    return add_registry_entry_hklm(app_name, install_path, uninstall_script_path,
                                  publisher, icon_path, main_executable)


def remove_registry_entry(app_name: str) -> bool:
    """Remove application from Windows registry."""
    success = False
    
    # Try to remove from HKCU first
    try:
        registry_path = f"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{app_name}"
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, registry_path)
        print(f"INFO: Removed registry entry from HKCU: {app_name}")
        success = True
    except Exception as e:
        print(f"WARNING: Failed to remove HKCU registry entry: {e}")
    
    # Try to remove from HKLM
    try:
        registry_path = f"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{app_name}"
        winreg.DeleteKey(winreg.HKEY_LOCAL_MACHINE, registry_path)
        print(f"INFO: Removed registry entry from HKLM: {app_name}")
        success = True
    except Exception as e:
        print(f"WARNING: Failed to remove HKLM registry entry: {e}")
    
    return success