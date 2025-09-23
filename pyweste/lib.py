"""
PyWeste core functions for Windows application installation.

Functions:
- copy_program: Copy files to installation directory
- desktop_shortcut: Create desktop shortcuts
- startmenu_shortcut: Create start menu shortcuts
- uninstall_script: Create uninstaller with admin elevation
"""

import os
import shutil
import win32com.client
import pythoncom
from pathlib import Path
from typing import List, Tuple, Optional


def copy_program(source_files: List[Tuple[str, str]], install_path: str) -> bool:
    """
    Copy files to installation directory.
    
    Args:
        source_files: List of tuples (source_path, relative_destination_path)
        install_path: Target installation directory
        
    Returns:
        bool: True if all files copied successfully, False otherwise
        
    Example:
        source_files = [
            ("C:/temp/myapp.exe", "myapp.exe"),
            ("C:/temp/data/config.ini", "config/config.ini")
        ]
        copy_program(source_files, "C:/Program Files/MyApp")
    """
    if not source_files:
        print("ERROR: No source files provided")
        return False
        
    install_path = Path(install_path)
    
    try:
        install_path.mkdir(parents=True, exist_ok=True)
        print(f"INFO: Created installation directory: {install_path}")
        
        for src, rel_dest in source_files:
            if not Path(src).exists():
                print(f"ERROR: Source file not found: {src}")
                return False
                
            dest = install_path / rel_dest
            dest.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(src, dest)
            print(f"INFO: Copied: {src} -> {dest}")
        
        print("INFO: All files copied successfully")
        return True
        
    except Exception as e:
        print(f"ERROR: File copy operation failed: {e}")
        return False


def desktop_shortcut(target_path: str, shortcut_name: str, icon_path: str = None) -> bool:
    """
    Create a desktop shortcut.
    
    Args:
        target_path: Path to the executable to launch
        shortcut_name: Name for the shortcut (without .lnk extension)
        icon_path: Optional path to icon file
        
    Returns:
        bool: True if shortcut created successfully, False otherwise
        
    Example:
        desktop_shortcut("C:/Program Files/MyApp/myapp.exe", "MyApp", "C:/Program Files/MyApp/icon.ico")
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


def startmenu_shortcut(target_path: str, shortcut_name: str, icon_path: str = None, folder: str = None) -> bool:
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
        startmenu_shortcut("C:/Program Files/MyApp/myapp.exe", "MyApp", folder="My Company")
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


def uninstall_script(app_name: str, install_path: str) -> bool:
    """
    Create an uninstallation script that requests admin privileges.
    
    Args:
        app_name: Name of the application
        install_path: Installation directory path
        
    Returns:
        bool: True if uninstaller created successfully, False otherwise
        
    Example:
        uninstall_script("MyApp", "C:/Program Files/MyApp")
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
        return True
    except Exception as e:
        print(f"ERROR: Failed to create uninstaller: {e}")
        return False


# If run directly, show usage
if __name__ == "__main__":
    print("PyWeste - Python Windows Installation Tools")
    print("==========================================")
    print("Available functions:")
    print("- copy_program(source_files, install_path)")
    print("- desktop_shortcut(target_path, shortcut_name, icon_path=None)")
    print("- startmenu_shortcut(target_path, shortcut_name, icon_path=None, folder=None)")
    print("- uninstall_script(app_name, install_path)")
    print("\nImport with: from pyweste import copy_program, desktop_shortcut, startmenu_shortcut, uninstall_script")